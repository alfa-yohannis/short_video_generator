"""Unit tests for the pure helpers in video_generator/generate_video.py.

These cover the storyboard parser, voice/key resolution, timestamp + estimated
SRT math, the Pango ampersand-escape pass, the AST syntax guard, prompt
construction, the TTS dispatch, and the Gemini HTTP response parsing (urlopen
mocked). No external tools or network needed.
"""

from __future__ import annotations

import io
import json
import re
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


def test_strip_code_fences_drops_prose_preamble(g):
    # The failure mode that aborted a real build: a prose line before the code
    # (the "30s" makes ast choke on an invalid decimal literal).
    text = "Here is scene 6, the conclusion, about 30s long:\nfrom manim import *\nx = 1\n"
    assert g._strip_code_fences(text) == "from manim import *\nx = 1"


def test_strip_code_fences_prose_then_fence(g):
    text = "Sure! Here's the file:\n```python\nfrom manim import *\ny = 2\n```\nHope that helps."
    assert g._strip_code_fences(text) == "from manim import *\ny = 2"


def test_strip_code_fences_keeps_clean_source(g):
    src = "from manim import *\nfrom _common import title_text\n\nclass S(Scene):\n    pass"
    assert g._strip_code_fences(src) == src


def test_extract_layout_issues_from_layout_error(g):
    out = (
        "[layout] 1 issue(s) in RefactorSingleton:\n"
        "  - OVERFLOW: 'Same object!' extends past the frame\n"
        "LayoutError: [layout] 1 issue(s) in RefactorSingleton: "
        "OVERFLOW: 'Same object!' extends past the frame\n"
    )
    issues = g._extract_layout_issues(out)
    assert issues.startswith("[layout] 1 issue(s) in RefactorSingleton:")
    assert "OVERFLOW" in issues


def test_extract_layout_issues_falls_back_to_bullets(g):
    # warn-style output: bullets under a [layout] header, no LayoutError line.
    out = (
        "[layout] 2 issue(s) in S:\n"
        "  - OVERFLOW: 'A' extends past the frame\n"
        "  - OVERLAP: 'A' and 'B' overlap (80% of the smaller box)\n"
    )
    issues = g._extract_layout_issues(out)
    assert issues == ("OVERFLOW: 'A' extends past the frame; "
                      "OVERLAP: 'A' and 'B' overlap (80% of the smaller box)")


def test_extract_layout_issues_ignores_non_layout_failures(g):
    # A plain Manim/Python traceback is not a layout violation -> no repair.
    out = "Traceback (most recent call last):\n  File ...\nValueError: boom\n"
    assert g._extract_layout_issues(out) == ""


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


# --- YouTube metadata helpers ----------------------------------------------


def test_strip_emoji_hashtags_title(g):
    out = g._strip_emoji_hashtags("Belajar Pythagoras 🚀 #keren #math sekarang")
    assert "🚀" not in out
    assert "#keren" not in out and "#math" not in out
    assert "Belajar Pythagoras" in out and "sekarang" in out


def test_strip_emoji_hashtags_keeps_csharp_and_punctuation(g):
    out = g._strip_emoji_hashtags("Pemrograman C# — lanjutan… selesai")
    assert "C#" in out and "—" in out and "…" in out


def test_strip_emoji_keeps_hashtags(g):
    out = g._strip_emoji("Materi keren 🚀\n#Pythagoras #Mathematics")
    assert "🚀" not in out
    assert "#Pythagoras" in out and "#Mathematics" in out


def test_cap_hashtags_limits_to_15(g):
    tags = " ".join(f"#tag{i}" for i in range(20))
    out = g._cap_hashtags("Deskripsi. " + tags, max_tags=15)
    kept = re.findall(r"#\w+", out)
    assert len(kept) == 15
    assert kept[0] == "#tag0" and kept[-1] == "#tag14"


def test_cap_hashtags_keeps_all_when_under_limit(g):
    src = "Deskripsi. #a #b #c"
    assert g._cap_hashtags(src) == src


def test_clamp_word_boundary(g):
    out = g._clamp("satu dua tiga empat lima enam tujuh", 12)
    assert len(out) <= 12 and not out.endswith(" ")


def test_clamp_under_limit_unchanged(g):
    assert g._clamp("short", 100) == "short"


def test_clamp_keywords_total_and_intact(g):
    kw = ", ".join(f"tag{i:02d}" for i in range(200))
    out = g._clamp_keywords(kw, 500)
    assert len(out) <= 500
    assert all(t.strip().startswith("tag") for t in out.split(","))


