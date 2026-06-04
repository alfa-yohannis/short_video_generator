"""Unit tests for the ``vgen`` package — pure logic, no external tools/network.

Organised by module: text helpers, the storyboard parser, subtitle math, the
TTS Strategy classes, the duration fitter, prompts, render-output parsing, the
YouTube helpers, and the CLI overrides. Network/ffmpeg behaviour lives in
``test_integration.py``.
"""

from __future__ import annotations

import io
import json
import re

import pytest

from conftest import make_storyboard, write_storyboard, FakeAiClient

from vgen import config, media, renderer, subtitles, text_utils, youtube
import vgen.tts as tts_mod
from vgen.duration import DurationFitter, count_words, estimate_seconds
from vgen.models import Scene
from vgen.narration import NarrationWriter
from vgen import density
from vgen.density import SceneTooDenseError, is_too_dense, min_fit_scale, overflow_count
from vgen.pipeline import (
    BuildOptions, apply_cli_overrides, _filtered, _guard_split, _run_with_splits, _scenes_changed,
)
from vgen.refine import StoryboardRefiner
from vgen.scenes import SceneSynthesizer
from vgen.storyboard import StoryboardParser, parse_duration_spec
from vgen.tts import (
    EdgeTtsEngine, GeminiQuotaError, GeminiTtsEngine, create_tts_engine,
    gemini_error_message, is_daily_quota, request_gemini_audio, resolve_gemini_key,
)
from vgen.youtube import YouTubeMetadataWriter


# --- text_utils: name helpers, fences, escapes, validation -----------------


def test_camel_from_snake():
    assert text_utils.camel_from_snake("strategy_pattern") == "StrategyPattern"
    assert text_utils.camel_from_snake("a-b c") == "ABC"


def test_strip_leading_digits():
    assert text_utils.strip_leading_digits("01_pengantar") == "pengantar"
    assert text_utils.strip_leading_digits("plain") == "plain"


def test_strip_code_fences_plain():
    assert text_utils.strip_code_fences("from manim import *\n") == "from manim import *"


def test_strip_code_fences_fenced():
    text = "```python\nfrom manim import *\nx = 1\n```"
    assert text_utils.strip_code_fences(text) == "from manim import *\nx = 1"


def test_strip_code_fences_drops_prose_preamble():
    text = "Here is scene 6, the conclusion, about 30s long:\nfrom manim import *\nx = 1\n"
    assert text_utils.strip_code_fences(text) == "from manim import *\nx = 1"


def test_strip_code_fences_keeps_clean_source():
    src = "from manim import *\nfrom _common import title_text\n\nclass S(Scene):\n    pass"
    assert text_utils.strip_code_fences(src) == src


def test_escape_bare_ampersand_in_literal():
    assert text_utils.escape_unsafe_ampersands('x = "Tom & Jerry"') == 'x = "Tom &amp; Jerry"'


def test_escape_leaves_known_entities():
    src = '"a &amp; b &lt; c &#39;d"'
    assert text_utils.escape_unsafe_ampersands(src) == src


def test_escape_ignores_ampersand_outside_strings():
    assert text_utils.escape_unsafe_ampersands("flags = A & B") == "flags = A & B"


def test_escape_idempotent():
    once = text_utils.escape_unsafe_ampersands('t("R&D")')
    assert once == 't("R&amp;D")'
    assert text_utils.escape_unsafe_ampersands(once) == once


def test_validate_python_source_ok(tmp_path):
    text_utils.validate_python_source(tmp_path / "s.py", "x = 1\ndef f():\n    return x\n")


def test_validate_python_source_syntax_error(tmp_path):
    with pytest.raises(SystemExit) as ei:
        text_utils.validate_python_source(tmp_path / "s.py", "def f(:\n  pass\n")
    assert "not valid Python" in str(ei.value)


# --- storyboard parser -----------------------------------------------------


@pytest.fixture()
def parser():
    return StoryboardParser()


def test_parse_scene_header_basename_and_class(parser):
    sc = parser.parse_scene("01_pengantar / Pengantar", "### description\nHi.\n")
    assert sc.basename == "01_pengantar" and sc.classname == "Pengantar" and sc.description == "Hi."


def test_parse_scene_class_meta_overrides_header(parser):
    assert parser.parse_scene("01_x / FromHeader", "**class:** FromMeta\n").classname == "FromMeta"


def test_parse_scene_classname_derived_when_absent(parser):
    assert parser.parse_scene("03_segitiga_siku", "").classname == "SegitigaSiku"


def test_parse_scene_file_and_duration(parser):
    sc = parser.parse_scene("01_x / X", "**file:** scene_x.py\n**fallback_duration:** 14\n")
    assert sc.file == "scene_x.py" and sc.fallback_duration == 14.0


def test_parse_scene_defaults_file_and_duration(parser):
    sc = parser.parse_scene("01_x / X", "### description\nno meta here\n")
    assert sc.file == "scene_01_x.py" and sc.fallback_duration == 15.0


def test_parse_scene_narration_and_extras(parser):
    body = ("**file:** s.py\n### description\nA card.\n"
            "### narration.id\nHalo.\n### narration.en\nHello.\n### notes\nremember this\n")
    sc = parser.parse_scene("01_x / X", body)
    assert sc.description == "A card."
    assert sc.narration == {"id": "Halo.", "en": "Hello."}
    assert sc.extras["notes"] == "remember this"
    assert "**file:**" not in sc.description


def test_parse_storyboard_full(parser, tmp_path):
    p = write_storyboard(
        tmp_path / "sb.md", title="pythagorean",
        voices={"id": "id-ID-ArdiNeural", "en": "en-US-GuyNeural"},
        tts_provider="gemini", gemini_model="gemini-2.5-flash-preview-tts",
        gemini_api_key="from-front-matter",
        scenes=[{"basename": "01_a", "classname": "A", "narration": {"id": "x", "en": "y"}},
                {"basename": "02_b", "classname": "B", "narration": {"id": "p", "en": "q"}}],
    )
    sb = parser.parse(p)
    assert sb.title == "pythagorean" and sb.tts_provider == "gemini"
    assert sb.gemini_model == "gemini-2.5-flash-preview-tts"
    assert sb.gemini_api_key == "from-front-matter"
    assert sb.voices == {"id": "id-ID-ArdiNeural", "en": "en-US-GuyNeural"}
    assert [s.basename for s in sb.scenes] == ["01_a", "02_b"]
    assert sb.project_brief


