"""Integration tests that drive real pipeline stages end to end.

Most use ffmpeg/ffprobe with fabricated silent media — no network, no API keys.
The Gemini path is exercised with ``request_gemini_audio`` monkeypatched to
return real (silent) PCM, so the PCM->MP3 + estimated-SRT plumbing is covered
without spending quota. Tests that need the live Edge/Gemini services are marked
``network`` and only run when ``VIDEO_GENERATOR_NETWORK_TESTS=1``.
"""

from __future__ import annotations

import os

import pytest

from conftest import requires, silent_mp3, color_video, pcm_silence, make_storyboard

from vgen import config, media
from vgen.assembly import ClipAssembler
from vgen.models import Scene
import vgen.tts as tts_mod
from vgen.tts import GeminiTtsEngine, EdgeTtsEngine, write_gemini_clip


def _scene(basename, **kw):
    return Scene(basename=basename, classname=kw.get("classname", "C"),
                 file=kw.get("file", f"scene_{basename}.py"),
                 fallback_duration=kw.get("duration", 5.0),
                 description=kw.get("description", ""),
                 narration=kw.get("narration", {"id": "Halo."}))


# --- ffprobe / valid_audio --------------------------------------------------


@requires("ffmpeg", "ffprobe")
def test_ffprobe_duration(tmp_path):
    mp3 = silent_mp3(tmp_path / "a.mp3", seconds=2.0)
    assert media.ffprobe_duration(mp3) == pytest.approx(2.0, abs=0.3)


@requires("ffmpeg", "ffprobe")
def test_valid_audio_accepts_real_rejects_garbage(tmp_path):
    assert media.valid_audio(silent_mp3(tmp_path / "good.mp3", seconds=1.0)) is True
    bad = tmp_path / "bad.mp3"
    bad.write_bytes(b"\x00\x01 not a real mp3 " * 16)
    assert media.valid_audio(bad) is False


# --- Gemini PCM -> MP3 + estimated SRT (no network) -------------------------


@requires("ffmpeg", "ffprobe")
def test_write_gemini_clip_pcm_to_mp3(tmp_path, monkeypatch):
    monkeypatch.setattr(tts_mod, "request_gemini_audio",
                        lambda *a, **k: (pcm_silence(1.0, 24000), 24000))
    mp3, srt = tmp_path / "01_x.mp3", tmp_path / "01_x.srt"
    write_gemini_clip("Kalimat satu. Kalimat dua.", mp3, srt, "key",
                      config.DEFAULT_GEMINI_MODEL, "Iapetus", 30.0)
    assert mp3.exists() and mp3.stat().st_size > 0
    assert media.ffprobe_duration(mp3) == pytest.approx(1.0, abs=0.3)
    import srt as _srt
    cues = list(_srt.parse(srt.read_text(encoding="utf-8")))
    assert len(cues) == 2
    assert cues[-1].end.total_seconds() == pytest.approx(media.ffprobe_duration(mp3), abs=0.1)


@requires("ffmpeg", "ffprobe")
def test_gemini_engine_skips_when_present(tmp_path, monkeypatch):
    sb = make_storyboard(languages=["id"], orientations=["landscape"],
                         tts_provider="gemini", gemini_api_key="key",
                         scenes=[_scene("01_x")])
    (tmp_path / "audio" / "id").mkdir(parents=True)
    silent_mp3(tmp_path / "audio" / "id" / "01_x.mp3", seconds=1.0)
    (tmp_path / "audio" / "id" / "01_x.srt").write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nHalo\n", encoding="utf-8")

    def boom(*a, **k):
        raise AssertionError("must not synthesize when outputs already exist")

    monkeypatch.setattr(tts_mod, "request_gemini_audio", boom)
    GeminiTtsEngine().synthesize_storyboard(sb, tmp_path, force=False)  # no-op


def test_gemini_engine_requires_key(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "REPO_ROOT", tmp_path)  # isolate from the real .env
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    sb = make_storyboard(languages=["id"], orientations=["landscape"],
                         tts_provider="gemini", gemini_api_key=None, scenes=[_scene("01_x")])
    with pytest.raises(SystemExit) as ei:
        GeminiTtsEngine().synthesize_storyboard(sb, tmp_path, force=False)
    assert "API key" in str(ei.value)


