# Design & Architecture — Multi-Subject Support

> **Status:** recommendation / design document. Describes an optional, phased refactor.
> No code is changed by this document.
>
> **Goal:** let the generator cleanly support multiple *subjects* (software design patterns,
> ArchiMate layers, TOGAF/ADM phases, and more in future) where each subject has a different
> **teaching approach** (scene content / visual style) and different **asset needs** (some load
> external SVG symbols, some are pure code/diagrams).
>
> **Hard constraint:** the existing design-pattern videos already produce good output and must keep
> producing equivalent output. Prefer reusing existing patterns over inventing new ones.

---

## 1. Current architecture — what already works well

The core pipeline is already subject-agnostic and well factored. **Do not disturb it:**

- `vgen/cli.py`, `vgen/pipeline.py` (9 stages: scripts → audio → scenes → render → mux → concat →
  thumbnails → srt → youtube), `vgen/storyboard.py`, `vgen/models.py`, `vgen/renderer.py`,
  `vgen/narration.py`, `vgen/tts.py`, `vgen/config.py`.

Two existing mechanisms are the right precedents to build on:

- **Pluggability exemplar** — the `AiClient` Strategy + `create_ai_client` Factory in
  [ai_client.py](video_generator/vgen/ai_client.py). Right model when there are a *few* variants
  with genuinely divergent **behavior** (claude vs codex subprocess handling).