def test_parse_storyboard_defaults(parser, tmp_path):
    text = ("---\ntitle: minimal\n---\n\nBrief.\n\n"
            "## Scene: 01_only / Only\n\n"
            "**fallback_duration:** 120\n\n"
            "### description\nA scene.\n")
    p = tmp_path / "min.md"
    p.write_text(text, encoding="utf-8")
    sb = parser.parse(p)
    assert sb.tts_provider == "edge" and sb.ai_cli == "claude"
    assert sb.gemini_model == config.DEFAULT_GEMINI_MODEL and sb.gemini_api_key is None
    assert sb.languages == ["id", "en"] and sb.orientations == ["landscape", "portrait"]


def test_parse_storyboard_requires_front_matter(parser, tmp_path):
    p = tmp_path / "no_fm.md"
    p.write_text("# just a heading\n\n## Scene: 01_x / X\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        parser.parse(p)


def test_parse_storyboard_requires_a_scene(parser, tmp_path):
    p = tmp_path / "no_scene.md"
    p.write_text("---\ntitle: t\n---\n\nJust a brief, no scenes.\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        parser.parse(p)


def test_parse_storyboard_resolves_scene_dirs_relative(parser, tmp_path):
    (tmp_path / "land").mkdir()
    p = write_storyboard(tmp_path / "sb.md", scenes_landscape_dir="land")
    sb = parser.parse(p)
    assert sb.scenes_landscape_dir == (tmp_path / "land").resolve()
    assert sb.scenes_portrait_dir is None


def test_peek_ai_cli_reads_front_matter(tmp_path):
    p = write_storyboard(tmp_path / "sb.md", ai_cli="codex")
    assert StoryboardParser.peek_ai_cli(p) == "codex"


def test_peek_ai_cli_missing_returns_none(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("no front matter here", encoding="utf-8")
    assert StoryboardParser.peek_ai_cli(p) is None


# --- duration spec + duration budget ---------------------------------------


@pytest.mark.parametrize("value,expected", [
    (180, 180.0), (90.5, 90.5), ("180", 180.0), ("3 minutes", 180.0), ("3 min", 180.0),
    ("1.5 min", 90.0), ("90s", 90.0), ("45 seconds", 45.0), ("2:30", 150.0),
    ("1:00:00", 3600.0), (None, None), ("", None),
])
def test_parse_duration_spec(value, expected):
    assert parse_duration_spec(value) == expected


def test_parse_duration_spec_invalid():
    with pytest.raises(SystemExit):
        parse_duration_spec("soon-ish")


def _durations_md(durations):
    return [{"basename": f"{i:02d}_s", "classname": f"S{i}", "duration": d,
             "narration": {"id": "x", "en": "y"}} for i, d in enumerate(durations, start=1)]


def test_max_duration_under_budget_ok(parser, tmp_path):
    p = write_storyboard(tmp_path / "sb.md", scenes=_durations_md([60, 60, 50]))
    p.write_text(p.read_text().replace("fps: 30", "max_duration: 3 minutes\nfps: 30"))
    assert parser.parse(p).max_duration == 180.0


def test_default_min_duration_under_budget_raises(parser, tmp_path):
    p = write_storyboard(tmp_path / "sb.md", scenes=_durations_md([60, 50]))  # 110
    with pytest.raises(SystemExit) as ei:
        parser.parse(p)
    assert "minimum duration" in str(ei.value) and "110" in str(ei.value)


def test_min_duration_at_budget_ok(parser, tmp_path):
    p = write_storyboard(tmp_path / "sb.md", scenes=_durations_md([60, 60]))
    sb = parser.parse(p)
    assert sb.min_duration == 120.0 and sb.duration_budget() == 120.0


def test_max_duration_over_budget_raises(parser, tmp_path):
    p = write_storyboard(tmp_path / "sb.md", scenes=_durations_md([90, 80, 40]))  # 210
    p.write_text(p.read_text().replace("fps: 30", "max_duration: 3 minutes\nfps: 30"))
    with pytest.raises(SystemExit) as ei:
        parser.parse(p)
    assert "max_duration" in str(ei.value) and "210" in str(ei.value)


def test_max_scene_duration_alias_is_total_cap(parser, tmp_path):
    p = write_storyboard(tmp_path / "sb.md", scenes=_durations_md([100, 100]))  # 200
    p.write_text(p.read_text().replace("fps: 30", "max_scene_duration: 3 minutes\nfps: 30"))
    with pytest.raises(SystemExit):
        parser.parse(p)


# --- subtitles -------------------------------------------------------------


def test_format_timestamp():
    assert subtitles.format_timestamp(0) == "00:00:00,000"
    assert subtitles.format_timestamp(1.25) == "00:00:01,250"
    assert subtitles.format_timestamp(3661.5) == "01:01:01,500"
    assert subtitles.format_timestamp(-5) == "00:00:00,000"
    assert subtitles.format_timestamp(0.9999) == "00:00:01,000"  # ms rounding carry


def test_split_sentences():
    assert subtitles.split_sentences("Halo dunia. Foo bar! Baz?") == ["Halo dunia.", "Foo bar!", "Baz?"]
    assert subtitles.split_sentences("   ") == []


def test_write_estimated_srt(tmp_path):
    import srt as _srt
    out = tmp_path / "clip.srt"
    s1, s2 = "Kalimat satu.", "Kalimat dua lebih panjang."
    subtitles.write_estimated_srt(f"{s1} {s2}", 10.0, out)
    cues = list(_srt.parse(out.read_text(encoding="utf-8")))
    assert len(cues) == 2
    assert cues[0].start.total_seconds() == pytest.approx(0.0)
    assert cues[-1].end.total_seconds() == pytest.approx(10.0)
    expected = 10.0 * len(s1) / (len(s1) + len(s2))
    assert cues[0].end.total_seconds() == pytest.approx(expected, abs=0.05)
    assert cues[0].content == s1


def test_write_estimated_srt_empty(tmp_path):
    out = tmp_path / "clip.srt"
    subtitles.write_estimated_srt("   ", 5.0, out)
    assert out.read_text() == ""


# --- TTS: voice resolution + key resolution --------------------------------


def test_voice_for_edge_from_map():
    sb = make_storyboard(voices={"id": "id-ID-ArdiNeural", "en": "en-US-GuyNeural"})
    assert EdgeTtsEngine().voice_for(sb, "en") == "en-US-GuyNeural"


def test_voice_for_edge_default():
    assert EdgeTtsEngine().voice_for(make_storyboard(voices={}), "id") == config.DEFAULT_EDGE_VOICE


def test_voice_for_gemini_default():
    assert GeminiTtsEngine().voice_for(make_storyboard(voices={}), "id") == config.DEFAULT_GEMINI_VOICE


def test_voice_for_gemini_from_map():
    assert GeminiTtsEngine().voice_for(make_storyboard(voices={"id": "Charon"}), "id") == "Charon"


def test_resolve_gemini_key_front_matter_wins(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "from-env")
    assert resolve_gemini_key(make_storyboard(gemini_api_key="from-front-matter")) == "from-front-matter"


def test_resolve_gemini_key_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "from-env")
    assert resolve_gemini_key(make_storyboard(gemini_api_key=None)) == "from-env"


def test_resolve_gemini_key_from_dotenv(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "REPO_ROOT", tmp_path)
    (tmp_path / ".env").write_text('# c\nGEMINI_API_KEY="dotenv-secret"\nOTHER=1\n', encoding="utf-8")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert resolve_gemini_key(make_storyboard(gemini_api_key=None)) == "dotenv-secret"


def test_resolve_gemini_key_absent(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "REPO_ROOT", tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert resolve_gemini_key(make_storyboard(gemini_api_key=None)) is None


# --- TTS: factory routing --------------------------------------------------


def test_create_tts_engine_edge():
    assert isinstance(create_tts_engine(make_storyboard(tts_provider="edge")), EdgeTtsEngine)


@pytest.mark.parametrize("provider", ["gemini", "google", "google_chirp", "chirp"])
def test_create_tts_engine_gemini_and_aliases(provider):
    assert isinstance(create_tts_engine(make_storyboard(tts_provider=provider)), GeminiTtsEngine)


def test_create_tts_engine_unknown_raises():
    with pytest.raises(SystemExit):
        create_tts_engine(make_storyboard(tts_provider="festival"))


# --- EdgeTtsEngine retry ---------------------------------------------------


class _Proc:
    def __init__(self, returncode, stderr=""):
        self.returncode, self.stderr, self.stdout = returncode, stderr, ""


def test_edge_retries_then_succeeds(tmp_path, monkeypatch):
    calls = {"n": 0}

    def fake_run(cmd, **kw):
        calls["n"] += 1
        if calls["n"] < 3:
            return _Proc(1, "socket.gaierror: Temporary failure in name resolution")
        return _Proc(0)

    monkeypatch.setattr(tts_mod.subprocess, "run", fake_run)
    monkeypatch.setattr(tts_mod.time, "sleep", lambda *_: None)
    EdgeTtsEngine().synthesize_clip("v", "hi", tmp_path / "a.mp3", tmp_path / "a.srt",
                                    retries=3, wait=0.0)
    assert calls["n"] == 3


def test_edge_transient_exhausted_raises_with_hint(tmp_path, monkeypatch):
    monkeypatch.setattr(tts_mod.subprocess, "run",
                        lambda cmd, **kw: _Proc(1, "Cannot connect to host speech.platform.bing.com"))
    monkeypatch.setattr(tts_mod.time, "sleep", lambda *_: None)
    with pytest.raises(SystemExit) as ei:
        EdgeTtsEngine().synthesize_clip("v", "hi", tmp_path / "a.mp3", tmp_path / "a.srt",
                                        retries=2, wait=0.0)
    assert "network problem" in str(ei.value)


def test_edge_nontransient_fails_fast(tmp_path, monkeypatch):
    calls = {"n": 0}

    def fake_run(cmd, **kw):
        calls["n"] += 1
        return _Proc(1, "No audio was received. Verify the voice name 'bogus'.")

    monkeypatch.setattr(tts_mod.subprocess, "run", fake_run)
    monkeypatch.setattr(tts_mod.time, "sleep", lambda *_: None)
    with pytest.raises(SystemExit):
        EdgeTtsEngine().synthesize_clip("bogus", "hi", tmp_path / "a.mp3", tmp_path / "a.srt",
                                        retries=3, wait=0.0)
    assert calls["n"] == 1


# --- media validation ------------------------------------------------------


def test_valid_audio_rejects_missing_and_empty(tmp_path):
    assert media.valid_audio(tmp_path / "nope.mp3") is False
    empty = tmp_path / "empty.mp3"
    empty.write_bytes(b"")
    assert media.valid_audio(empty) is False


def test_is_up_to_date(tmp_path):
    import os
    dest, src = tmp_path / "out.mp4", tmp_path / "in.py"
    src.write_text("x")
    assert media.is_up_to_date(dest, src) is False           # dest missing
    dest.write_text("v")
    os.utime(src, (1000, 1000)); os.utime(dest, (2000, 2000))
    assert media.is_up_to_date(dest, src) is True            # dest newer
    os.utime(src, (3000, 3000))
    assert media.is_up_to_date(dest, src) is False           # src newer
    assert media.is_up_to_date(dest, tmp_path / "absent") is True  # missing src ignored


# --- Gemini HTTP parsing + quota classification ----------------------------


class _FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_request_gemini_audio_parses(monkeypatch):
    import base64
    pcm = b"\x01\x02\x03\x04"
    payload = {"candidates": [{"content": {"parts": [
        {"inlineData": {"mimeType": "audio/L16;codec=pcm;rate=24000",
                        "data": base64.b64encode(pcm).decode()}}]}}]}
    monkeypatch.setattr(tts_mod.urllib.request, "urlopen",
                        lambda req, timeout=None: _FakeResp(json.dumps(payload).encode()))
    out_pcm, rate = request_gemini_audio("hi", "key", "model", "Iapetus", 30.0)
    assert out_pcm == pcm and rate == 24000


def test_request_gemini_audio_http_error_becomes_runtimeerror(monkeypatch):
    def boom(req, timeout=None):
        raise tts_mod.urllib.error.HTTPError("u", 429, "Too Many", {},
                                             io.BytesIO(b'{"error":"quota"}'))

    monkeypatch.setattr(tts_mod.urllib.request, "urlopen", boom)
    with pytest.raises(RuntimeError) as ei:
        request_gemini_audio("hi", "key", "model", "Iapetus", 30.0)
    assert "429" in str(ei.value)


def test_request_gemini_audio_no_audio_raises(monkeypatch):
    monkeypatch.setattr(tts_mod.urllib.request, "urlopen",
                        lambda req, timeout=None: _FakeResp(json.dumps({"candidates": []}).encode()))
    with pytest.raises(RuntimeError):
        request_gemini_audio("hi", "key", "model", "Iapetus", 30.0)


_DAILY_429 = json.dumps({"error": {"code": 429, "message": (
    "You exceeded your current quota. Quota exceeded for metric: "
    "generativelanguage.googleapis.com/generate_requests_per_model_per_day, limit: 100")}})


def test_is_daily_quota_detects_per_day():
    assert is_daily_quota(_DAILY_429) is True
    assert is_daily_quota('{"error":{"message":"per_model_per_day"}}') is True
    assert is_daily_quota('{"error":{"message":"requests per minute"}}') is False


def test_gemini_error_message_extracts():
    assert "exceeded your current quota" in gemini_error_message(_DAILY_429)
    assert gemini_error_message("not json at all <html>") == "not json at all <html>"


def test_request_gemini_audio_daily_quota_raises_quota_error(monkeypatch):
    def boom(req, timeout=None):
        raise tts_mod.urllib.error.HTTPError("u", 429, "Too Many", {}, io.BytesIO(_DAILY_429.encode()))

    monkeypatch.setattr(tts_mod.urllib.request, "urlopen", boom)
    with pytest.raises(GeminiQuotaError):
        request_gemini_audio("hi", "key", "model", "Iapetus", 30.0)


def test_request_gemini_audio_other_429_is_plain_runtimeerror(monkeypatch):
    body = json.dumps({"error": {"code": 429, "message": "Rate limit: requests per minute"}})

    def boom(req, timeout=None):
        raise tts_mod.urllib.error.HTTPError("u", 429, "Too Many", {}, io.BytesIO(body.encode()))

    monkeypatch.setattr(tts_mod.urllib.request, "urlopen", boom)
    with pytest.raises(RuntimeError) as ei:
        request_gemini_audio("hi", "key", "model", "Iapetus", 30.0)
    assert not isinstance(ei.value, GeminiQuotaError) and "429" in str(ei.value)


def test_gemini_engine_quota_fast_fails_without_retry(tmp_path, monkeypatch):
    calls = {"n": 0}

    def quota(*a, **k):
        calls["n"] += 1
        raise GeminiQuotaError("daily quota exhausted")

    monkeypatch.setattr(tts_mod, "write_gemini_clip", quota)
    monkeypatch.setattr(tts_mod.time, "sleep",
                        lambda *_: (_ for _ in ()).throw(AssertionError("slept")))
    engine = GeminiTtsEngine(retries=2, wait=0.0)
    with pytest.raises(SystemExit) as ei:
        engine.synthesize_one("Halo.", "Iapetus", tmp_path / "a.mp3", tmp_path / "a.srt")
    assert calls["n"] == 1
    assert "--tts edge" in str(ei.value)


# --- duration fitter -------------------------------------------------------


def test_estimate_seconds():
    assert estimate_seconds("one two three four") == pytest.approx(4 / config.ESTIMATE_WORDS_PER_SECOND)
    assert estimate_seconds("") == 0.0


def test_fit_before_tts_compresses_when_over(tmp_path, monkeypatch):
    long_id = " ".join(["kata"] * 300)
    sb = make_storyboard(
        languages=["id"], max_duration=60.0,
        scenes=[Scene("01_a", "A", "s.py", 30, "d", {"id": long_id}),
                Scene("02_b", "B", "s.py", 30, "d", {"id": long_id})])
    (tmp_path / "scripts" / "id").mkdir(parents=True)
    fitter = DurationFitter(FakeAiClient(), EdgeTtsEngine())
    # deterministic compress = keep the first N words (no AI)
    monkeypatch.setattr(fitter, "_compress_narration",
                        lambda sb_, lang, cur, n: " ".join(cur.split()[:n]))
    fitter.fit_before_tts(sb, tmp_path)
    total = sum(estimate_seconds(s.narration["id"]) for s in sb.scenes)
    assert total <= 60.0
    assert len((tmp_path / "scripts" / "id" / "01_a.txt").read_text().split()) < 300


def test_fit_before_tts_noop_without_cap(tmp_path, monkeypatch):
    called = {"n": 0}
    sb = make_storyboard(languages=["id"], max_duration=None,
                         scenes=[Scene("01_a", "A", "s.py", 30, "d", {"id": " ".join(["w"] * 999)})])
    fitter = DurationFitter(FakeAiClient(), EdgeTtsEngine())
    monkeypatch.setattr(fitter, "_compress_narration",
                        lambda *a, **k: called.__setitem__("n", called["n"] + 1) or "x")
    fitter.fit_before_tts(sb, tmp_path)
    assert called["n"] == 0


# --- prompts ---------------------------------------------------------------


def test_narration_prompt():
    sb = make_storyboard(title="Pythagorean", project_brief="A brief about triangles.")
    sc = Scene("01_x", "X", "s.py", 20, "Title card.", {"en": "Hello there."})
    prompt = NarrationWriter(FakeAiClient()).build_prompt(sb, sc, "id")
    assert "Pythagorean" in prompt and "Title card." in prompt and "Indonesian" in prompt
    assert "Hello there." in prompt                 # the other language offered for meaning
    assert str(int(20 * 1.9)) in prompt and "HARD LIMIT" in prompt


def test_scene_prompt_includes_sources_and_narration():
    sb = make_storyboard(title="T")
    sc = Scene("01_x", "MyScene", "s.py", 10, "desc", {"id": "teks id", "en": "english text"})
    prompt = SceneSynthesizer(FakeAiClient()).build_prompt(sb, sc, "portrait", "SKELETON_MARK", "COMMON_MARK")
    assert "COMMON_MARK" in prompt and "SKELETON_MARK" in prompt
    assert "teks id" in prompt and "english text" in prompt
    assert "class MyScene(Scene)" in prompt
    assert "SHORTS_SAFE_BOTTOM" in prompt            # portrait constraint


# --- renderer output parsing -----------------------------------------------


def test_extract_layout_issues_from_layout_error():
    out = ("[layout] 1 issue(s) in RefactorSingleton:\n"
           "  - OVERFLOW: 'Same object!' extends past the frame\n"
           "LayoutError: [layout] 1 issue(s) in RefactorSingleton: "
           "OVERFLOW: 'Same object!' extends past the frame\n")
    issues = renderer.extract_layout_issues(out)
    assert issues.startswith("[layout] 1 issue(s) in RefactorSingleton:") and "OVERFLOW" in issues


def test_extract_layout_issues_falls_back_to_bullets():
    out = ("[layout] 2 issue(s) in S:\n"
           "  - OVERFLOW: 'A' extends past the frame\n"
           "  - OVERLAP: 'A' and 'B' overlap (80% of the smaller box)\n")
    assert renderer.extract_layout_issues(out) == (
        "OVERFLOW: 'A' extends past the frame; "
        "OVERLAP: 'A' and 'B' overlap (80% of the smaller box)")


def test_extract_layout_issues_ignores_non_layout():
    out = "Traceback (most recent call last):\n  File ...\nValueError: boom\n"
    assert renderer.extract_layout_issues(out) == ""


def test_extract_render_error_nameerror_with_location():
    out = ("│ /x/scenes_landscape/scene_04_refactor_singleton.py:76 in construct │\n"
           "NameError: name 'CARD_BG_OR' is not defined\n")
    msg = renderer.extract_render_error(out)
    assert msg.startswith("NameError: name 'CARD_BG_OR' is not defined")
    assert "scene_04_refactor_singleton.py:76 in construct" in msg


def test_extract_render_error_none_on_clean():
    assert renderer.extract_render_error("INFO Rendered Scene\nPlayed 5 animations\n") == ""


def test_extract_render_error_prefers_last():
    assert renderer.extract_render_error("ValueError: first\nTypeError: second one\n").startswith("TypeError: second one")


def test_extract_render_error_ignores_traceback_header():
    out = "Traceback (most recent call last):\nKeyError: 'missing'\n"
    assert renderer.extract_render_error(out).startswith("KeyError: 'missing'")


# --- YouTube helpers -------------------------------------------------------


def test_strip_emoji_and_hashtags_title():
    out = youtube.strip_emoji_and_hashtags("Belajar Pythagoras 🚀 #keren #math sekarang")
    assert "🚀" not in out and "#keren" not in out and "#math" not in out
    assert "Belajar Pythagoras" in out and "sekarang" in out


def test_strip_emoji_and_hashtags_keeps_csharp_and_punct():
    out = youtube.strip_emoji_and_hashtags("Pemrograman C# — lanjutan… selesai")
    assert "C#" in out and "—" in out and "…" in out


def test_strip_emoji_keeps_hashtags():
    out = youtube.strip_emoji("Materi keren 🚀\n#Pythagoras #Mathematics")
    assert "🚀" not in out and "#Pythagoras" in out and "#Mathematics" in out


def test_cap_hashtags_limits_to_15():
    tags = " ".join(f"#tag{i}" for i in range(20))
    kept = re.findall(r"#\w+", youtube.cap_hashtags("Deskripsi. " + tags, max_tags=15))
    assert len(kept) == 15 and kept[0] == "#tag0" and kept[-1] == "#tag14"


def test_cap_hashtags_keeps_all_when_under_limit():
    src = "Deskripsi. #a #b #c"
    assert youtube.cap_hashtags(src) == src


def test_clamp_word_boundary():
    out = youtube.clamp("satu dua tiga empat lima enam tujuh", 12)
    assert len(out) <= 12 and not out.endswith(" ")


def test_clamp_under_limit_unchanged():
    assert youtube.clamp("short", 100) == "short"


def test_clamp_keywords_total_and_intact():
    out = youtube.clamp_keywords(", ".join(f"tag{i:02d}" for i in range(200)), 500)
    assert len(out) <= 500 and all(t.strip().startswith("tag") for t in out.split(","))


def test_clamp_keywords_handles_newlines():
    assert youtube.clamp_keywords("a,\nb , c\n", 500) == "a, b, c"


def test_extract_json_variants():
    assert youtube.extract_json('{"title": "x"}')["title"] == "x"
    assert youtube.extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert youtube.extract_json('blah {"a": 2} blah') == {"a": 2}


def test_youtube_text_layout():
    assert youtube.youtube_text("T", "D", "k1, k2") == "TITLE\nT\n\nDESCRIPTION\nD\n\nKEYWORDS\nk1, k2\n"


def test_youtube_prompt_language_and_limits():
    p_en = youtube.youtube_prompt("Hello world.", "en")
    assert "English" in p_en and "Hello world." in p_en
    assert "100 characters" in p_en and "5000 characters" in p_en and "500" in p_en and "hashtags" in p_en
    p_id = youtube.youtube_prompt("Halo dunia.", "id")
    assert "Indonesian" in p_id and "Halo dunia." in p_id


# --- YouTubeMetadataWriter (AI client faked) -------------------------------


def test_youtube_writer_per_language(tmp_path):
    sb = make_storyboard(languages=["id", "en"],
                         scenes=[Scene("01_x", "X", "s.py", 10, "d", {"id": "Halo.", "en": "Hi."})])
    for lang, text in (("id", "Materi Pythagoras."), ("en", "Pythagoras material.")):
        d = tmp_path / "scripts" / lang
        d.mkdir(parents=True)
        (d / "01_x.txt").write_text(text, encoding="utf-8")

    seen = []

    def reply(prompt):
        lang = "id" if "Materi Pythagoras." in prompt else "en"
        seen.append(lang)
        return json.dumps({
            "title": ("Judul " if lang == "id" else "Title ") + "T" * 130 + " 🚀 #nope",
            "description": "Hook. 🚀 " + ("x " * 50) + "\n" + " ".join(f"#tag{i}" for i in range(20)),
            "keywords": ", ".join(f"kw{i:03d}" for i in range(300)),
        })

    YouTubeMetadataWriter(FakeAiClient(reply)).generate(sb, tmp_path, force=False)
    assert set(seen) == {"id", "en"}
    for lang in ("id", "en"):
        content = (tmp_path / "youtube" / lang / "youtube.txt").read_text(encoding="utf-8")
        title = content.split("TITLE\n", 1)[1].split("\n\n", 1)[0]
        desc = content.split("DESCRIPTION\n", 1)[1].split("\n\nKEYWORDS", 1)[0]
        kw = content.split("KEYWORDS\n", 1)[1].strip()
        assert len(title) <= config.YT_TITLE_MAX and "🚀" not in title and "#nope" not in title
        assert len(desc) <= config.YT_DESC_MAX and "🚀" not in desc
        assert len(re.findall(r"#\w+", desc)) <= 15
        assert len(kw) <= config.YT_KEYWORDS_MAX and "#" not in kw


def test_youtube_writer_skips_on_cli_failure(tmp_path):
    sb = make_storyboard(languages=["id"],
                         scenes=[Scene("01_x", "X", "s.py", 10, "d", {"id": "Halo."})])
    d = tmp_path / "scripts" / "id"
    d.mkdir(parents=True)
    (d / "01_x.txt").write_text("Materi.", encoding="utf-8")

    def boom(prompt):
        raise SystemExit("claude not logged in")

    YouTubeMetadataWriter(FakeAiClient(boom)).generate(sb, tmp_path, force=False)  # must not raise
    assert not (tmp_path / "youtube" / "id" / "youtube.txt").exists()


def test_youtube_writer_skips_when_no_transcript(tmp_path):
    sb = make_storyboard(languages=["id"],
                         scenes=[Scene("01_x", "X", "s.py", 10, "d", {})])
    fake = FakeAiClient("{}")
    YouTubeMetadataWriter(fake).generate(sb, tmp_path, force=False)
    assert fake.prompts == []                         # never asked the AI
    assert not (tmp_path / "youtube" / "id" / "youtube.txt").exists()


# --- CLI overrides ---------------------------------------------------------


def test_apply_cli_overrides_tts_and_voice():
    sb = make_storyboard(tts_provider="edge",
                         voices={"id": "id-ID-ArdiNeural", "en": "en-US-GuyNeural"})
    options = BuildOptions(storyboard="x.md", output="out", ai_cli="codex",
                           tts="gemini", voice="Charon", gemini_api_key="k")
    apply_cli_overrides(sb, options)
    assert sb.tts_provider == "gemini"
    assert set(sb.voices.values()) == {"Charon"}
    assert sb.ai_cli == "codex" and sb.gemini_api_key == "k"


def test_apply_cli_overrides_orientation_restricts_to_one():
    sb = make_storyboard()                       # defaults to [landscape, portrait]
    options = BuildOptions(storyboard="x.md", output="out", orientation="portrait")
    apply_cli_overrides(sb, options)
    assert sb.orientations == ["portrait"]


def test_apply_cli_overrides_orientation_both_keeps_storyboard():
    sb = make_storyboard()                       # [landscape, portrait]
    options = BuildOptions(storyboard="x.md", output="out", orientation="both")
    apply_cli_overrides(sb, options)
    assert sb.orientations == ["landscape", "portrait"]


def test_apply_cli_overrides_noop_when_unset():
    sb = make_storyboard(tts_provider="edge", voices={"id": "v"}, ai_cli="claude")
    options = BuildOptions(storyboard="x.md", output="out", ai_cli=None, tts=None,
                           voice=None, gemini_api_key=None)
    apply_cli_overrides(sb, options)
    assert sb.tts_provider == "edge" and sb.voices == {"id": "v"} and sb.ai_cli == "claude"


# --- AI clients use the max model / capacity by default --------------------


def _capture_command(client, monkeypatch):
    captured = {}
    monkeypatch.setattr(client, "_resolve_binary", lambda: client.name)
    monkeypatch.setattr(client, "_run", lambda cmd, prompt: captured.setdefault("cmd", cmd) or "")
    client.generate("hi")
    return captured["cmd"]


def test_claude_command_uses_max_model_and_effort(monkeypatch):
    from vgen.ai_client import ClaudeClient
    cmd = _capture_command(ClaudeClient(), monkeypatch)
    assert config.DEFAULT_CLAUDE_MODEL in cmd
    assert "--effort" in cmd and config.DEFAULT_CLAUDE_EFFORT in cmd


def test_codex_command_uses_max_reasoning(monkeypatch):
    from vgen.ai_client import CodexClient
    cmd = _capture_command(CodexClient(), monkeypatch)
    assert any("model_reasoning_effort" in str(x) and config.DEFAULT_CODEX_REASONING in str(x)
               for x in cmd)


def test_codex_omits_model_by_default(monkeypatch):
    # ChatGPT-account logins reject an explicit model, so we don't force one.
    from vgen.ai_client import CodexClient
    assert "--model" not in _capture_command(CodexClient(model=None), monkeypatch)


def test_codex_pins_model_when_set(monkeypatch):
    from vgen.ai_client import CodexClient
    cmd = _capture_command(CodexClient(model="gpt-5"), monkeypatch)
    assert "--model" in cmd and "gpt-5" in cmd


# --- per-scene validate-and-refine loop ------------------------------------


class _FakeValidator:
    """A SceneValidator stand-in: fails the check ``fail_times`` times, then passes."""

    def __init__(self, fail_times=0, problem="OVERFLOW: text past frame", is_layout=True):
        self.fail_times = fail_times
        self.problem = problem
        self.is_layout = is_layout
        self.calls = 0

    def check_scene(self, *args, **kwargs):
        self.calls += 1
        if self.calls <= self.fail_times:
            return False, self.problem, self.is_layout
        return True, "", False


def _synth_with_validator(validator, attempts):
    return SceneSynthesizer(FakeAiClient("from manim import *\n"),
                            validator=validator, validate_attempts=attempts)


def test_validate_and_fix_refines_until_pass(tmp_path, monkeypatch):
    sb = make_storyboard(languages=["id"])
    validator = _FakeValidator(fail_times=2)
    synth = _synth_with_validator(validator, attempts=10)
    repairs = {"n": 0}
    monkeypatch.setattr(synth, "repair",
                        lambda *a, **k: repairs.__setitem__("n", repairs["n"] + 1))
    scene = Scene("01_x", "X", "scene_01_x.py", 10, "d", {"id": "Halo."})
    scene_path = tmp_path / "scene_01_x.py"
    scene_path.write_text("x")
    synth._validate_and_fix(sb, tmp_path, scene, "landscape", scene_path)
    assert validator.calls == 3 and repairs["n"] == 2   # failed twice, passed on the 3rd


def test_validate_and_fix_gives_up_after_attempts(tmp_path, monkeypatch):
    sb = make_storyboard(languages=["id"])
    validator = _FakeValidator(fail_times=99)            # never passes
    synth = _synth_with_validator(validator, attempts=3)
    monkeypatch.setattr(synth, "repair", lambda *a, **k: None)
    scene = Scene("01_x", "X", "scene_01_x.py", 10, "d", {"id": "Halo."})
    scene_path = tmp_path / "scene_01_x.py"
    scene_path.write_text("x")
    with pytest.raises(SystemExit) as ei:
        synth._validate_and_fix(sb, tmp_path, scene, "landscape", scene_path)
    assert "after 3 refine attempt" in str(ei.value)


def test_validate_and_fix_noop_without_validator(tmp_path):
    sb = make_storyboard(languages=["id"])
    synth = SceneSynthesizer(FakeAiClient())             # no validator
    scene = Scene("01_x", "X", "scene_01_x.py", 10, "d", {"id": "Halo."})
    scene_path = tmp_path / "scene_01_x.py"
    scene_path.write_text("x")
    synth._validate_and_fix(sb, tmp_path, scene, "landscape", scene_path)  # must not raise


# --- storyboard refinement (over-dense -> rewrite, within the cap) ---------

from conftest import storyboard_text  # noqa: E402  (kept near its users)


def _input_storyboard(*durations):
    return make_storyboard(scenes=[
        Scene(f"{i:02d}_s", f"S{i}", f"scene_{i:02d}_s.py", d, "d", {})
        for i, d in enumerate(durations, start=1)])


def test_refiner_returns_within_cap_storyboard(tmp_path):
    # The AI "splits/trims" into three lighter scenes that still total <= 180s.
    revised = storyboard_text(scenes=[
        {"basename": "01_a", "classname": "A", "duration": 60},
        {"basename": "02_b", "classname": "B", "duration": 60},
        {"basename": "03_c", "classname": "C", "duration": 50},
    ])
    refiner = StoryboardRefiner(FakeAiClient(revised))
    sb = refiner.refine(_input_storyboard(90, 90), tmp_path, cap_seconds=180.0)
    assert [s.basename for s in sb.scenes] == ["01_a", "02_b", "03_c"]
    assert sb.duration_budget() <= 180.0
    assert (tmp_path / "storyboard.refined.md").exists()   # revision saved, original untouched


def test_refiner_retries_when_over_cap(tmp_path):
    over = storyboard_text(scenes=[{"basename": "01_a", "classname": "A", "duration": 200}])  # > 180
    ok = storyboard_text(scenes=[{"basename": "01_a", "classname": "A", "duration": 120}])
    replies = iter([over, ok])
    refiner = StoryboardRefiner(FakeAiClient(lambda _p: next(replies)))
    sb = refiner.refine(_input_storyboard(90), tmp_path, cap_seconds=180.0, attempts=3)
    assert sb.duration_budget() == 120.0


def test_refiner_gives_up_after_attempts(tmp_path):
    always_over = storyboard_text(scenes=[{"basename": "01_a", "classname": "A", "duration": 300}])
    refiner = StoryboardRefiner(FakeAiClient(always_over))
    with pytest.raises(SystemExit) as ei:
        refiner.refine(_input_storyboard(90), tmp_path, cap_seconds=180.0, attempts=2)
    assert "within the 120-180s range" in str(ei.value)


def test_refiner_strips_fence_and_prose(tmp_path):
    body = storyboard_text(scenes=[{"basename": "01_a", "classname": "A", "duration": 120}])
    reply = "Sure, here is the revised storyboard:\n```markdown\n" + body + "\n```\nHope it helps!"
    sb = StoryboardRefiner(FakeAiClient(reply)).refine(_input_storyboard(120), tmp_path, cap_seconds=180.0)
    assert [s.basename for s in sb.scenes] == ["01_a"]


def test_scenes_changed_detects_plan_edits():
    a = make_storyboard(scenes=[Scene("01_a", "A", "s.py", 30, "desc", {})])
    same = make_storyboard(scenes=[Scene("01_a", "A", "s.py", 30, "desc", {})])
    different = make_storyboard(scenes=[Scene("01_a", "A", "s.py", 20, "desc", {})])  # duration
    assert _scenes_changed(a, same) is False
    assert _scenes_changed(a, different) is True


# --- density signal: when is a failing scene "too dense"? ------------------


def _overflow(span_x, span_y=6.0, fw=14.2, fh=8.0):
    return (f"OVERFLOW: 'x' extends past the frame "
            f"(x[{-span_x/2:.2f},{span_x/2:.2f}] y[{-span_y/2:.2f},{span_y/2:.2f}], "
            f"frame {fw}x{fh})")


def test_overflow_count():
    assert overflow_count(_overflow(20)) == 1
    assert overflow_count(_overflow(20) + "; " + _overflow(18)) == 2
    assert overflow_count("OVERLAP: a and b") == 0


def test_min_fit_scale():
    # a 20-wide item in a 14.2 frame needs 14.2/20 ≈ 0.71
    assert min_fit_scale(_overflow(20)) == pytest.approx(14.2 / 20, abs=0.01)
    assert min_fit_scale("OVERLAP: no bbox here") is None


def test_is_too_dense_by_scale():
    # 24 wide in a 14.2 frame -> 0.59 < 0.60 -> too dense
    assert is_too_dense(_overflow(24), 0.60) is True
    # 20 wide -> 0.71 -> not (by scale), and only one item
    assert is_too_dense(_overflow(20), 0.60) is False


def test_is_too_dense_by_count():
    assert is_too_dense(_overflow(20) + "; " + _overflow(18), 0.60) is True


def test_is_too_dense_negatives():
    assert is_too_dense("", 0.60) is False
    assert is_too_dense("OVERLAP: a and b overlap (80% of the smaller box)", 0.60) is False


# --- Storyboard.to_markdown round-trips through the parser ------------------


def test_storyboard_to_markdown_roundtrips(tmp_path):
    sb = make_storyboard(
        title="demo", languages=["id", "en"], voices={"id": "id-ID-ArdiNeural"},
        tts_provider="edge", max_duration=180.0, project_brief="A brief.",
        scenes=[Scene("01_a", "A", "scene_01_a.py", 60, "Desc one.", {"id": "Halo.", "en": "Hi."}),
                Scene("02_b", "B", "scene_02_b.py", 60, "Desc two.", {})])
    p = tmp_path / "rt.md"
    p.write_text(sb.to_markdown(), encoding="utf-8")
    out = StoryboardParser().parse(p)
    assert out.title == "demo" and out.min_duration == 120.0 and out.max_duration == 180.0
    assert out.voices == {"id": "id-ID-ArdiNeural"}
    assert [(s.basename, s.classname, s.file, s.fallback_duration, s.description)
            for s in out.scenes] == [
        ("01_a", "A", "scene_01_a.py", 60.0, "Desc one."),
        ("02_b", "B", "scene_02_b.py", 60.0, "Desc two.")]
    assert out.scenes[0].narration == {"id": "Halo.", "en": "Hi."}
    assert out.scenes[1].narration == {}


# --- escalation: density failures lead to SceneTooDenseError ----------------


class _DenseValidator:
    """Always reports the same too-dense (2-overflow) failure."""
    def check_scene(self, *args, **kwargs):
        problem = _overflow(20) + "; " + _overflow(18)
        return False, problem, True


class _OverlapValidator:
    """Always reports a single, *non-dense* overlap (repairable in place)."""
    def check_scene(self, *args, **kwargs):
        return False, "OVERLAP: 'a' and 'b' overlap (80% of the smaller box)", True


def _synth(validator, attempts, monkeypatch, repairs):
    synth = SceneSynthesizer(FakeAiClient("from manim import *\n"),
                             validator=validator, validate_attempts=attempts)
    monkeypatch.setattr(synth, "repair",
                        lambda *a, **k: repairs.__setitem__("n", repairs["n"] + 1))
    return synth


def test_validate_escalates_to_too_dense_after_three_repairs(tmp_path, monkeypatch):
    repairs = {"n": 0}
    synth = _synth(_DenseValidator(), 10, monkeypatch, repairs)
    scene = Scene("01_x", "X", "scene_01_x.py", 20, "d", {"id": "Halo."})
    sp = tmp_path / "scene_01_x.py"
    sp.write_text("x")
    with pytest.raises(SceneTooDenseError) as ei:
        synth._validate_and_fix(make_storyboard(languages=["id"]), tmp_path, scene, "landscape", sp)
    assert repairs["n"] == config.REPAIRS_BEFORE_SPLIT      # 3 in-place repairs, then escalate
    assert ei.value.scene is scene


def test_validate_nondense_never_escalates(tmp_path, monkeypatch):
    repairs = {"n": 0}
    synth = _synth(_OverlapValidator(), 3, monkeypatch, repairs)
    scene = Scene("01_x", "X", "scene_01_x.py", 20, "d", {"id": "Halo."})
    sp = tmp_path / "scene_01_x.py"
    sp.write_text("x")
    with pytest.raises(SystemExit) as ei:        # exhausts attempts, never "too dense"
        synth._validate_and_fix(make_storyboard(languages=["id"]), tmp_path, scene, "landscape", sp)
    assert "still violates" in str(ei.value)


# --- StoryboardRefiner.split_scene -----------------------------------------


def test_split_scene_divides_duration(tmp_path):
    sb = make_storyboard(
        languages=["id", "en"], project_brief="b",
        scenes=[Scene("05_diagram", "Diagram", "scene_05_diagram.py", 60, "Too much.", {}),
                Scene("01_a", "A", "scene_01_a.py", 60, "Intro.", {})])
    revised = storyboard_text(scenes=[
        {"basename": "05_diagrama", "classname": "Diagrama", "duration": 30, "description": "part one"},
        {"basename": "05_diagramb", "classname": "Diagramb", "duration": 30, "description": "part two"},
        {"basename": "01_a", "classname": "A", "duration": 60, "description": "Intro."}])
    out = StoryboardRefiner(FakeAiClient(revised)).split_scene(
        sb, sb.scenes[0], "OVERFLOW...", tmp_path, cap_seconds=180.0)
    assert [s.basename for s in out.scenes] == ["05_diagrama", "05_diagramb", "01_a"]
    assert out.duration_budget() == 120


# --- split guards + the --only view ----------------------------------------


def test_guard_split_raises_after_max_rounds():
    exc = SceneTooDenseError(Scene("x", "X", "x.py", 24, "d", {}), "landscape", "ev")
    with pytest.raises(SystemExit):
        _guard_split(exc, config.MAX_SPLIT_ROUNDS)


def test_guard_split_raises_on_duration_floor():
    exc = SceneTooDenseError(Scene("x", "X", "x.py", 10, "d", {}), "landscape", "ev")  # 10/2=5 < 7
    with pytest.raises(SystemExit) as ei:
        _guard_split(exc, 0)
    assert "7s" in str(ei.value)


def test_guard_split_ok_when_splittable():
    exc = SceneTooDenseError(Scene("x", "X", "x.py", 24, "d", {}), "landscape", "ev")  # 24/2=12 >= 7
    _guard_split(exc, 0)   # must not raise


def test_filtered_view():
    sb = make_storyboard(scenes=[Scene("01_a", "A", "a.py", 10, "d", {}),
                                 Scene("02_b", "B", "b.py", 10, "d", {})])
    assert [s.basename for s in _filtered(sb, ["02_b"]).scenes] == ["02_b"]
    assert _filtered(sb, None) is sb
    with pytest.raises(SystemExit):
        _filtered(sb, ["nope"])


def test_run_with_splits_splits_then_succeeds(tmp_path, monkeypatch):
    import vgen.pipeline as pl
    sb = make_storyboard(scenes=[Scene("05_x", "X", "scene_05_x.py", 24, "d", {})])
    dense = sb.scenes[0]
    calls = {"runs": 0}

    class _FakePipeline:
        def __init__(self, active):
            self.active = active

        def run(self):
            calls["runs"] += 1
            if calls["runs"] == 1:
                raise SceneTooDenseError(dense, "landscape", "OVERFLOW...")

    split_sb = make_storyboard(scenes=[Scene("05_xa", "Xa", "scene_05_xa.py", 12, "d", {}),
                                       Scene("05_xb", "Xb", "scene_05_xb.py", 12, "d", {})])
    monkeypatch.setattr(pl, "build_pipeline", lambda active, o, opt: _FakePipeline(active))
    monkeypatch.setattr(pl, "create_ai_client", lambda name, effort=None: FakeAiClient())
    monkeypatch.setattr(pl.StoryboardRefiner, "split_scene",
                        lambda self, sb_, sc, ev, out, cap: split_sb)
    options = BuildOptions(storyboard="x.md", output=str(tmp_path), only=None)
    _run_with_splits(sb, tmp_path, options)
    assert calls["runs"] == 2     # raised once, split, then succeeded