# --- mux + concat (ffmpeg) --------------------------------------------------


@requires("ffmpeg", "ffprobe")
def test_mux_and_concat_pipeline(tmp_path):
    sb = make_storyboard(title="demo", languages=["id"], orientations=["landscape"],
                         scenes=[_scene("01_a"), _scene("02_b")])
    lang, orient = "id", "landscape"
    vdir = tmp_path / "video" / lang / orient
    adir = tmp_path / "audio" / lang
    vdir.mkdir(parents=True)
    adir.mkdir(parents=True)
    for sc in sb.scenes:
        color_video(vdir / f"{sc.basename}.mp4", seconds=1.0)
        silent_mp3(adir / f"{sc.basename}.mp3", seconds=1.0)

    assembler = ClipAssembler()
    assembler.mux(sb, tmp_path, lang, orient, force=False)
    clip_dir = tmp_path / "clips" / lang / orient
    assert (clip_dir / "01_a.mp4").exists() and (clip_dir / "02_b.mp4").exists()

    # Each scene gets a SCENE_TAIL_PAD_SECONDS digest hold on its muxed clip.
    pad = config.SCENE_TAIL_PAD_SECONDS
    assert media.ffprobe_duration(clip_dir / "01_a.mp4") == pytest.approx(1.0 + pad, abs=0.4)

    final = assembler.concat(sb, tmp_path, lang, orient)
    assert final.exists() and final.name == "demo_landscape_id.mp4"
    assert media.ffprobe_duration(final) == pytest.approx(2.0 + 2 * pad, abs=0.4)


@requires("ffmpeg", "ffprobe")
def test_mux_keeps_video_that_outruns_audio(tmp_path):
    """A scene whose VIDEO runs longer than its narration must keep its full
    length — content rendered after the audio ends (e.g. a final card revealed
    once a short narration has stopped) must not be truncated to the audio."""
    sb = make_storyboard(title="demo", languages=["id"], orientations=["landscape"],
                         scenes=[_scene("01_a")])
    lang, orient = "id", "landscape"
    vdir = tmp_path / "video" / lang / orient
    adir = tmp_path / "audio" / lang
    vdir.mkdir(parents=True)
    adir.mkdir(parents=True)
    color_video(vdir / "01_a.mp4", seconds=2.0)     # video longer than the audio
    silent_mp3(adir / "01_a.mp3", seconds=1.0)

    ClipAssembler().mux(sb, tmp_path, lang, orient, force=False)
    clip = tmp_path / "clips" / lang / orient / "01_a.mp4"
    pad = config.SCENE_TAIL_PAD_SECONDS
    # The clip is the VIDEO length (+ digest pad), NOT the 1s audio.
    assert media.ffprobe_duration(clip) == pytest.approx(2.0 + pad, abs=0.4)


@requires("ffmpeg", "ffprobe")
def test_mux_keeps_audio_that_outruns_video(tmp_path):
    """Symmetric guard: a narration longer than its visuals must not be cut off —
    the clip is the longer of (video, audio) plus the digest pad, either way."""
    sb = make_storyboard(title="demo", languages=["id"], orientations=["landscape"],
                         scenes=[_scene("01_a")])
    lang, orient = "id", "landscape"
    vdir = tmp_path / "video" / lang / orient
    adir = tmp_path / "audio" / lang
    vdir.mkdir(parents=True)
    adir.mkdir(parents=True)
    color_video(vdir / "01_a.mp4", seconds=1.0)
    silent_mp3(adir / "01_a.mp3", seconds=2.0)       # audio longer than the video

    ClipAssembler().mux(sb, tmp_path, lang, orient, force=False)
    clip = tmp_path / "clips" / lang / orient / "01_a.mp4"
    pad = config.SCENE_TAIL_PAD_SECONDS
    # The clip is the AUDIO length (+ digest pad), NOT the 1s video.
    assert media.ffprobe_duration(clip) == pytest.approx(2.0 + pad, abs=0.4)


