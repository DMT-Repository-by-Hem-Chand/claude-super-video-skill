# Captions

Most social video is watched muted. Burn captions for Reels/Shorts/feeds; ship a sidecar `.srt` for YouTube.

## Getting word timings

- Footage: `transcribe.py` (Scribe word-level, or `--engine whisper`).
- Generated voiceover: transcribe the TTS output, then **align to the script** — map the script's words onto the transcript timing so names, numbers and punctuation are spelled as written, never as misheard. Simple alignment: walk both word lists with `difflib.SequenceMatcher` on lowercased tokens; matched script words take the transcript word's start/end; unmatched script words interpolate between neighbours.

## Building the SRT

Output-timeline offsets (hard rule): `out_t = word.start - segment.start + segment.offset_in_output`. `render.py --build-subtitles` does this from the EDL.

Chunking: break on punctuation and on pauses ≥ 0.3 s; avoid cues shorter than 0.35 s (merge into the neighbour); max ~32 characters per line for vertical, ~42 for 16:9; at most 2 lines.

## Styles

| Style | Use | Spec |
|---|---|---|
| bold-overlay | fast social, launches | 1–3 words, UPPERCASE, bold sans, white with 2–3 px black outline, lower third (`MarginV` ≈ 35 at 1080p, higher on 9:16 to clear platform UI) |
| karaoke pill | vertical explainers | 3–5 words on a rounded pill, active word in accent colour |
| natural-sentence | documentary, talks, education | 4–7 words, sentence case, larger, `MarginV` 60–80 |

Vertical safe zones: keep captions out of the bottom ~20% (Reels/TikTok UI) and the right ~15% (action buttons). Around 62–70% of frame height is safe.

## Burning with ffmpeg

```bash
ffmpeg -i in.mp4 -vf "subtitles=master.srt:force_style='FontName=Arial,FontSize=18,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=35'" -c:a copy out.mp4
```

On Windows quote the path carefully: `subtitles='C\:/path/master.srt'` (escape the drive colon). Always burn subtitles as the **last** filter.

## Indic scripts and bilingual captions

- Use a font with the glyphs: `Nirmala UI` (Windows), `Noto Sans Telugu`, `Noto Sans Devanagari`. libass falls back silently to boxes — grab a frame and look.
- Telugu/Devanagari need complex shaping; libass in recent ffmpeg builds handles it, but verify conjuncts on a frame.
- Bilingual: two SRTs, the second with a different `Alignment=8` (top) or a smaller line above the main one. Keep one language dominant.
- For transliterated mantras/kirtans, caption the meaning, not every repetition.

## Remotion captions

`@remotion/captions` `Caption` shape: `{text, startMs, endMs, timestampMs, confidence}` per word. Group with `createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds: 800})` and render pages with the active token highlighted.
