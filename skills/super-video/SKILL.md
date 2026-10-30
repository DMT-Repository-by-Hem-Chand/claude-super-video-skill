---
name: super-video
description: All-in-one video editing and production for Claude Code. Edit raw footage by conversation (transcribe, cut filler and retakes, color grade, burn subtitles, add animated overlays), make videos from scratch (script, voiceover, music, Remotion / HyperFrames / Manim / PIL visuals, render), cut finished videos into vertical Shorts/Reels/TikTok, and QC loudness, pacing, captions and layout before anything ships. Use whenever the user mentions video, footage, clips, reels, shorts, edit, cut, trim, subtitles, captions, voiceover, b-roll, color grade, motion graphics, explainer, promo, launch video, ffmpeg, Remotion, or drops video files in a folder — even if they never say "edit".
---

# Super Video

One skill that merges three proven sources (see `THIRD_PARTY_NOTICES.md` at the repo root):

- **video-use** (browser-use) — conversation-driven editing of real footage: transcript-first cutting, EDL, per-segment render, self-eval.
- **claude-code-video-toolkit** (Digital Samba) — production from nothing: script → voiceover → music → visuals → compose → QC → render; motion craft; social cut-downs; pacing.
- **awesome-claude-video-skills** (Agent Skills Hub) — the map of 379 other video skills, tested end to end, so you know when to reach for a specialist.

`SKILL_DIR` below means the directory containing this file. Helpers are in `SKILL_DIR/helpers/`; run them with `python "SKILL_DIR/helpers/<name>.py"` (or `uv run`). Never write session output inside `SKILL_DIR`.

## Step 0 — Route the job

Look at what the user gave you, then pick ONE primary mode. Read only the reference file(s) that mode needs.

| The user has / wants | Mode | Read |
|---|---|---|
| Raw footage (talking head, interview, tutorial, event, travel, multi-take) to turn into an edit | **EDIT** | `references/edit-footage.md` |
| No footage — a brief, script, URL, release notes, seva/campaign idea → a finished video | **CREATE** | `references/create-from-scratch.md` |
| A finished video → vertical/square/portrait cut-downs, highlight reels | **REPURPOSE** | `references/shorts-and-reframe.md` |
| An animation, title card, lower third, kinetic text, diagram, logo sting | **MOTION** | `references/engines.md` + `references/motion-craft.md` |
| Just a conversion, trim, compress, extract audio, GIF, speed change | **QUICK** | `references/ffmpeg-cookbook.md` — no ceremony, just do it |

Cross-cutting references, read when the job touches them: `references/audio.md` (voiceover, music, SFX, loudness), `references/captions.md`, `references/qc.md` (always before showing output), `references/ecosystem.md` (when a specialist skill would do this better).

Modes combine: an EDIT often needs MOTION overlays and captions; a CREATE often ends in REPURPOSE.

## Step 1 — Cold-start check (once per machine, not every session)

```bash
python "SKILL_DIR/helpers/doctor.py"
```

It reports ffmpeg/ffprobe, Python deps, Node, yt-dlp, and whether `ELEVENLABS_API_KEY` is set. Missing key is fine: transcription falls back to local faster-whisper (`--engine whisper`) — say so, because Whisper drops some fillers. Install animation engines (HyperFrames, Remotion, Manim) lazily, the first time a slot needs one, inside that slot's directory.

## Step 2 — The universal loop

1. **Inventory.** `ffprobe` every source. Read existing memory (`edit/project.md` or `project.json`) and summarize the last session in one sentence before asking whether to continue.
2. **Look before asking.** Transcribe (EDIT) or read the brief (CREATE). Sample one or two `timeline_view.py` images for a first visual impression.
3. **Converse.** Ask questions shaped by the material — not a fixed checklist. Collect: purpose and audience, target length and aspect (16:9 / 9:16 / 1:1 / 4:5), platform, brand (palette, fonts, logo, voice), pacing feel, must-keep and must-cut moments, captions, music, language(s).
4. **Propose a strategy in 4–8 plain sentences** — shape, take choices or scene list, look, animation plan, audio plan, captions, runtime estimate. **Wait for an explicit OK.** Never touch the cut or render anything heavy before that.
5. **Execute.** Build animations in **parallel sub-agents** (one `Agent` call per slot, all in one message). Render a preview first.
6. **Self-eval before showing anything** — `references/qc.md`. Max 3 fix → re-render passes; then report what is still wrong instead of looping.
7. **Iterate on natural-language feedback.** Never re-transcribe unchanged sources. Final render only on confirmation.
8. **Persist.** Append a session entry to `edit/project.md` (EDIT) or `project.json` (CREATE): strategy, decisions + why, outstanding items.

