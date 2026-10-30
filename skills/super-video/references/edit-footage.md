# EDIT mode — turning raw footage into a cut

Source: video-use (browser-use, MIT). The LLM never watches the video; it **reads** it through two layers:

1. **Transcript (always loaded)** — word-level timestamps, speakers, audio events like `(laughter)`, packed into `takes_packed.md` (~12 KB for an hour of takes).
2. **Visual composite (on demand)** — `timeline_view.py` filmstrip + waveform PNG for a specific range, only at decision points.

Naive frame-dumping is ~45M tokens for a 20-minute shoot; this is 12 KB of text and a handful of PNGs.

## Layout

```
<videos_dir>/
├── <sources, never modified>
└── edit/
    ├── project.md          memory, appended every session
    ├── takes_packed.md     phrase-level transcript — primary reading view
    ├── edl.json            cut decisions
    ├── transcripts/        cached raw JSON per source
    ├── animations/slot_<id>/   one dir per overlay (source + render + notes)
    ├── clips_graded/       per-segment extracts with grade + fades
    ├── master.srt          output-timeline subtitles
    ├── downloads/          yt-dlp pulls
    ├── verify/             debug frames / timeline PNGs
    ├── preview.mp4
    └── final.mp4
```

## Pipeline

```
transcribe_batch.py <dir>  →  pack_transcripts.py --edit-dir <dir>/edit  →  read takes_packed.md
→ pre-scan for slips  →  converse  →  strategy (WAIT for OK)  →  edl.json
→ animations in parallel sub-agents  →  render.py --preview  →  self-eval (qc.md)  →  final
```

**Pre-scan:** one pass over `takes_packed.md` listing verbal slips, mis-speaks, false starts and phrasings to avoid. Feed the list to the editor brief.

Multi-language footage (Telugu, Hindi, English mixed is common): pass `--language` only when the whole file is one language; otherwise let Scribe auto-detect. Scribe handles code-switching far better than local Whisper.

## Packed transcript format

```
## C0103  (duration: 43.0s, 8 phrases)
  [002.52-005.36] S0 Ninety percent of what a web agent does is completely wasted.
  [006.08-006.74] S0 We fixed this.
```

Phrases break on silence ≥ 0.5 s or speaker change. This gives word-boundary precision from text alone.

## Cut craft

- **Audio first.** Candidate cuts come from word boundaries and silence gaps.
  - Silence ≥ 400 ms: cleanest cut.
  - 150–400 ms: usable, check visually.
  - < 150 ms: unsafe, mid-phrase.
- **Padding** (worked example from a shipped launch video): 50 ms before the first kept word, 80 ms after the last. Tighter for montage energy, looser for documentary. Stay in 30–200 ms.
- **Preserve peaks.** Laughs, punchlines, emphasis. Extend past the punchline to keep the reaction — the laugh is the beat.
- **Speaker handoffs** want 400–600 ms of air (less for fast, more for cinematic).
- **Audio events** `(laughs)`, `(applause)`, `(sighs)` mark beats; extend past them.
- **J-cut / L-cut** when a hard cut feels abrupt: let the next clip's audio start under the previous picture (J) or the previous audio trail over the next picture (L). Do it in the extract step with offset audio ranges.

## Editor sub-agent brief (multi-take selection)

For "pick the best take of each beat across many clips", spawn one sub-agent with a brief shaped like this:

```
You are editing a <type> video. Pick the best take of each beat and assemble
them chronologically by beat, not by source clip order.

INPUTS
  - takes_packed.md (time-annotated phrase transcripts of all takes)
  - Context: <2 sentences from the user>
  - Speaker(s): <name, role, delivery note>
  - Structure: <archetype below, adapted, or invented>
  - Verbal slips to avoid: <pre-scan list>
  - Target runtime: <seconds>

ARCHETYPES (pick, adapt, invent)
  Launch / demo:    HOOK → PROBLEM → SOLUTION → BENEFIT → EXAMPLE → CTA
  Tutorial:         INTRO → SETUP → STEPS → GOTCHAS → RECAP
  Interview:        (QUESTION → ANSWER → FOLLOWUP) ×N
  Event / festival: ARRIVAL → HIGHLIGHTS → QUIET MOMENTS → DEPARTURE
  Appeal / seva:    HOOK (a face, a need) → STORY → IMPACT → HOW TO HELP → CTA
  Documentary:      THESIS → EVIDENCE → COUNTERPOINT → CONCLUSION
  Music:            INTRO → VERSE → CHORUS → BRIDGE → OUTRO

RULES
  - Start/end on word boundaries from the transcript, padded 30–200 ms.
  - Prefer silences ≥ 400 ms as cut targets.
  - Keep an unavoidable slip only if no better take exists; say so in "reason".
  - Over budget → drop a beat or trim tails; report the total and self-correct.

OUTPUT: JSON array only
  [{"source":"C0103","start":2.42,"end":6.85,"beat":"HOOK","quote":"...","reason":"..."}]
Then one line: total runtime check.
```

