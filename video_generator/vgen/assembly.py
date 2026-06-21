"""Assembling per-scene clips into the final videos and subtitle files.

`ClipAssembler` does the three ffmpeg-driven steps after rendering:

* :meth:`mux` — add each scene's narration audio onto its silent video clip,
* :meth:`concat` — join a language+orientation's clips into one final video,
* :meth:`merge_subtitles` — stitch the per-scene SRTs into one, offsetting each
  scene's cues by the running clip duration.

All three skip work that's already up to date (by file mtime), so a partially
finished build resumes cheaply.
"""

from __future__ import annotations

import subprocess
from datetime import timedelta
from pathlib import Path
from typing import List, Optional

from .media import ffprobe_duration, is_up_to_date
from .models import Storyboard


class ClipAssembler:
    """Muxes, concatenates and merges subtitles for a finished render."""

    def mux(self, storyboard: Storyboard, output: Path, lang: str, orient: str,
            force: bool) -> None:
        """Combine each scene's silent video with its narration mp3."""
        clip_dir = output / "clips" / lang / orient
        clip_dir.mkdir(parents=True, exist_ok=True)
        for scene in storyboard.scenes:
            video = output / "video" / lang / orient / f"{scene.basename}.mp4"
            audio = output / "audio" / lang / f"{scene.basename}.mp3"
            clip = clip_dir / f"{scene.basename}.mp4"
            # Re-mux when either input is newer than the muxed clip.
            if not force and is_up_to_date(clip, video, audio):
                continue
            if not video.exists() or not audio.exists():
                raise SystemExit(f"Missing inputs for muxing {clip}: {video}, {audio}")
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error",
                 "-i", str(video), "-i", str(audio),
                 "-map", "0:v:0", "-map", "1:a:0",
                 "-c:v", "copy",
                 "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                 "-af", "aresample=48000,pan=stereo|c0=c0|c1=c0",
                 "-shortest", "-movflags", "+faststart",
                 str(clip)],
                check=True,
            )

    def concat(self, storyboard: Storyboard, output: Path, lang: str, orient: str,
               force: bool = False) -> Path:
        """Concatenate a language+orientation's clips into one final video."""
        clip_dir = output / "clips" / lang / orient
        final_dir = output / "final"
        final_dir.mkdir(parents=True, exist_ok=True)
        final_path = final_dir / f"{storyboard.final_stem(orient, lang)}.mp4"
        clips = [clip_dir / f"{sc.basename}.mp4" for sc in storyboard.scenes]
        # Skip the re-encode when the final is already newer than every clip.
        if not force and is_up_to_date(final_path, *clips):
            return final_path
        list_path = clip_dir / "concat_list.txt"
        list_path.write_text(
            "\n".join(f"file '{sc.basename}.mp4'" for sc in storyboard.scenes) + "\n",
            encoding="utf-8",
        )
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-f", "concat", "-safe", "0", "-i", str(list_path),
             "-r", str(storyboard.fps),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
             "-movflags", "+faststart",
             str(final_path)],
            check=True,
        )
        return final_path

    def thumbnail(self, storyboard: Storyboard, output: Path, lang: str, orient: str,
                  force: bool = False) -> Optional[Path]:
        """Save a poster frame for one (language, orientation): a still from the
        last second of the FIRST scene's clip, at
        ``final/<title>_<orient>_<lang>.png`` (alongside the final mp4/srt/txt).

        Uses the muxed per-scene clip (falls back to the raw render). Returns the
        thumbnail path, or ``None`` if there's no scene/source to grab from.
        """
        if not storyboard.scenes:
            return None
        first = storyboard.scenes[0].basename
        source = output / "clips" / lang / orient / f"{first}.mp4"
        if not source.exists():
            source = output / "video" / lang / orient / f"{first}.mp4"
        if not source.exists():
            return None
        final_dir = output / "final"
        final_dir.mkdir(parents=True, exist_ok=True)
        thumb = final_dir / f"{storyboard.final_stem(orient, lang)}.png"
        if not force and is_up_to_date(thumb, source):
            return thumb
        # -sseof -1 seeks to one second before the end, then grab a single frame.
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-sseof", "-1", "-i", str(source),
             "-frames:v", "1", "-update", "1", str(thumb)],
            check=True,
        )
        return thumb

    def merge_subtitles(self, storyboard: Storyboard, output: Path, lang: str,
                        orient: str) -> Path:
        """Merge per-scene SRTs into one, offsetting each scene by the clip length.

        Per-scene SRTs live next to the audio (``audio/<lang>/<scene>.srt``); the
        merged result lands in ``final/<title>_<orient>_<lang>.srt`` beside that
        orientation's final mp4. The cues are orientation-independent, but each
        scene is offset by *this* orientation's clip duration.
        """
        import srt as srt_lib  # lazy import so a missing dependency can be installed

        audio_dir = output / "audio" / lang
        merged: List = []
        offset = timedelta(0)
        index = 1
        for scene in storyboard.scenes:
            clip = output / "clips" / lang / orient / f"{scene.basename}.mp4"
            duration = timedelta(seconds=ffprobe_duration(clip))
            srt_path = audio_dir / f"{scene.basename}.srt"
            if srt_path.exists():
                for cue in srt_lib.parse(srt_path.read_text(encoding="utf-8")):
                    merged.append(srt_lib.Subtitle(
                        index=index,
                        start=cue.start + offset,
                        end=cue.end + offset,
                        content=cue.content,
                    ))
                    index += 1
            offset += duration
        final_dir = output / "final"
        final_dir.mkdir(parents=True, exist_ok=True)
        out_path = final_dir / f"{storyboard.final_stem(orient, lang)}.srt"
        out_path.write_text(srt_lib.compose(merged), encoding="utf-8")
        return out_path
