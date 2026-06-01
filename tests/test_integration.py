"""Integration tests that drive real pipeline stages end to end.

Most use ffmpeg/ffprobe with fabricated silent media — no network, no API keys.
The Gemini path is exercised with `_gemini_synth` monkeypatched to return real
(silent) PCM, so the PCM->MP3 + estimated-SRT plumbing is covered without
spending quota. Tests that need the live Edge/Gemini services are marked
`network` and only run when VIDEO_GENERATOR_NETWORK_TESTS=1.
"""

from __future__ import annotations

import os

import pytest

from conftest import requires, silent_mp3, color_video, pcm_silence


def _sb(g, **kw):
    defaults = dict(
        title="demo", languages=["id"], orientations=["landscape"],
        voices={}, tts_provider="edge", gemini_model=g.DEFAULT_GEMINI_MODEL,
        gemini_api_key=None, ai_cli="claude", fps=30,
        resolution_landscape=(1920, 1080), scenes_landscape_dir=None,
        scenes_portrait_dir=None, scenes=[], project_brief="",
    )
    defaults.update(kw)
    return g.Storyboard(**defaults)


def _scene(g, basename, **kw):
    return g.Scene(basename=basename, classname=kw.get("classname", "C"),
                   file=kw.get("file", f"scene_{basename}.py"),
                   fallback_duration=kw.get("duration", 5.0),
                   description=kw.get("description", ""),
                   narration=kw.get("narration", {"id": "Halo."}))


# --- ffprobe ----------------------------------------------------------------


@requires("ffmpeg", "ffprobe")
def test_ffprobe_duration(g, tmp_path):
    mp3 = silent_mp3(tmp_path / "a.mp3", seconds=2.0)
    assert g._ffprobe_duration(mp3) == pytest.approx(2.0, abs=0.3)


# --- Gemini PCM -> MP3 + estimated SRT (no network) -------------------------


@requires("ffmpeg", "ffprobe")
def test_gemini_tts_one_pcm_to_mp3(g, tmp_path, monkeypatch):
    monkeypatch.setattr(g, "_gemini_synth", lambda *a, **k: (pcm_silence(1.0, 24000), 24000))
    mp3 = tmp_path / "01_x.mp3"
    srt = tmp_path / "01_x.srt"
    g._gemini_tts_one("Kalimat satu. Kalimat dua.", mp3, srt, "key",
                      "gemini-2.5-flash-preview-tts", "Iapetus", 30.0)
    assert mp3.exists() and mp3.stat().st_size > 0
    assert g._ffprobe_duration(mp3) == pytest.approx(1.0, abs=0.3)

    import srt as _srt
    cues = list(_srt.parse(srt.read_text(encoding="utf-8")))
    assert len(cues) == 2
    assert cues[-1].end.total_seconds() == pytest.approx(g._ffprobe_duration(mp3), abs=0.1)


@requires("ffmpeg", "ffprobe")
def test_generate_audio_gemini_skips_when_present(g, tmp_path, monkeypatch):
    sb = _sb(g, tts_provider="gemini", gemini_api_key="key",
             scenes=[_scene(g, "01_x")])
    (tmp_path / "audio" / "id").mkdir(parents=True)
    (tmp_path / "subtitles" / "id").mkdir(parents=True)
    (tmp_path / "audio" / "id" / "01_x.mp3").write_bytes(b"x")
    (tmp_path / "subtitles" / "id" / "01_x.srt").write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nHalo\n", encoding="utf-8")

    def boom(*a, **k):
        raise AssertionError("must not synthesize when outputs already exist")

    monkeypatch.setattr(g, "_gemini_synth", boom)
    g._generate_audio_gemini(sb, tmp_path, force=False)  # should be a no-op


def test_generate_audio_gemini_requires_key(g, tmp_path, monkeypatch):
    monkeypatch.setattr(g, "REPO_ROOT", tmp_path)  # isolate from the real .env
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    sb = _sb(g, tts_provider="gemini", gemini_api_key=None,
             scenes=[_scene(g, "01_x")])
    with pytest.raises(SystemExit) as ei:
        g._generate_audio_gemini(sb, tmp_path, force=False)
    assert "API key" in str(ei.value)