@requires("ffmpeg")
def test_mux_missing_inputs_raises(tmp_path):
    sb = make_storyboard(languages=["id"], orientations=["landscape"], scenes=[_scene("01_a")])
    with pytest.raises(SystemExit):
        ClipAssembler().mux(sb, tmp_path, "id", "landscape", force=False)


@requires("ffmpeg", "ffprobe")
def test_merge_subtitles_offsets_across_scenes(tmp_path):
    import srt as _srt
    sb = make_storyboard(title="demo", languages=["id"], orientations=["landscape"],
                         scenes=[_scene("01_a"), _scene("02_b")])
    lang, orient = "id", "landscape"
    clip_dir = tmp_path / "clips" / lang / orient
    audio_dir = tmp_path / "audio" / lang          # per-scene SRTs live beside the audio now
    clip_dir.mkdir(parents=True)
    audio_dir.mkdir(parents=True)
    for sc in sb.scenes:
        color_video(clip_dir / f"{sc.basename}.mp4", seconds=1.0)
        (audio_dir / f"{sc.basename}.srt").write_text(
            f"1\n00:00:00,000 --> 00:00:00,800\n{sc.basename}\n", encoding="utf-8")

    out = ClipAssembler().merge_subtitles(sb, tmp_path, lang, orient)
    assert out == tmp_path / "final" / "demo_landscape_id.srt"
    cues = list(_srt.parse(out.read_text(encoding="utf-8")))
    assert len(cues) == 2
    assert cues[1].start.total_seconds() >= cues[0].end.total_seconds()
    assert cues[1].start.total_seconds() == pytest.approx(1.0, abs=0.4)


# --- live Edge TTS (opt-in) -------------------------------------------------


@pytest.mark.network
@requires("ffprobe")
@pytest.mark.skipif(os.environ.get("VIDEO_GENERATOR_NETWORK_TESTS") != "1",
                    reason="set VIDEO_GENERATOR_NETWORK_TESTS=1 to hit live Edge TTS")
def test_edge_audio_generation_live(tmp_path):
    sb = make_storyboard(languages=["id"], orientations=["landscape"],
                         tts_provider="edge", voices={"id": "id-ID-ArdiNeural"},
                         scenes=[_scene("01_x", narration={"id": "Halo, ini tes."})])
    EdgeTtsEngine().synthesize_storyboard(sb, tmp_path, force=False)
    mp3 = tmp_path / "audio" / "id" / "01_x.mp3"
    assert mp3.exists() and mp3.stat().st_size > 0
    assert (tmp_path / "audio" / "id" / "01_x.srt").exists()
    assert media.ffprobe_duration(mp3) > 0.5


@requires("ffmpeg", "ffprobe")
def test_concat_splices_bumpers_in_order(tmp_path, monkeypatch):
    """Engagement bumper after the FIRST scene, end bumper at the END — and the
    final length is the sum (scenes + both bumpers)."""
    from vgen import config as _config
    bdir = tmp_path / "bumpers"
    bdir.mkdir()
    monkeypatch.setattr(_config, "BUMPERS_DIR", bdir)
    color_video(bdir / "engagement_landscape_id.mp4", seconds=2.0)
    color_video(bdir / "end_landscape_id.mp4", seconds=3.0)

    sb = make_storyboard(title="demo", languages=["id"], orientations=["landscape"],
                         scenes=[_scene("01_a"), _scene("02_b")], bumpers=True)
    lang, orient = "id", "landscape"
    cdir = tmp_path / "clips" / lang / orient
    cdir.mkdir(parents=True)
    for sc in sb.scenes:
        color_video(cdir / f"{sc.basename}.mp4", seconds=1.0)

    asm = ClipAssembler()
    names = [c.name for c, _ in asm._final_sequence(sb, tmp_path, lang, orient)]
    assert names == ["01_a.mp4", "engagement_landscape_id.mp4",
                     "02_b.mp4", "end_landscape_id.mp4"]

    final = asm.concat(sb, tmp_path, lang, orient)
    assert media.ffprobe_duration(final) == pytest.approx(1 + 2 + 1 + 3, abs=0.5)
