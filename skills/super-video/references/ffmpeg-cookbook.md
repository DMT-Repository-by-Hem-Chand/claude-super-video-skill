# ffmpeg cookbook (QUICK mode)

Adapted from claude-code-video-toolkit's ffmpeg skill (MIT) plus editing extras. Deliverables always get `-pix_fmt yuv420p -movflags +faststart` and even dimensions.

## Inspect

```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 in.mp4
ffprobe -v quiet -print_format json -show_format -show_streams in.mp4
```

## Trim

```bash
ffmpeg -ss 00:00:30 -to 00:00:45 -i in.mp4 -c:v libx264 -crf 18 -c:a aac out.mp4   # accurate (re-encode)
ffmpeg -ss 30 -t 15 -i in.mp4 -c copy out.mp4                                      # fast, keyframe-aligned only
```

`-c copy` can silently drop video until the next keyframe — re-encode when the cut point matters.

## Resize / reframe

```bash
-vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"   # letterbox
-vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"                      # fill & crop
-vf "scale=1280:-2"                                                                            # width, even height
-vf "scale=trunc(iw/2)*2:trunc(ih/2)*2"                                                        # force even
```

## Compress

```bash
ffmpeg -i in.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k out.mp4    # balanced
ffmpeg -i in.mp4 -c:v libx264 -crf 28 -preset slow -c:a aac -b:a 96k out.mp4        # small (WhatsApp)
# target size: bitrate_kbps ≈ size_MB * 8192 / seconds - audio_kbps ; use -b:v with -pass 1/2 for accuracy
```

## Audio

```bash
ffmpeg -i in.mp4 -vn -c:a libmp3lame -q:a 2 out.mp3          # extract mp3
ffmpeg -i in.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le out.wav   # ASR-ready
ffmpeg -i in.mp4 -i new.wav -map 0:v -map 1:a -c:v copy -c:a aac -shortest out.mp4   # replace audio
ffmpeg -i in.mp4 -af "afade=t=in:d=0.5,afade=t=out:st=9.5:d=0.5" -c:v copy out.mp4
```

## Speed

```bash
ffmpeg -i in.mp4 -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]" -map "[v]" -map "[a]" out.mp4   # 2x
ffmpeg -i in.mp4 -filter:v "setpts=0.1*PTS" -an timelapse.mp4                                                # 10x, no audio
```

`speed = source_s / target_s`; `setpts=(1/speed)*PTS`; `atempo` per stage in 0.5–2.0 — chain for more (`atempo=2.0,atempo=2.0` = 4×).

## Concatenate

```bash
printf "file '%s'\n" clip1.mp4 clip2.mp4 clip3.mp4 > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy out.mp4                      # identical codecs/params
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -crf 18 -c:a aac out.mp4  # mixed sources
```

Crossfade two clips: `-filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=<len0-0.5>[v];[0:a][1:a]acrossfade=d=0.5[a]"`.

## Overlays & text

```bash
# logo, top-right, 40px margin, 10-20 s only
ffmpeg -i in.mp4 -i logo.png -filter_complex "[1]scale=160:-1[l];[0][l]overlay=W-w-40:40:enable='between(t,10,20)'" out.mp4
# animated overlay at T=12s (shift its frame 0)
ffmpeg -i base.mp4 -i anim.mov -filter_complex "[1:v]setpts=PTS-STARTPTS+12/TB[o];[0:v][o]overlay=eof_action=pass" out.mp4
# picture-in-picture
-filter_complex "[1:v]scale=iw/4:-2[p];[0:v][p]overlay=W-w-32:H-h-32"
# side by side
-filter_complex "[0:v]scale=-2:1080[a];[1:v]scale=-2:1080[b];[a][b]hstack"
# simple text (explicit font file!)
-vf "drawtext=fontfile='C\:/Windows/Fonts/arialbd.ttf':text='Anna Daan':fontsize=72:fontcolor=white:x=(w-tw)/2:y=h*0.8"
```

## Images → video

```bash
ffmpeg -framerate 30 -i frames/f_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 out.mp4
# Ken Burns on a still, 5 s
ffmpeg -loop 1 -i photo.jpg -vf "scale=3840:-2,zoompan=z='min(zoom+0.0008,1.15)':d=150:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30" -t 5 -pix_fmt yuv420p kb.mp4
# slideshow from a list with durations: concat demuxer with "duration" lines
```

## GIF

```bash
ffmpeg -i in.mp4 -vf "fps=15,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" out.gif
ffmpeg -i in.gif -movflags +faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" out.mp4
```

## Stabilize, denoise, fix

```bash
ffmpeg -i shaky.mp4 -vf vidstabdetect=shakiness=5 -f null - && ffmpeg -i shaky.mp4 -vf vidstabtransform=smoothing=20,unsharp=5:5:0.8 stable.mp4
ffmpeg -i in.mp4 -vf hqdn3d=3:3:6:6 out.mp4                         # video denoise
ffmpeg -i in.mp4 -vf "transpose=1" out.mp4                          # rotate 90° cw
ffmpeg -i vfr_phone.mp4 -vf fps=30 -c:v libx264 -crf 18 cfr.mp4     # VFR phone footage → CFR before editing
```

## Stills

```bash
ffmpeg -ss 12.5 -i in.mp4 -frames:v 1 -q:v 2 still.jpg              # one frame (thumbnail candidate)
ffmpeg -i in.mp4 -vf "select='gt(scene,0.35)',scale=480:-1" -vsync vfr scenes/s_%03d.jpg   # scene-change frames
```

## Common errors

- *height not divisible by 2* → `scale=trunc(iw/2)*2:trunc(ih/2)*2`.
- *Non-monotonous DTS* on concat → re-encode or normalize all inputs (same fps, resolution, sample rate) first.
- Audio drift after concat of phone clips → convert VFR to CFR and resample audio to 48 kHz first.
- Windows paths in filters → forward slashes and escape the drive colon: `C\:/path/file.srt`.