## Hard rules (correctness, not taste — never break these)

**Editing**
1. Subtitles are applied LAST in the filter chain, after every overlay.
2. Per-segment extract → lossless `-c copy` concat. Never one giant filtergraph once overlays exist (double encode).
3. 30 ms audio fade in/out at every segment boundary — otherwise every cut pops.
4. Overlays use `setpts=PTS-STARTPTS+T/TB` so the animation's frame 0 lands at its window start.
5. Master SRT uses output-timeline offsets: `out = word.start - segment.start + segment.offset_in_output`.
6. Never cut inside a word; snap every edge to a word boundary, padded 30–200 ms (ASR drifts 50–100 ms).
7. Word-level verbatim transcripts only. Cache per source; never re-transcribe an unchanged file.
8. Never reason audio and video independently — every cut must work on both tracks.

**Production**
9. Strategy confirmation before execution. Always.
10. Loudness: master to −14 LUFS integrated, true peak ≤ −1 dBTP (two-pass `loudnorm`), then *measure* per section. You cannot listen — report numbers, never claim it "sounds good".
11. Fonts fail silently. Use explicit font paths (PIL) or assert the web font loaded (`document.fonts.check(...)`) before rendering.
12. Readable text: nothing a viewer must read under 2.6% of the frame's short side (28 px at 1080p). A line holds ≥ 0.5 s + 0.3 s per word; the last line ≥ 2 s.
13. No dead air: > 3 s with nothing changing on screen is a stall unless it's a deliberate hold. First frame must not be empty (it's the Shorts/Reels cover).
14. Never `linear` easing for arrivals/exits (cubic/exp out). Opacity and colour never bounce.
15. Even dimensions, `yuv420p`, `-movflags +faststart` on every deliverable MP4.
16. Outputs live next to the user's material (`<videos_dir>/edit/` or the project folder). Never inside `SKILL_DIR`.

Everything else in the references is a **worked example**, not a mandate. Artistic freedom is the default: invent split-screens, J/L-cuts, speed ramps, match cuts, whatever the material calls for.

## Helpers

| Helper | What it does |
|---|---|
| `doctor.py` | Environment check (ffmpeg, deps, keys, engines) |
| `transcribe.py <video> [--engine auto\|scribe\|whisper] [--language te] [--num-speakers N]` | Word-level transcript → `edit/transcripts/<name>.json`, cached |
| `transcribe_batch.py <dir>` | Same, for a folder (4 parallel workers on Scribe) |
| `pack_transcripts.py --edit-dir <dir>` | All transcripts → `takes_packed.md`, phrase lines with `[start-end]` — your primary reading view |
| `timeline_view.py <video> <start> <end>` | Filmstrip + waveform + word labels PNG for one range. Decision points only, not a scan tool |
| `render.py <edl.json> -o out.mp4 [--preview] [--build-subtitles]` | Extract → grade → fades → concat → overlays → subtitles last |
| `grade.py <in> -o <out> [--list-presets] [--filter '<ffmpeg>']` | Color grade (ASC-CDL mental model) |
| `cutdown.py --input v.mp4 --platform shorts\|reels\|tiktok [--mode blur\|crop\|pad] [--segment a-b@focus]` | Reframe to 9:16 / 1:1 / 4:5, optional highlight segments |
| `pacing.py` | Words-per-minute measure + pitch-preserving slow-down for rushed TTS |

## Memory

- EDIT sessions: `<videos_dir>/edit/project.md` — one `## Session N — YYYY-MM-DD` block per session (Strategy / Decisions / Reasoning log / Outstanding).
- CREATE projects: `<project>/project.json` — phase, scenes with status, assets, session history. Reconcile it against the filesystem on resume (an asset marked ready but missing is a flagged issue).

## Anti-patterns (consistently fail)

Pre-computed scoring heuristics instead of reading the transcript · SRT/phrase-level ASR · burning subtitles before overlays · hard audio cuts · sequential sub-agents for independent animations · editing before strategy approval · assuming the video type · the "generated look" defaults (dark navy void, glow/bloom, purple gradients, everything centred and fading up, logo docked in a corner, three KPI cards in a row) — see `references/motion-craft.md` · twenty stock whooshes · claiming audio quality you could not measure.