def test_clamp_keywords_handles_newlines(g):
    assert g._clamp_keywords("a,\nb , c\n", 500) == "a, b, c"


def test_extract_json_variants(g):
    assert g._extract_json('{"title": "x"}')["title"] == "x"
    assert g._extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert g._extract_json('blah {"a": 2} blah') == {"a": 2}


def test_youtube_text_layout(g):
    txt = g._youtube_text("T", "D", "k1, k2")
    assert txt == "TITLE\nT\n\nDESCRIPTION\nD\n\nKEYWORDS\nk1, k2\n"


def test_youtube_prompt_language_and_limits(g):
    p_en = g._youtube_prompt("Hello world.", "en")
    assert "English" in p_en and "Hello world." in p_en
    assert "100 characters" in p_en and "5000 characters" in p_en and "500" in p_en
    assert "hashtags" in p_en
    p_id = g._youtube_prompt("Halo dunia.", "id")
    assert "Indonesian" in p_id and "Halo dunia." in p_id


# --- generate_youtube (per-language, run_ai_cli mocked) --------------------


def test_generate_youtube_per_language(g, tmp_path, monkeypatch):
    sb = _sb(g, languages=["id", "en"],
             scenes=[g.Scene(basename="01_x", classname="X", file="s.py",
                             fallback_duration=10, description="d",
                             narration={"id": "Halo.", "en": "Hi."})])
    # pre-write narration scripts the stage reads
    for lang, text in (("id", "Materi Pythagoras."), ("en", "Pythagoras material.")):
        d = tmp_path / "scripts" / lang
        d.mkdir(parents=True)
        (d / "01_x.txt").write_text(text, encoding="utf-8")

    seen_langs = []

    def fake_run_ai_cli(cli, prompt):
        # distinguish by the language's transcript embedded in the prompt
        lang = "id" if "Materi Pythagoras." in prompt else "en"
        seen_langs.append(lang)
        return json.dumps({
            "title": ("Judul " if lang == "id" else "Title ") + "T" * 130 + " 🚀 #nope",
            "description": "Hook. 🚀 " + ("x " * 50) + "\n" +
                           " ".join(f"#tag{i}" for i in range(20)),
            "keywords": ", ".join(f"kw{i:03d}" for i in range(300)),
        })

    monkeypatch.setattr(g, "run_ai_cli", fake_run_ai_cli)
    g.generate_youtube(sb, tmp_path, force=False)

    assert set(seen_langs) == {"id", "en"}
    for lang in ("id", "en"):
        out = tmp_path / "youtube" / lang / "youtube.txt"
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        title = content.split("TITLE\n", 1)[1].split("\n\n", 1)[0]
        desc = content.split("DESCRIPTION\n", 1)[1].split("\n\nKEYWORDS", 1)[0]
        kw = content.split("KEYWORDS\n", 1)[1].strip()
        assert len(title) <= g.YT_TITLE_MAX and "🚀" not in title and "#nope" not in title
        assert len(desc) <= g.YT_DESC_MAX and "🚀" not in desc
        # hashtags capped at 15 in the description
        assert len(re.findall(r"#\w+", desc)) <= 15
        assert len(kw) <= g.YT_KEYWORDS_MAX and "#" not in kw


def test_generate_youtube_skips_on_cli_failure(g, tmp_path, monkeypatch):
    sb = _sb(g, languages=["id"],
             scenes=[g.Scene(basename="01_x", classname="X", file="s.py",
                             fallback_duration=10, description="d",
                             narration={"id": "Halo."})])
    d = tmp_path / "scripts" / "id"
    d.mkdir(parents=True)
    (d / "01_x.txt").write_text("Materi.", encoding="utf-8")

    def boom(cli, prompt):
        raise SystemExit("claude not logged in")

    monkeypatch.setattr(g, "run_ai_cli", boom)
    # must NOT raise, and must NOT write the file
    g.generate_youtube(sb, tmp_path, force=False)
    assert not (tmp_path / "youtube" / "id" / "youtube.txt").exists()


def test_generate_youtube_skips_when_no_transcript(g, tmp_path, monkeypatch):
    sb = _sb(g, languages=["id"],
             scenes=[g.Scene(basename="01_x", classname="X", file="s.py",
                             fallback_duration=10, description="d", narration={})])
    called = {"n": 0}
    monkeypatch.setattr(g, "run_ai_cli", lambda *a, **k: called.__setitem__("n", called["n"] + 1) or "{}")
    g.generate_youtube(sb, tmp_path, force=False)
    assert called["n"] == 0
    assert not (tmp_path / "youtube" / "id" / "youtube.txt").exists()