- **Zero-code extension precedent** — `DeclarativeProfile` + `profiles/<name>.yaml` + `get_profile()`
  in [preparation.py:319-385](video_generator/vgen/preparation.py#L319-L385). A YAML-driven,
  drop-a-file extension point — currently scoped only to the agentic asset-**preparation** step.

Also key: the storyboard front-matter already drives most config, and the `# Preparation` markdown
block is **already** a per-storyboard scene-guidance channel — it is injected verbatim into every
scene prompt ([scenes.py:297-303](video_generator/vgen/scenes.py#L297-L303)).

---

## 2. The three coupling points (the actual problems)

### #1 — Hardcoded subject logic in the scene prompt
[scenes.py `_assets_note()`](video_generator/vgen/scenes.py#L245-L290) injects ArchiMate-specific
instructions (`archi_element`, the layer list, the six relationship arrows) for **any** storyboard
that declares assets. A non-ArchiMate subject that happens to load assets is misdirected.

### #2 — Subject helpers dumped in the shared template
[scenes_landscape/_common.py](video_generator/templates/scenes_landscape/_common.py) and
[scenes_portrait/_common.py](video_generator/templates/scenes_portrait/_common.py) each carry
~140 lines of **ArchiMate-only** helpers (`ARCHI_LAYER_FILL`, `archi_element`, `archi_logo`,
`assignment_arrow`/`serving_arrow`/`influence_arrow`/`composition_arrow`, and their geometry
helpers). This single file is copied into **every** build and injected verbatim into **every**
scene prompt — so design-pattern builds carry and show ArchiMate dead code.

The two orientation files are also ~92% byte-identical (only frame config, a few size constants,
and the portrait-only `SHORTS_SAFE_*` + `fit_to_shorts_area` differ) — a real maintenance hazard.

> Verified against real builds: design-pattern scenes use `uml_class_box`, `realization_arrow`, and
> `association_arrow` (all **generic** — they stay in core), but **never** use any ArchiMate-only
> helper. This pins the split boundary precisely.

### #3 — Duplicated bulk drivers
[auto_generate_patterns.py](auto_generate_patterns.py) and [auto_generate_ea.py](auto_generate_ea.py)
are ~95% identical (CSV queue, locking, `ensure_storyboard`, console launch, finalize/reset/status
modes, parallelism). They differ only in the storyboard-generation prompt/exemplar, the storyboard
filename suffix, and the generator CLI flags. `auto_generate_ea.py` already strains with keyword
routing (`_is_togaf_topic`) selecting between two inline exemplars. A 3rd/4th subject multiplies
this debt. (There is also a stray `auto_generate_ea copy.py` to delete.)

---

## 3. Recommended architecture — **Subject Packs**

A **Subject Pack** is the single declarative home for everything specific to one subject. It
generalizes the proven `profiles/*.yaml` precedent from "asset preparation only" to "all per-subject
knowledge". A new `subjects/` directory sits beside `profiles/`:

```
subjects/<name>/
  subject.yaml          # the manifest
  storyboard_prompt.md  # bulk-driver storyboard-generation prompt
  exemplars/default.md  # storyboard exemplar (teaching arc)
  helpers/<name>.py     # scene render helpers, composed into the build (optional)
```

### `subject.yaml` fields

| Field | Purpose |
|---|---|
| `name`, `display_name` | identity; `name` is the `subject:` front-matter value |
| `aliases` | bulk-driver topic routing (replaces `_is_togaf_topic`) |
| `scene_helpers` | helper module(s) composed into each build's `_common.py` |
| `scene_guidance` | notation/rendering rules injected into the scene prompt (replaces the hardcoded `_assets_note` text); supports an `{asset_listing}` placeholder |
| `asset_source` | `none` \| `static` (assets_dir) \| `preparation_profile` (references a `profiles/<x>.yaml`) |
| `storyboard.prompt_file`, `storyboard.exemplar_file` | bulk-driver storyboard generation |
| `naming.storyboard_suffix` | e.g. `_pattern_storyboard.md` vs `_storyboard.md` |
| `csv`, `cli_flags` | bulk-driver queue + default generator flags |

A storyboard selects its pack with **one new front-matter key**: `subject:`. Default `generic`
(reproduces today's behavior exactly). For back-compat, `preparation_profile: archi` may imply
`subject: archimate`.

### Resolution — YAML (mirror `get_profile`), **not** a Python subclass registry

New `vgen/subjects.py` mirrors `preparation.get_profile` exactly:

```python
class SubjectPack:                 # base = "generic": no helpers, empty guidance
    name = "generic"
    scene_helpers: list = []
    scene_guidance = ""
class DeclarativeSubjectPack(SubjectPack):   # built from subjects/<name>/subject.yaml
    ...
def get_subject(name) -> SubjectPack:        # folder wins, else generic (with a log note)
```

**Why YAML over Python subclasses:**

1. The five concerns are ~80% **data** (prompt/exemplar/guidance text, flag lists, naming, asset
   choice). Only the Manim helper module is code — and it is already a plain `.py` copied into the
   build, not imported into `vgen`.
2. Adding a subject must be a **no-code-change folder drop** (the stated future goal). A Python
   registry forces a `vgen/` edit + import wiring per subject.
3. The `profiles/` precedent already proved YAML works for the *hardest* per-subject concern
   (launching the Archi app + MCP server). Reuse it.
4. `ai_client._CLIENTS` is the right model for the **opposite** case (few variants, divergent
   behavior). Subjects are open-ended and mostly data → they match `profiles/`, not `ai_client`.

The base class is kept as an **escape hatch**: a future subject that genuinely needs imperative
behavior can subclass `SubjectPack` — the same dual shape as `PreparationProfile` /
`DeclarativeProfile`. No new mechanism is introduced.

### How each coupling point is removed

- **#1** — `_assets_note` keeps building the generic asset *listing*; the ArchiMate instruction
  block becomes `get_subject(storyboard.subject).scene_guidance.format(asset_listing=...)`. Generic
  subjects contribute no helper instructions.
- **#2** — the ArchiMate block moves to `subjects/archimate/helpers/archimate.py`; `materialize_dir`
  composes **only the active subject's** helpers into the build's `_common.py`. Pattern builds carry
  zero ArchiMate code; prompts show only the relevant helpers (because the prompt injects the build's
  now-subject-correct `_common` source).
- **#3** — one `auto_generate.py` parameterized by `--subject`; the two old scripts become 3-line
  shims; `_is_togaf_topic` collapses into pack `aliases` / CSV-category lookup; delete the stray copy.

### `_common.py` split (coupling #2 + the duplication)

```
templates/common/_core.py     # ~900 shared lines, orientation-agnostic, reads size constants
templates/common/_landscape.py # thin delta: frame config (16:9) + size constants
templates/common/_portrait.py  # thin delta: frame config (9:16) + SHORTS_SAFE_* + fit_to_shorts_area
```

`materialize_dir` assembles the build's single `scenes_<orient>/_common.py` by **concatenating**
core + orientation delta + the active subject's helper module(s). Concatenation (not a multi-file
import split) preserves two invariants existing builds depend on: generated scenes do
`from _common import (...)`, and the scene prompt injects one `_common` source verbatim.

---

## 4. Per-file changes (for the future refactor)

- [models.py](video_generator/vgen/models.py) — add `Storyboard.subject: str = "generic"`; emit it
  in `to_markdown` (so refinement round-trips it).
- [storyboard.py](video_generator/vgen/storyboard.py) — parse `subject:` with a sensible default.
- [config.py](video_generator/vgen/config.py) — add `SUBJECTS_DIR = REPO_ROOT / "subjects"`.
- `vgen/subjects.py` **(new)** — mirror `preparation.get_profile`.
- [scenes.py](video_generator/vgen/scenes.py) — `materialize_dir` composes active-subject helpers;
  `_assets_note` uses `pack.scene_guidance`; `build_prompt` unchanged (its `common_src` is now
  subject-correct by construction).
- `subjects/` tree **(new)** — verbatim moves of the existing exemplars/prompts/ArchiMate helpers.
- repo root — `auto_generate.py` **(new)** + the two scripts reduced to shims; delete
  `auto_generate_ea copy.py`.
- `templates/` — split into `common/_core.py` + orientation deltas.

---

## 5. Phased, behavior-preserving migration

Each phase is independently shippable, ordered by value/risk.

| Phase | Change | Risk |
|---|---|---|
| **P0** | Add the seam: `subject` field (default `generic`), `SUBJECTS_DIR`, `subjects.py` with generic only | none (nothing reads `subject` yet) |
| **P1** | Consolidate bulk drivers (#3); old scripts → shims | low (no pipeline change) |
| **P2** | Move ArchiMate helpers out of `_common` into `subjects/archimate/helpers/` (#2) | medium |
| **P3** | Make `scene_guidance` subject-driven (#1) | low (verbatim text move) |
| **P4** | Collapse landscape/portrait `_common` into core + deltas | medium (pure refactor) |

**Equivalence harness (every phase):** keep golden builds for `strategy` (pattern) and
`archimate_strategy_layer` (archimate) made before P0. After each phase, regenerate with the same
flags and diff: (1) each composed `_common.py`, (2) each generated `scene_*.py`, (3) the assembled
scene-prompt strings, (4) the final mp4 (or low-quality per-scene frames). P0–P1 should be
bit-identical on scenes; P2–P4 should be symbol/value-identical for archimate `_common` and
unchanged for pattern outputs.

---

## 6. Scope tiers — recommendation: **Tier 2**

- **Tier 1 (~2–3 days)** — fix all three coupling points as *data*: `subjects/` packs +
  `vgen/subjects.py` + subject-driven `scene_guidance` + single-helper compose + one unified
  bulk driver. *Skip* the `_core` collapse (just delete the ArchiMate block from both `_common.py`).
  Satisfies every stated requirement; adding a subject becomes a folder drop.
- **Tier 2 (~4–6 days) — recommended** — Tier 1 **plus** the landscape/portrait `_core` collapse
  (the biggest duplication, ~2×1094 lines → core + thin deltas) and pack `asset_source`/`cli_flags`
  actually driving defaults (so a storyboard often needs only `subject:`). Fixes every concrete
  problem and the duplication hazard, and stops there.
- **Tier 3 (+2–4 days, optional)** — a `subject scaffold <name>` command; per-subject narration /
  teaching-arc hooks (so TOGAF "method" voice differs from ArchiMate "notation" voice); pack-level
  scene-skeleton override. Worth it only once 4+ subjects exist or narration must genuinely diverge.

---

## 7. Alternatives considered and rejected

- **Python-subclass subject registry (à la `ai_client._CLIENTS`)** — forces a `vgen/` code edit per
  subject; subjects are mostly data. Rejected (the base class is still kept as an escape hatch).
- **Overload the existing `profiles/` to also carry scene guidance + helpers** — a profile's scope
  is the agentic preparation step (MCP launch). Many subjects need no preparation but still need
  guidance/helpers/prompt/naming. Couples two different axes; a subject should *reference* a profile,
  not *be* one.
- **Per-subject full `_common_<subject>.py` templates** — re-introduces the landscape/portrait
  duplication × subjects (N×2 near-identical 1094-line files) — the exact hazard #2 flags.
- **Multi-file `_common` package import** — breaks the verbatim-prompt-injection and
  `from _common import (...)` contracts; would require touching all working pattern builds.
- **Keyword routing kept in the bulk driver** — `_is_togaf_topic` is precisely the debt that
  multiplies; moved to pack `aliases` / CSV-category lookup.
- **Plugin entry-point registry (setuptools)** — over-engineering for a single-repo tool;
  filesystem-folder discovery (like `profiles/`) is simpler and matches existing conventions.

---

## 8. Bottom line

The core is already clean; the problem is that one subject's (ArchiMate's) specifics leaked into
three shared places. Introduce a **Subject Pack** (a `subjects/<name>/` folder resolved exactly like
the existing `profiles/`), move each leak into its pack, and unify the two bulk drivers. After Tier 2,
adding a new subject is: drop a `subjects/<name>/` folder (YAML + prompt + exemplar + optional helper
`.py`), with **zero changes to `vgen/`**.
