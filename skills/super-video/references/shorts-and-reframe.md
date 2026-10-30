# REPURPOSE — Shorts, Reels, TikTok, feed cut-downs

## cutdown.py (pure ffmpeg, no keys)

```bash
python "SKILL_DIR/helpers/cutdown.py" --input final.mp4 --platform shorts                 # 9:16, whole video, blur fill
python "SKILL_DIR/helpers/cutdown.py" --input final.mp4 --format 9:16 --format 1:1 --start 1:05 --end 1:50
python "SKILL_DIR/helpers/cutdown.py" --input final.mp4 --mode crop \
    --segment 0:04-0:11@0.5 --segment 0:42-0:58@0.25 --segment 2:10-2:21@0.7          # highlight reel, per-segment focus
python "SKILL_DIR/helpers/cutdown.py" --input final.mp4 --overlay frame_1080x1920.png   # branded frame on top
```

Modes:
- **blur** (default) — whole frame fitted to width over a blurred, darkened copy. Nothing lost; safe for slides and screen recordings. In 9:16 a 1080p source shows at 56% scale, so small text shrinks — `--zoom 1.3` trades a little edge for size.
- **crop** — fill by cutting the sides. Best for talking heads / one subject. `--focus` 0 = left, 0.5 = centre, 1 = right, per segment with `@`.
- **pad** — fitted over a solid colour (`--pad-color`).

Segments are joined with short audio fades so the joins don't click. Run `--help` for everything.

## Picking the moments (from a long talk, katha, event, interview)

1. Transcribe and pack (`edit-footage.md`).
2. Read `takes_packed.md` and shortlist 5–10 candidate clips, each 15–60 s, that **stand alone**: a complete thought with a hook in the first sentence and a payoff at the end. Good signals: a story, a strong claim, a number, a question answered, laughter/applause events, an emotional peak.
3. Present the shortlist as a table (start–end, hook line, payoff line, why it works) and let the user pick.
4. Cut on word boundaries with padding, add burned captions (`captions.md`, vertical safe zones), optional hook title for the first 2 s.
5. Cover frame: the first frame must not be empty or black — it's the thumbnail on Reels/Shorts.

## Platform specs

| Platform | Aspect / size | Length | Notes |
|---|---|---|---|
| YouTube Shorts | 1080×1920 | ≤ 3 min (≤ 60 s performs best) | Captions out of the bottom 20% |
| Instagram Reels | 1080×1920 (cover crops to 4:5 in grid) | 15–90 s | Keep key content inside the centre 1080×1350 |
| TikTok | 1080×1920 | 15–60 s typical | Right-side buttons, bottom caption area |
| Facebook/Instagram feed | 1080×1350 (4:5) or 1080×1080 | ≤ 60 s | Muted autoplay — captions mandatory |
| WhatsApp Status | 1080×1920 | ≤ 60 s per status, keep < 16 MB | `-crf 28 -preset slow -b:a 96k` |
| YouTube | 1920×1080 or 3840×2160 | any | Sidecar SRT, chapters in description |

Export: `-c:v libx264 -profile:v high -pix_fmt yuv420p -r 30 -c:a aac -b:a 160k -ar 48000 -movflags +faststart`.
