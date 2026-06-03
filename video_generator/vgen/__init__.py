"""``vgen`` — the bilingual Manim tutorial-video generator, organised as a
small object-oriented package.

This file is deliberately light (it imports nothing heavy) so the bootstrap step
can run before the virtual environment exists. Use it as a map of the package:

Domain model
    models.py        Scene, Storyboard            — the data every stage reads

Foundations (pure helpers, no state)
    config.py        paths + default constants
    progress.py      ProgressLogger               — the [MM:SS] console logger
    text_utils.py    clean/validate AI source text
    subtitles.py     build estimated .srt files
    media.py         ffprobe duration, mtime checks

Strategy hierarchies (swappable behaviour behind one interface)
    ai_client.py     AiClient  <- ClaudeClient / CodexClient        (narrator)
    tts.py           TtsEngine <- EdgeTtsEngine / GeminiTtsEngine    (voice)

Services (one responsibility each; take their collaborators by injection)
    storyboard.py    StoryboardParser             — markdown -> Storyboard
    refine.py        StoryboardRefiner            — rewrite an over-dense storyboard
    narration.py     NarrationWriter              — write the scripts
    scenes.py        SceneSynthesizer             — generate/repair scene .py
    duration.py      DurationFitter               — keep under max_duration
    renderer.py      ManimRenderer                — scenes -> silent clips
    assembly.py      ClipAssembler                — mux / concat / merge srt
    youtube.py       YouTubeMetadataWriter        — youtube.txt per language
    dependencies.py  DependencyChecker            — verify tools are installed

Orchestration
    pipeline.py      VideoPipeline + run_build    — runs the 8 stages
    cli.py           main()                       — argparse -> BuildOptions
    bootstrap.py     bootstrap_venv()             — self-install into .venv

The flow: a storyboard is parsed into a ``Storyboard``; ``run_build`` wires a
``VideoPipeline`` with one of each service (the *composition root*) and runs the
stages: scripts -> audio -> scenes -> render -> mux -> concat -> srt -> youtube.
"""
