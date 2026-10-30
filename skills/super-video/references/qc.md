# QC — self-evaluate before the user sees anything

If you wouldn't ship it, don't present it. Max 3 fix → re-render passes; after that, report what is still wrong with timecodes.

## 1. File

```bash
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate,pix_fmt -of compact out.mp4
```

Duration matches the EDL / scene plan (± 1 frame per segment); dimensions even and as asked; `yuv420p`; audio stream present and not silent.

## 2. Every cut boundary (EDIT)

`timeline_view.py` on the **rendered output** (not the sources), ±1.5 s around every cut. Check:
- visual jump / flash / black frame at the cut
- waveform spike at the boundary (a pop that slipped past the 30 ms fade)
- subtitle hidden behind an overlay (rule: subtitles last)
- overlay showing the wrong frames or misaligned (rule: `setpts` shift)

Also sample first 2 s, last 2 s and 2–3 midpoints: grade consistency, caption readability, coherence.

## 3. Picture (any mode)

```bash
# black gaps
ffmpeg -i out.mp4 -vf "blackdetect=d=0.3:pix_th=0.10" -an -f null - 2>&1 | grep black_start
# frozen stretches > 3 s (dead air for the eye)
ffmpeg -i out.mp4 -vf "freezedetect=n=0.003:d=3" -an -f null - 2>&1 | grep freeze_start
# contact sheet for a quick look
ffmpeg -i out.mp4 -vf "fps=1/3,scale=480:-1,tile=4x4" -frames:v 1 verify/contact.png
```

First frame not empty. No text under 28 px at 1080p (2.6% of the short side). Text contrast ≥ WCAG AA (4.5:1 body, 3:1 large). Text inside the frame and inside platform safe zones. Fonts actually loaded (zoom into a frame — fallback faces look "almost Arial"). Indic glyphs render (no boxes).

## 4. Sound

```bash
ffmpeg -i out.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -15       # integrated LUFS, true peak
ffmpeg -ss <t> -t <d> -i out.mp4 -af volumedetect -f null - 2>&1 | grep -E "mean|max"   # per section
ffmpeg -i out.mp4 -af silencedetect=n=-45dB:d=1.5 -f null - 2>&1 | grep silence_start     # unexpected silence
```

Targets: −14 LUFS integrated (±1), true peak ≤ −1 dBTP; dialogue sections within ~3 dB of each other; music under speech; end card not 15 dB down. Narration pace 140–160 wpm per scene (`pacing.py`). Narration fits its scene (not cut off, < 1.5 s dead air after).

If `render.py`'s loudnorm lands under target (e.g. −16 LUFS), the true-peak ceiling limited the linear gain: the source has sharp peaks. Put a limiter before normalizing (`alimiter=limit=0.7:level=false`) and re-run, or accept and report it.

Report the numbers. Never claim it sounds good.

## 5. Critic pass (anything that will be published)

Spawn one critic sub-agent with the rendered file, the EDL or scene plan, and any reference videos. Brief it to roast, not praise:

```
You are a harsh senior video editor. Review <abs path to preview.mp4> against
<brief/EDL>. Extract frames with ffmpeg as needed. Return: a one-line verdict,
problems ranked by severity with timecodes and evidence (frame paths, levels),
and the 5 fixes to do first. No praise. Do not edit anything.
```

Fresh eyes catch cut-off payoff lines, half-second memes, unreadable small text at phone size, and the generated-look defaults.

## 6. Content and rights

- Names, dates, numbers, spellings on screen match the user's source (donation amounts, phone numbers, URLs, UPI IDs — triple-check; a wrong digit costs real money).
- Music, footage and images are owned, licensed or generated. Faces of identifiable people (especially children) only with the org's consent policy satisfied.
- No impersonation: cloned voices and avatars only of people who consented.
