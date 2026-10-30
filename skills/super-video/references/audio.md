# Audio — voiceover, music, SFX, loudness

Sound is where generated videos sound cheap. You cannot listen: measure everything and report numbers.

## Voiceover

Providers (use whatever the user has):
- **ElevenLabs** — `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}` with header `xi-api-key`, body `{"text": ..., "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "speed": 1.0}}`. Multilingual v2 handles Hindi; check Telugu support for the chosen model before promising it.
- **Self-hosted open models** (Qwen3-TTS etc.) — cheap at scale, need a GPU endpoint.
- **The user's own recording** — always the best option for a real person's voice. Voice-clone only a voice the user has rights to and consent for.

Rules:
- Generate **per scene** (`scenes/01-hook.mp3` + `01-hook.txt`).
- Comfortable pace 140–160 wpm. Measure: `wpm = words / (duration_s / 60)`. Cloned voices inherit pace from their reference clip — a snappy reference gives 170–210 wpm every time.
- Fix rushed takes deterministically: pitch-preserving `atempo` (floor 0.85×, `pacing.py` does this) rather than regenerating and hoping.
- Generate 2–3 takes for key lines and pick by pace first, pitch movement second (flat delivery = low semitone spread).
- Pronunciation: spell names phonetically in the TTS text (keep the correct spelling in captions), e.g. "Hare Krishna" is fine; "Janmashtami" → "Janma-shtami" if mispronounced.

## Music

- Music taste is the user's call. Offer two contrasting beds (e.g. warm devotional strings vs. upbeat percussion) and let them choose.
- Only licensed, royalty-free, or generated music. Never rip commercial tracks.
- **Duck under speech** −12 to −15 dB relative to the music-only level:

```bash
ffmpeg -i vo.wav -i music.mp3 -filter_complex \
 "[1:a]volume=0.9[m];[m][0:a]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=400[duck];[duck][0:a]amix=inputs=2:duration=first:normalize=0[a]" \
 -map "[a]" mix.wav
```

- Ramp music out *before* a stinger or end card (`afade=t=out`), don't let its tail decay under the CTA.
- Cut to music on a beat grid (`motion-craft.md`).

## SFX

- Fewer is better: ~8 designed hits in 18 s reads as designed; ~20 whooshes reads as generic.
- Every effect is tied to something visible (cut, landing, click).
- **Hit on the frame:** measure the effect's attack (first sample above ~−30 dBFS of its peak) and start the file that many seconds *before* the contact frame.

## Loudness — master once

Mix to PCM, then two-pass loudnorm on the final mix (YouTube/Instagram target −14 LUFS, true peak ≤ −1 dBTP):

```bash
# pass 1: measure
ffmpeg -i mix.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | tail -12
# pass 2: apply measured values
ffmpeg -i mix.wav -af loudnorm=I=-14:TP=-1:LRA=11:measured_I=<i>:measured_TP=<tp>:measured_LRA=<lra>:measured_thresh=<th>:offset=<off>:linear=true -ar 48000 master.wav
```

Then measure the rendered file and per-section levels:

```bash
ffmpeg -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -15
ffmpeg -ss 40 -t 5 -i final.mp4 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
```

An end card 15 dB under the dialogue, or music louder than speech, is a bug. Clean speech without music: `highpass=f=80,afftdn=nf=-25,acompressor=threshold=-18dB:ratio=3` is a reasonable first pass for noisy temple/hall recordings — check it didn't make the voice metallic (report, don't assume).