# --- mux + concat (ffmpeg) --------------------------------------------------


@requires("ffmpeg", "ffprobe")
def test_mux_and_concat_pipeline(g, tmp_path):
    sb = _sb(g, title="demo", scenes=[_scene(g, "01_a"), _scene(g, "02_b")])
    lang, orient = "id", "landscape"
    vdir = tmp_path / "video" / lang / orient
    adir = tmp_path / "audio" / lang
    vdir.mkdir(parents=True)
    adir.mkdir(parents=True)
    for sc in sb.scenes:
        color_video(vdir / f"{sc.basename}.mp4", seconds=1.0)
        silent_mp3(adir / f"{sc.basename}.mp3", seconds=1.0)

    g.mux_clips(sb, tmp_path, lang, orient, force=False)
    clip_dir = tmp_path / "clips" / lang / orient
    assert (clip_dir / "01_a.mp4").exists()
    assert (clip_dir / "02_b.mp4").exists()

    final = g.concat_final(sb, tmp_path, lang, orient)
    assert final.exists() and final.stat().st_size > 0
    assert final.name == "demo_landscape.mp4"
    assert g._ffprobe_duration(final) == pytest.approx(2.0, abs=0.4)


@requires("ffmpeg")
def test_mux_missing_inputs_raises(g, tmp_path):
    sb = _sb(g, scenes=[_scene(g, "01_a")])
    with pytest.raises(SystemExit):
        g.mux_clips(sb, tmp_path, "id", "landscape", force=False)


# --- merge_srts (ffmpeg for clip durations) ---------------------------------


@requires("ffmpeg", "ffprobe")
def test_merge_srts_offsets_across_scenes(g, tmp_path):
    import srt as _srt

    sb = _sb(g, title="demo", scenes=[_scene(g, "01_a"), _scene(g, "02_b")])
    lang = "id"
    clip_dir = tmp_path / "clips" / lang / "landscape"
    srt_dir = tmp_path / "subtitles" / lang
    clip_dir.mkdir(parents=True)
    srt_dir.mkdir(parents=True)
    for sc in sb.scenes:
        color_video(clip_dir / f"{sc.basename}.mp4", seconds=1.0)
        (srt_dir / f"{sc.basename}.srt").write_text(
            f"1\n00:00:00,000 --> 00:00:00,800\n{sc.basename}\n", encoding="utf-8")

    out = g.merge_srts(sb, tmp_path, lang)
    cues = list(_srt.parse(out.read_text(encoding="utf-8")))
    assert len(cues) == 2
    # the second scene's cue is offset by the first clip's (~1s) duration
    assert cues[1].start.total_seconds() >= cues[0].end.total_seconds()
    assert cues[1].start.total_seconds() == pytest.approx(1.0, abs=0.4)


# --- live Edge TTS (opt-in) -------------------------------------------------


@pytest.mark.network
@requires("ffprobe")
@pytest.mark.skipif(os.environ.get("VIDEO_GENERATOR_NETWORK_TESTS") != "1",
                    reason="set VIDEO_GENERATOR_NETWORK_TESTS=1 to hit live Edge TTS")
def test_edge_audio_generation_live(g, tmp_path):
    sb = _sb(g, tts_provider="edge", voices={"id": "id-ID-ArdiNeural"},
             scenes=[_scene(g, "01_x", narration={"id": "Halo, ini tes."})])
    g._generate_audio_edge(sb, tmp_path, force=False)
    mp3 = tmp_path / "audio" / "id" / "01_x.mp3"
    srt = tmp_path / "subtitles" / "id" / "01_x.srt"
    assert mp3.exists() and mp3.stat().st_size > 0
    assert srt.exists()
    assert g._ffprobe_duration(mp3) > 0.5
