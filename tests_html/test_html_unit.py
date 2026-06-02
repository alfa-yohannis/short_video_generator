"""Unit tests for the HTML/Playwright orchestrator (video_generator_html).

Covers the HTML-specific pieces — JS scene-source extraction/validation, the
Mermaid/anime scene prompt, render-dir materialization, the component-source helper,
Chrome resolution — plus the shared logic this app reuses (storyboard parse,
voice/key resolution, TTS retry/quota, audio validation, YouTube). No browser
or network needed. (Run separately from the Manim `tests/` suite.)
"""

from __future__ import annotations

import io
import json

import pytest

from conftest import write_storyboard, silent_mp3


def _sb(g, **kw):
    defaults = dict(
        title="t", languages=["id", "en"], orientations=["landscape", "portrait"],
        voices={}, tts_provider="edge", gemini_model=g.DEFAULT_GEMINI_MODEL,
        gemini_api_key=None, ai_cli="claude", fps=30,
        resolution_landscape=(1920, 1080), scenes_landscape_dir=None,
        scenes_portrait_dir=None, scenes=[], project_brief="",
    )
    defaults.update(kw)
    return g.Storyboard(**defaults)


# --- storyboard parse (shared) ---------------------------------------------


def test_parse_storyboard(g, tmp_path):
    p = write_storyboard(tmp_path / "sb.md", title="singleton",
                         scenes=[{"basename": "01_a", "classname": "A"},
                                 {"basename": "02_b", "classname": "B"}])
    sb = g.parse_storyboard(p)
    assert sb.title == "singleton"
    assert [s.basename for s in sb.scenes] == ["01_a", "02_b"]


def test_resolve_voice_defaults(g):
    assert g._resolve_voice(_sb(g, voices={}, tts_provider="edge"), "id") == "id-ID-ArdiNeural"
    assert g._resolve_voice(_sb(g, voices={}, tts_provider="gemini"), "id") == "Iapetus"


# --- JS scene-source extraction --------------------------------------------


def test_strip_fences_js_fenced(g):
    text = "Here:\n```js\nexport default function build(ctx){ return ctx.tl; }\n```\nok"
    assert g._strip_code_fences(text).startswith("export default function build")


def test_strip_fences_js_prose_preamble(g):
    text = "Sure, here it is:\nexport default function build(ctx){}\n"
    assert g._strip_code_fences(text).startswith("export default function build")


def test_strip_fences_clean_passthrough(g):
    src = "export default function build(ctx){ return ctx.tl; }"
    assert g._strip_code_fences(src) == src


# --- JS scene validation ---------------------------------------------------


def test_validate_ok(g, tmp_path):
    g._validate_scene_source(tmp_path / "s.js",
                             "export default function build(ctx){ return ctx.tl; }")


def test_validate_no_export_raises(g, tmp_path):
    with pytest.raises(SystemExit) as ei:
        g._validate_scene_source(tmp_path / "s.js", "function build(){}")
    assert "export default" in str(ei.value)


def test_validate_unbalanced_raises(g, tmp_path):
    with pytest.raises(SystemExit):
        g._validate_scene_source(tmp_path / "s.js", "export default function build(ctx){ return (")


# --- Mermaid/anime scene prompt + common src + render dir ----------------------


def test_build_scene_prompt(g):
    sb = _sb(g, title="Singleton", project_brief="brief")
    sc = g.Scene("01_x", "X", "s.py", 12, "desc", {"id": "teks", "en": "text"})
    prompt = g._build_scene_prompt(sb, sc, skeleton="SKELETON", common_src="KIT")
    assert "export default async function build(ctx)" in prompt
    assert "Mermaid" in prompt and "anime.js timeline" in prompt and "ctx.isPortrait" in prompt
    assert "c.diagram" in prompt and "classDiagram" in prompt
    assert "KIT" in prompt and "SKELETON" in prompt
    assert "teks" in prompt and "text" in prompt and "01_x" in prompt


def test_html_common_src_has_components_and_css(g):
    src = g._html_common_src()
    assert "createComponents" in src      # from components.js
    assert "--primary" in src             # from theme.css


def test_materialize_render_dir(g, tmp_path):
    rd = g._materialize_render_dir(tmp_path)
    assert (rd / "index.html").exists()
    assert (rd / "theme.css").exists()
    assert (rd / "components.js").exists()
    assert (rd / "vendor" / "anime.min.js").exists()
    assert (rd / "vendor" / "mermaid.min.js").exists()
    assert (rd / "assets" / "fonts").is_dir()
    assert (rd / "scenes").is_dir()


def test_resolve_chrome_none_when_absent(g, monkeypatch):
    monkeypatch.setattr(g.shutil, "which", lambda _name: None)
    assert g._resolve_chrome() is None


# --- audio validation + edge retry (shared) --------------------------------


def test_valid_audio_missing_and_empty(g, tmp_path):
    assert g._valid_audio(tmp_path / "nope.mp3") is False
    (tmp_path / "e.mp3").write_bytes(b"")
    assert g._valid_audio(tmp_path / "e.mp3") is False


class _Proc:
    def __init__(self, rc, err=""):
        self.returncode, self.stderr, self.stdout = rc, err, ""


def test_edge_retry_then_success(g, tmp_path, monkeypatch):
    calls = {"n": 0}

    def run(cmd, **kw):
        calls["n"] += 1
        return _Proc(0) if calls["n"] >= 2 else _Proc(1, "Temporary failure in name resolution")

    monkeypatch.setattr(g.subprocess, "run", run)
    monkeypatch.setattr(g.time, "sleep", lambda *_: None)
    g._edge_tts_one("v", "hi", tmp_path / "a.mp3", tmp_path / "a.srt", retries=2, wait=0.0)
    assert calls["n"] == 2


# --- Gemini synth + quota (shared) -----------------------------------------


class _FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_gemini_daily_quota_raises(g, monkeypatch):
    body = json.dumps({"error": {"message": "Quota exceeded ... requests_per_model_per_day, limit: 100"}})

    def boom(req, timeout=None):
        raise g.urllib.error.HTTPError("u", 429, "Too Many", {}, io.BytesIO(body.encode()))

    monkeypatch.setattr(g.urllib.request, "urlopen", boom)
    with pytest.raises(g.GeminiQuotaError):
        g._gemini_synth("hi", "k", "m", "Iapetus", 30.0)


# --- YouTube helpers (shared) ----------------------------------------------


def test_youtube_text_and_extract_json(g):
    assert g._youtube_text("T", "D", "k") == "TITLE\nT\n\nDESCRIPTION\nD\n\nKEYWORDS\nk\n"
    assert g._extract_json('```json\n{"a": 1}\n```') == {"a": 1}


# --- TTS dispatch ----------------------------------------------------------


def test_generate_audio_unknown_provider(g, tmp_path):
    with pytest.raises(SystemExit):
        g.generate_audio(_sb(g, tts_provider="festival"), tmp_path, force=False)
