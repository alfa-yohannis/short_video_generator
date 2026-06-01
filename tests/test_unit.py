"""Unit tests for the pure helpers in video_generator/generate_video.py.

These cover the storyboard parser, voice/key resolution, timestamp + estimated
SRT math, the Pango ampersand-escape pass, the AST syntax guard, prompt
construction, the TTS dispatch, and the Gemini HTTP response parsing (urlopen
mocked). No external tools or network needed.
"""

from __future__ import annotations

import io
import json
from argparse import Namespace

import pytest

from conftest import storyboard_text, write_storyboard


# --- name helpers ----------------------------------------------------------


def test_camel_from_snake(g):
    assert g._camel_from_snake("strategy_pattern") == "StrategyPattern"
    assert g._camel_from_snake("pengantar") == "Pengantar"
    assert g._camel_from_snake("a-b c") == "ABC"


def test_strip_leading_digits(g):
    assert g._strip_leading_digits("01_pengantar") == "pengantar"
    assert g._strip_leading_digits("12-intro") == "intro"
    assert g._strip_leading_digits("plain") == "plain"


# --- scene parsing ---------------------------------------------------------


def test_parse_scene_header_basename_and_class(g):
    sc = g.parse_scene("01_pengantar / Pengantar", "### description\nHi.\n")
    assert sc.basename == "01_pengantar"
    assert sc.classname == "Pengantar"
    assert sc.description == "Hi."


def test_parse_scene_class_meta_overrides_header(g):
    sc = g.parse_scene("01_x / FromHeader", "**class:** FromMeta\n")
    assert sc.classname == "FromMeta"


def test_parse_scene_classname_derived_when_absent(g):
    sc = g.parse_scene("03_segitiga_siku", "")
    assert sc.classname == "SegitigaSiku"  # camel-cased, digits stripped


def test_parse_scene_file_and_duration(g):
    sc = g.parse_scene("01_x / X", "**file:** scene_x.py\n**fallback_duration:** 14\n")
    assert sc.file == "scene_x.py"
    assert sc.fallback_duration == 14.0


def test_parse_scene_defaults_file_and_duration(g):
    sc = g.parse_scene("01_x / X", "### description\nno meta here\n")
    assert sc.file == "scene_01_x.py"
    assert sc.fallback_duration == 15.0


def test_parse_scene_narration_and_extras(g):
    body = (
        "**file:** s.py\n"
        "### description\nA card.\n"
        "### narration.id\nHalo.\n"
        "### narration.en\nHello.\n"
        "### notes\nremember this\n"
    )
    sc = g.parse_scene("01_x / X", body)
    assert sc.description == "A card."
    assert sc.narration == {"id": "Halo.", "en": "Hello."}
    assert sc.extras["notes"] == "remember this"
    # metadata lines must not bleed into the description
    assert "**file:**" not in sc.description


# --- storyboard parsing ----------------------------------------------------


def test_parse_storyboard_full(g, tmp_path):
    p = write_storyboard(
        tmp_path / "sb.md",
        title="pythagorean",
        voices={"id": "id-ID-ArdiNeural", "en": "en-US-GuyNeural"},
        tts_provider="gemini",
        gemini_model="gemini-2.5-flash-preview-tts",
        gemini_api_key="from-front-matter",
        scenes=[
            {"basename": "01_a", "classname": "A", "narration": {"id": "x", "en": "y"}},
            {"basename": "02_b", "classname": "B", "narration": {"id": "p", "en": "q"}},
        ],
    )
    sb = g.parse_storyboard(p)
    assert sb.title == "pythagorean"
    assert sb.tts_provider == "gemini"
    assert sb.gemini_model == "gemini-2.5-flash-preview-tts"
    assert sb.gemini_api_key == "from-front-matter"
    assert sb.voices == {"id": "id-ID-ArdiNeural", "en": "en-US-GuyNeural"}
    assert [s.basename for s in sb.scenes] == ["01_a", "02_b"]
    assert sb.project_brief  # captured from the body before the first scene


def test_parse_storyboard_defaults(g, tmp_path):
    # Minimal front-matter: no tts_provider, ai_cli, gemini_*; defaults apply.
    text = (
        "---\n"
        "title: minimal\n"
        "---\n\n"
        "Brief.\n\n"
        "## Scene: 01_only / Only\n\n"
        "### description\nA scene.\n"
    )
    p = tmp_path / "min.md"
    p.write_text(text, encoding="utf-8")
    sb = g.parse_storyboard(p)
    assert sb.tts_provider == "edge"
    assert sb.ai_cli == "claude"
    assert sb.gemini_model == g.DEFAULT_GEMINI_MODEL
    assert sb.gemini_api_key is None
    assert sb.languages == ["id", "en"]
    assert sb.orientations == ["landscape", "portrait"]


