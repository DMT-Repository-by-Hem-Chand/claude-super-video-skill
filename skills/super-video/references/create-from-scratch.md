# CREATE mode — a finished video from a brief

Source: claude-code-video-toolkit (Digital Samba, MIT), condensed. Pipeline:

```
BRIEF → SCRIPT → SCENE PLAN → (approve) → ASSETS (VO, music, images, b-roll, UI) → COMPOSE → QC → RENDER → CUT-DOWNS
```

Render at every stage: placeholder cards before assets exist, silent before audio exists. A video that renders end-to-end early is easier to steer than one that appears all at once.

## 1. Brief

Ask, shaped by what the user already gave you:
- Purpose and the one thing the viewer should do or remember.
- Audience and platform (YouTube 16:9, Reels/Shorts 9:16, feed 1:1 or 4:5, WhatsApp status 9:16 < 16 MB).
- Length. Rough guide: Shorts 20–45 s, promo 15–60 s, explainer 60–180 s, release notes 60–120 s.
- Brand: palette, fonts, logo, voice. If none, propose one and confirm (see Brand profile below).
- Source content: pasted notes, URL (fetch and summarise), changelog, screenshots, existing footage.
- Language(s) of narration and captions.

## 2. Script

Write `VOICEOVER-SCRIPT.md` — one section per scene, narration text plus a one-line visual note.

- **Pace:** comfortable narration is 140–160 wpm. 150 wpm ≈ 2.5 words/s, so a 30 s scene holds ~75 words. Count words before generating audio.
- Hook in the first 2 seconds (a question, a face, a surprising number, the result first).
- One idea per scene. Short sentences. Write for the ear.
- End with one clear CTA, held on screen ≥ 2 s.

## 3. Scene plan

Present a table and **wait for approval**:

| # | Scene | Type | Duration | Narration (words) | Visual | Asset status |
|---|---|---|---|---|---|---|

Scene types that recur: title, hook, problem, solution, demo (screen recording or rebuilt UI), feature, stats, testimonial/quote, story beat, b-roll montage, recap, CTA, credits.

Write `project.json` alongside:

```json
{
  "name": "janmashtami-appeal", "template": "remotion", "phase": "planning",
  "format": {"width": 1080, "height": 1920, "fps": 30},
  "brand": "brands/hkm",
  "scenes": [{"id": "01-hook", "type": "hook", "durationS": 4, "visual": {"asset": "public/img/hook.jpg", "status": "asset-needed"}}],
  "audio": {"voiceover": {"status": "script-ready"}, "music": {"status": "none"}},
  "sessions": [{"date": "YYYY-MM-DD", "summary": "Planned 7 scenes"}]
}
```

Phases: `planning → assets → audio → review → rendered → published`. On resume, reconcile statuses against the filesystem.

## 4. Assets

**Voiceover** (`audio.md`): generate **per scene** (`public/audio/scenes/01-hook.mp3` + `01-hook.txt`), never one long file — per-scene audio lets each scene's duration follow its narration. Measure wpm after generation (`pacing.py`); slow rushed takes with pitch-preserving `atempo`, floor 0.85×.

**Music:** user-supplied or licensed library track, or generated. Offer two contrasting beds and let the user choose. Duck under speech (`audio.md`).

**Images / cards:** for anything that must carry readable text, prefer designing the text in code (Remotion/HyperFrames/PIL) over asking an image model to spell it. Use image models for backgrounds, illustrations, textures. Generate at the target aspect (1440×2560 for 9:16 text cards, 2560×1440 for 16:9).

**B-roll:** real footage first (the org's own photos/video beat stock every time). AI video clips (Veo, Seedance, LTX, etc. via whichever generation skill/connector is available) for short motion inserts; boomerang or slow-zoom them to fill time rather than generating long clips.

**Product / UI demos:** two options.
- *Screen recording* with Playwright (scripted, deterministic) — `npx playwright` with `recordVideo`, fixed viewport (1440×810 or 1920×1080), slowMo for readability.
- *Synthetic UI* — rebuild the screens as static React from the app's source, drive a scripted cursor and camera (zoom/pan keyframes, every click is a frame number). Cleaner and re-editable; prefer it when the source is readable.

Speed-fit a recording to its scene: `speed = recording_s / scene_s`; `setpts=(1/speed)*PTS`, `atempo=speed` (chain atempo stages within 0.5–2.0).

## 5. Compose

Default engine: **Remotion** for narrated multi-scene videos (React, component state, `<Sequence>`/`TransitionSeries`, `@remotion/captions`). Alternatives in `engines.md`: HyperFrames (HTML/GSAP), moviepy (pure Python, good for vertical explainers built from stills + clips), Manim (math/diagrams), PIL+ffmpeg (simple cards).

Remotion scaffold:

```bash
npx create-video@latest my-video --blank      # or copy an existing template
cd my-video && npm i
npx remotion studio                           # preview
npx remotion render src/index.ts Main out/video.mp4 --codec h264 --crf 18
```

Scene timing is **audio-anchored**: each scene's `durationInFrames = ceil((narration_s + 0.4) * fps)`; music runs under the whole composition. Read `motion-craft.md` before animating anything.

Shared component ideas worth building once per org: animated background (subtle, from the brand), slide transitions with a cause, lower third / name label, narrator picture-in-picture, split screen, logo sting, captions component, CTA card with QR code.

## 6. Brand profile

```
brands/<name>/
├── brand.json   {"colors": {"primary": "#..", "accent": "#..", "bgDark": "#..", "bgLight": "#..", "text": "#.."},
│                 "fonts": {"display": "path/or/webfont", "body": "..."}, "logo": "assets/logo.svg"}
├── voice.json   {"provider": "elevenlabs", "voiceId": "...", "stability": 0.5, "similarity": 0.75, "speed": 1.0}
└── assets/      logo, backgrounds, music beds
```

Keep brand profiles in the user's project or org repo, not in this skill.

## 7. QC → render → cut-downs

Run `qc.md` checks on the preview, fix, then final render. Then offer `shorts-and-reframe.md` cut-downs and a thumbnail (a still from the strongest frame plus 3–5 words of large text).

## Scene review

Before the final render, walk the user through a scene-by-scene review: for each scene a still (`ffmpeg -ss <mid> -frames:v 1`), its narration, duration, and any QC flags. Collect changes in one round instead of re-rendering after every comment.