## EDL format

```json
{
  "version": 1,
  "sources": {"C0103": "/abs/path/C0103.MP4", "C0108": "/abs/path/C0108.MP4"},
  "ranges": [
    {"source": "C0103", "start": 2.42, "end": 6.85, "beat": "HOOK",
     "quote": "...", "reason": "Cleanest delivery, stops before slip at 38.46."}
  ],
  "grade": "warm_cinematic",
  "overlays": [{"file": "edit/animations/slot_1/render.mp4", "start_in_output": 0.0, "duration": 5.0}],
  "subtitles": "edit/master.srt",
  "total_duration_s": 87.4
}
```

`grade` is a preset name or a raw ffmpeg filter. `subtitles` is optional and always applied last.

## Color grade (only when asked)

Reason about the image; don't apply a preset blindly. Look at a frame, decide what's wrong, change one thing, look again.

Mental model is ASC CDL, per channel: `out = (in × slope + offset) ^ power`, then global saturation. Slope → highlights, offset → shadows, power → midtones.

`grade.py --list-presets`: `warm_cinematic` (subtle teal/orange, slightly desaturated, safe on faces), `neutral_punch` (contrast + gentle S-curve, no hue shift), `none` (default). Anything else: `--filter '<raw ffmpeg chain>'`.

Grade **per segment during extraction**, never post-concat. Check skin tones before going aggressive. Temple/indoor tungsten footage usually needs white balance (`colortemperature=temperature=5600` or `colorbalance`) before any look.

## Subtitles (only when asked)

Three dimensions: **chunking** (1/2/3 words or sentence), **case**, **placement**.

- `bold-overlay` (shipped default in `render.py`) — fast social: ~2-word UPPERCASE chunks, break on punctuation and pauses ≥ 0.3 s, grow to 3 words rather than flash a cue < 0.35 s, bold sans 18 with 2 px outline, `MarginV=35`.
- `natural-sentence` — documentary/education: 4–7 word sentence-case chunks, `MarginV=60–80`, larger font.

Non-Latin scripts (Telugu, Devanagari): set a `FontName` that has the glyphs (e.g. Nirmala UI on Windows, Noto Sans Telugu / Noto Sans Devanagari elsewhere) in the force_style, and verify on a frame — missing glyphs render as boxes silently. More in `captions.md`.

## Animation overlays

Pick the engine per slot (`engines.md`). Every slot is one sub-agent, all spawned in one message. Each brief is self-contained (sub-agents have no parent context):

1. One-sentence goal — "Build ONE animation: <spec>. Nothing else."
2. Absolute output path `<edit>/animations/slot_<id>/render.mp4`
3. Exact spec: resolution, fps, codec, pix_fmt, CRF, duration
4. Palette as concrete values (hex/RGB) and font file path
5. Frame-by-frame timeline with easing
6. Anti-list: no chrome, no extras, no titles unless specified
7. Deliverable checklist: source, render, ffprobe duration check, short report
8. "Do not ask questions. If anything is ambiguous, pick the most obvious interpretation and proceed."

**Payoff sync:** find the payoff word's timestamp; start the overlay `reveal_duration` earlier so the landing frame coincides with the spoken word.

**Durations:** sync-to-narration cards ≥ 3 s (5–7 s simple, 8–14 s complex diagrams); beat-synced accents 0.5–2 s; hold the final frame ≥ 1 s; over voiceover total ≥ narration + 1 s. Never reveal two independent elements at once.

**Typing text:** centre on the full string's width, not the partial string, or the text slides left as it types.

Worked hook idea — "show the edit": transcript words pop on their timestamps over bars from the real audio envelope; a filler "ummm" turns orange and is cut out on screen at the same frame the audio cuts. Works because picture and sound are driven by the same data. Use it whenever the story is "we removed something".

## Output spec

Match the source unless asked. Common: 1920×1080@24 cinematic, 1920×1080@30 screen, 1080×1920@30 vertical, 1080×1080@30 square, 3840×2160@24 4K. `render.py` scales to 1080p by default; change the extract command for other targets.

## Downloading sources

`yt-dlp -f "bv*+ba/b" -o "edit/downloads/%(title)s.%(ext)s" <url>` — only for material the user owns or is licensed to use.
