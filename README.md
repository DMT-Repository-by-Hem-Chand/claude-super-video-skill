# Super Video — one Claude Code skill for video editing and production

Drop footage in a folder, or describe the video you want, and talk to Claude Code. One skill that covers:

- **EDIT**: transcript-first cutting of real footage. Removes fillers, false starts and dead air, picks the best takes, color grades, adds 30 ms fades at every cut, burns subtitles, and builds animated overlays in parallel sub-agents.
- **CREATE**: brief → script → per-scene voiceover → music → visuals (Remotion, HyperFrames, Manim, PIL or moviepy) → render.
- **REPURPOSE**: 9:16, 1:1 and 4:5 cut-downs and highlight reels for Shorts, Reels, TikTok and WhatsApp.
- **QC**: checks cut boundaries, loudness (−14 LUFS / −1 dBTP), black and frozen frames, text size and contrast, narration pace, and runs a critic pass before anything ships.
- **Ecosystem map**: which of the 379 community video skills to use when a specialist does the job better.

It works on Windows, macOS and Linux. Without an ElevenLabs key, transcription falls back to local faster-whisper.

## Install

```powershell
# Windows (PowerShell)
git clone https://github.com/DMT-Repository-by-Hem-Chand/claude-super-video-skill $HOME\claude-super-video-skill
& $HOME\claude-super-video-skill\install.ps1
```

```bash
# macOS / Linux
git clone https://github.com/DMT-Repository-by-Hem-Chand/claude-super-video-skill ~/claude-super-video-skill
~/claude-super-video-skill/install.sh
```

The installer links or copies `skills/super-video` into `~/.claude/skills/super-video` and installs the Python dependencies. Then run `python ~/.claude/skills/super-video/helpers/doctor.py` to check the setup.

Requirements: ffmpeg, Python 3.10+, and Node 18+ (Node 22+ for HyperFrames). Optional: `ELEVENLABS_API_KEY` in `skills/super-video/.env` for Scribe transcription (better filler detection, speaker diarization, Telugu/Hindi code-switching) and TTS.

## Use

```bash
cd path/to/your/footage
claude
> edit these into a 60-second Janmashtami highlight with Telugu + English captions
> make a 30s vertical appeal video for Anna Daan from these 12 photos and this script
> cut this 40-minute katha into 5 Reels
```

The skill looks at the material, asks questions, proposes a plan and **waits for your OK** before cutting. It self-checks the render and writes everything to `<footage>/edit/`. Session memory lives in `edit/project.md`, so the next session continues where this one stopped.

## Layout

```
skills/super-video/
├── SKILL.md                 router + hard rules + loop
├── references/              loaded on demand per mode
│   ├── edit-footage.md  create-from-scratch.md  shorts-and-reframe.md
│   ├── engines.md  motion-craft.md  audio.md  captions.md
│   └── qc.md  ffmpeg-cookbook.md  ecosystem.md
├── helpers/                 transcribe, pack, timeline_view, render, grade, cutdown, pacing, doctor
└── engines/manim/           Manim production guide
```

## Credits

Built by merging and adapting:
- [browser-use/video-use](https://github.com/browser-use/video-use) (MIT): the editing pipeline and helpers
- [digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) (MIT): the production workflow, motion craft, cutdown and pacing
- [zhuyansen/awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills) (CC0): the ecosystem map and end-to-end test findings

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Changes from upstream: a local Whisper fallback, Windows fixes (UTF-8 I/O, subtitle filter paths, CUDA→CPU fallback, Windows fonts), and a unified router and QC.