def test_parse_storyboard_requires_front_matter(g, tmp_path):
    p = tmp_path / "no_fm.md"
    p.write_text("# just a heading\n\n## Scene: 01_x / X\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        g.parse_storyboard(p)


def test_parse_storyboard_requires_a_scene(g, tmp_path):
    p = tmp_path / "no_scene.md"
    p.write_text("---\ntitle: t\n---\n\nJust a brief, no scenes.\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        g.parse_storyboard(p)


def test_parse_storyboard_resolves_scene_dirs_relative(g, tmp_path):
    (tmp_path / "land").mkdir()
    p = write_storyboard(tmp_path / "sb.md", scenes_landscape_dir="land")
    sb = g.parse_storyboard(p)
    assert sb.scenes_landscape_dir == (tmp_path / "land").resolve()
    assert sb.scenes_portrait_dir is None


# --- voice resolution ------------------------------------------------------


def _sb(g, **kw):
    """A tiny in-memory Storyboard for resolver tests."""
    defaults = dict(
        title="t", languages=["id", "en"], orientations=["landscape"],
        voices={}, tts_provider="edge", gemini_model=g.DEFAULT_GEMINI_MODEL,
        gemini_api_key=None, ai_cli="claude", fps=30,
        resolution_landscape=(1920, 1080), scenes_landscape_dir=None,
        scenes_portrait_dir=None, scenes=[], project_brief="",
    )
    defaults.update(kw)
    return g.Storyboard(**defaults)


def test_resolve_voice_edge_from_map(g):
    sb = _sb(g, voices={"id": "id-ID-ArdiNeural", "en": "en-US-GuyNeural"})
    assert g._resolve_voice(sb, "en") == "en-US-GuyNeural"


def test_resolve_voice_edge_fallback_ardi(g):
    sb = _sb(g, voices={}, tts_provider="edge")
    assert g._resolve_voice(sb, "id") == g.DEFAULT_EDGE_VOICE == "id-ID-ArdiNeural"


def test_resolve_voice_gemini_fallback_iapetus(g):
    sb = _sb(g, voices={}, tts_provider="gemini")
    assert g._resolve_voice(sb, "id") == g.DEFAULT_GEMINI_VOICE == "Iapetus"


def test_resolve_voice_gemini_from_map(g):
    sb = _sb(g, voices={"id": "Charon"}, tts_provider="gemini")
    assert g._resolve_voice(sb, "id") == "Charon"


# --- Gemini key resolution -------------------------------------------------


def test_resolve_gemini_key_front_matter_wins(g, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "from-env")
    sb = _sb(g, gemini_api_key="from-front-matter")
    assert g._resolve_gemini_key(sb) == "from-front-matter"


def test_resolve_gemini_key_env(g, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "from-env")
    sb = _sb(g, gemini_api_key=None)
    assert g._resolve_gemini_key(sb) == "from-env"


def test_resolve_gemini_key_from_dotenv(g, monkeypatch, tmp_path):
    monkeypatch.setattr(g, "REPO_ROOT", tmp_path)
    (tmp_path / ".env").write_text(
        '# comment\nGEMINI_API_KEY="dotenv-secret"\nOTHER=1\n', encoding="utf-8"
    )
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    sb = _sb(g, gemini_api_key=None)
    assert g._resolve_gemini_key(sb) == "dotenv-secret"


def test_resolve_gemini_key_absent(g, monkeypatch, tmp_path):
    monkeypatch.setattr(g, "REPO_ROOT", tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    sb = _sb(g, gemini_api_key=None)
    assert g._resolve_gemini_key(sb) is None


# --- timestamps & estimated SRT --------------------------------------------


def test_fmt_ts_basic(g):
    assert g._fmt_ts(0) == "00:00:00,000"
    assert g._fmt_ts(1.25) == "00:00:01,250"
    assert g._fmt_ts(3661.5) == "01:01:01,500"


def test_fmt_ts_clamps_negative(g):
    assert g._fmt_ts(-5) == "00:00:00,000"


def test_fmt_ts_ms_rounding_carry(g):
    assert g._fmt_ts(0.9999) == "00:00:01,000"


def test_split_sentences(g):
    assert g._split_sentences("Halo dunia. Foo bar! Baz?") == [
        "Halo dunia.", "Foo bar!", "Baz?",
    ]


def test_split_sentences_empty(g):
    assert g._split_sentences("   ") == []


def test_write_estimated_srt(g, tmp_path):
    import srt as _srt

    out = tmp_path / "clip.srt"
    s1, s2 = "Kalimat satu.", "Kalimat dua lebih panjang."
    g._write_estimated_srt(f"{s1} {s2}", 10.0, out)
    cues = list(_srt.parse(out.read_text(encoding="utf-8")))
    assert len(cues) == 2
    assert cues[0].start.total_seconds() == pytest.approx(0.0)
    assert cues[-1].end.total_seconds() == pytest.approx(10.0)
    # boundary is proportional to sentence length
    expected = 10.0 * len(s1) / (len(s1) + len(s2))
    assert cues[0].end.total_seconds() == pytest.approx(expected, abs=0.05)
    assert cues[0].content == s1


def test_write_estimated_srt_empty(g, tmp_path):
    out = tmp_path / "clip.srt"
    g._write_estimated_srt("   ", 5.0, out)
    assert out.read_text() == ""


# --- Pango ampersand escape ------------------------------------------------


def test_escape_bare_ampersand_in_literal(g):
    assert g._escape_unsafe_ampersands('x = "Tom & Jerry"') == 'x = "Tom &amp; Jerry"'


def test_escape_leaves_known_entities(g):
    src = '"a &amp; b &lt; c &#39;d"'
    assert g._escape_unsafe_ampersands(src) == src


def test_escape_multiple_in_one_literal(g):
    assert g._escape_unsafe_ampersands("'A & B & C'") == "'A &amp; B &amp; C'"


def test_escape_ignores_ampersand_outside_strings(g):
    # A bitwise `&` in code (not inside a string literal) must be left alone.
    assert g._escape_unsafe_ampersands("flags = A & B") == "flags = A & B"


def test_escape_idempotent(g):
    once = g._escape_unsafe_ampersands('t("R&D")')
    assert once == 't("R&amp;D")'
    assert g._escape_unsafe_ampersands(once) == once


# --- code fence stripping --------------------------------------------------


def test_strip_code_fences_plain(g):
    assert g._strip_code_fences("from manim import *\n") == "from manim import *"


def test_strip_code_fences_fenced(g):
    text = "```python\nfrom manim import *\nx = 1\n```"
    assert g._strip_code_fences(text) == "from manim import *\nx = 1"


# --- AST validation --------------------------------------------------------


def test_validate_scene_source_ok(g, tmp_path):
    g._validate_scene_source(tmp_path / "s.py", "x = 1\ndef f():\n    return x\n")


def test_validate_scene_source_syntax_error(g, tmp_path):
    with pytest.raises(SystemExit) as ei:
        g._validate_scene_source(tmp_path / "s.py", "def f(:\n  pass\n")
    assert "not valid Python" in str(ei.value)


# --- prompts ---------------------------------------------------------------


def test_build_narration_prompt(g):
    sb = _sb(g, title="Pythagorean", project_brief="A brief about triangles.")
    sc = g.Scene(basename="01_x", classname="X", file="s.py", fallback_duration=20,
                 description="Title card.", narration={"en": "Hello there."})
    prompt = g.build_narration_prompt(sb, sc, "id")
    assert "Pythagorean" in prompt
    assert "Title card." in prompt
    assert "Indonesian" in prompt
    # the existing other-language narration is offered for meaning
    assert "Hello there." in prompt
    # word target = max(20, duration*2.5)
    assert str(int(20 * 2.5)) in prompt


def test_build_scene_prompt_includes_sources_and_narration(g):
    sb = _sb(g, title="T")
    sc = g.Scene(basename="01_x", classname="MyScene", file="s.py",
                 fallback_duration=10, description="desc",
                 narration={"id": "teks id", "en": "english text"})
    prompt = g._build_scene_prompt(sb, sc, "portrait", "SKELETON_MARK", "COMMON_MARK")
    assert "COMMON_MARK" in prompt and "SKELETON_MARK" in prompt
    assert "teks id" in prompt and "english text" in prompt
    assert "class MyScene(Scene)" in prompt
    # portrait gets the shorts-safe constraint
    assert "SHORTS_SAFE_BOTTOM" in prompt


# --- TTS dispatch ----------------------------------------------------------


def test_generate_audio_unknown_provider(g, tmp_path):
    sb = _sb(g, tts_provider="festival")
    with pytest.raises(SystemExit):
        g.generate_audio(sb, tmp_path, force=False)


def test_generate_audio_routes_edge(g, tmp_path, monkeypatch):
    seen = {}
    monkeypatch.setattr(g, "_generate_audio_edge", lambda sb, o, f: seen.setdefault("p", "edge"))
    monkeypatch.setattr(g, "_generate_audio_gemini", lambda sb, o, f: seen.setdefault("p", "gemini"))
    g.generate_audio(_sb(g, tts_provider="edge"), tmp_path, False)
    assert seen["p"] == "edge"


@pytest.mark.parametrize("provider", ["gemini", "google", "google_chirp", "chirp"])
def test_generate_audio_routes_gemini_and_aliases(g, tmp_path, monkeypatch, provider):
    seen = {}
    monkeypatch.setattr(g, "_generate_audio_edge", lambda sb, o, f: seen.setdefault("p", "edge"))
    monkeypatch.setattr(g, "_generate_audio_gemini", lambda sb, o, f: seen.setdefault("p", "gemini"))
    g.generate_audio(_sb(g, tts_provider=provider), tmp_path, False)
    assert seen["p"] == "gemini"


# --- _peek_ai_cli ----------------------------------------------------------


def test_peek_ai_cli_reads_front_matter(g, tmp_path):
    p = write_storyboard(tmp_path / "sb.md", ai_cli="codex")
    assert g._peek_ai_cli(p) == "codex"


def test_peek_ai_cli_missing_returns_none(g, tmp_path):
    p = tmp_path / "x.md"
    p.write_text("no front matter here", encoding="utf-8")
    assert g._peek_ai_cli(p) is None


# --- cmd_build CLI overrides -----------------------------------------------


def test_cmd_build_tts_and_voice_override(g, tmp_path, monkeypatch):
    """--tts / --voice override the storyboard and --voice applies to all langs."""
    p = write_storyboard(
        tmp_path / "sb.md",
        tts_provider="edge",
        voices={"id": "id-ID-ArdiNeural", "en": "en-US-GuyNeural"},
        scenes=[{"basename": "01_x", "classname": "X",
                 "narration": {"id": "halo", "en": "hi"}}],
    )
    captured = {}

    def fake_generate_audio(sb, output, force):
        captured["provider"] = sb.tts_provider
        captured["voices"] = dict(sb.voices)

    monkeypatch.setattr(g, "generate_audio", fake_generate_audio)
    monkeypatch.setattr(g, "ensure_narration", lambda sb, sc, lang, output=None: "x")

    args = Namespace(
        storyboard=str(p), output=str(tmp_path / "out"), stage="audio",
        only=None, force=False, ai_cli="claude", tts="gemini", voice="Charon",
        gemini_api_key="k", skip_dep_check=True, no_ai_cli_check=True,
    )
    g.cmd_build(args)
    assert captured["provider"] == "gemini"
    assert set(captured["voices"].values()) == {"Charon"}


# --- Gemini HTTP response parsing (mocked) ---------------------------------


class _FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_gemini_synth_parses_audio(g, monkeypatch):
    import base64

    pcm = b"\x01\x02\x03\x04"
    payload = {"candidates": [{"content": {"parts": [
        {"inlineData": {"mimeType": "audio/L16;codec=pcm;rate=24000",
                        "data": base64.b64encode(pcm).decode()}}
    ]}}]}
    monkeypatch.setattr(g.urllib.request, "urlopen",
                        lambda req, timeout=None: _FakeResp(json.dumps(payload).encode()))
    out_pcm, rate = g._gemini_synth("hi", "key", "model", "Iapetus", 30.0)
    assert out_pcm == pcm
    assert rate == 24000


def test_gemini_synth_http_error_becomes_runtimeerror(g, monkeypatch):
    def boom(req, timeout=None):
        raise g.urllib.error.HTTPError("url", 429, "Too Many Requests", {},
                                       io.BytesIO(b'{"error":"quota"}'))

    monkeypatch.setattr(g.urllib.request, "urlopen", boom)
    with pytest.raises(RuntimeError) as ei:
        g._gemini_synth("hi", "key", "model", "Iapetus", 30.0)
    assert "429" in str(ei.value)


def test_gemini_synth_no_audio_raises(g, monkeypatch):
    monkeypatch.setattr(g.urllib.request, "urlopen",
                        lambda req, timeout=None: _FakeResp(json.dumps({"candidates": []}).encode()))
    with pytest.raises(RuntimeError):
        g._gemini_synth("hi", "key", "model", "Iapetus", 30.0)
