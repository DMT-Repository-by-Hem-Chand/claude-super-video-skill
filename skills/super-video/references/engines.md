# Rendering engines — pick per slot

Do not default to Remotion just because something is web-adjacent. Pick per animation slot or per project.

| Engine | Best for | Setup (lazy, inside the slot/project dir) |
|---|---|---|
| **PIL + PNG sequence + ffmpeg** | Simple cards: counters, typewriter, single bar reveal, progressive draw, lower thirds. Fastest to iterate. | `pip install pillow`; render frames → `ffmpeg -framerate 30 -i f_%04d.png -c:v libx264 -pix_fmt yuv420p render.mp4` |
| **HyperFrames** | HTML/CSS/GSAP compositions: kinetic type, UI motion, website/mockup-to-video, transparent WebM overlays, deterministic frame capture with lint/validate checks | Node 22+. `npx --yes hyperframes init . --example blank --non-interactive --skip-skills` → build → `npx --yes hyperframes lint` / `validate` → `npx --yes hyperframes render . -o render.mp4` (`--format webm -o render.webm` for alpha) |
| **Remotion** | Multi-scene narrated videos, React component state, reusable brand components, captions, TransitionSeries | `npx create-video@latest`; `npx remotion render <entry> <comp> render.mp4` |
| **Manim** | Equations, graphs, algorithms, state machines, 3Blue1Brown-style explainers | See `engines/manim/MANIM.md` and its references. `pip install manim` (needs a LaTeX install for MathTex) |
| **moviepy** | Pure-Python assembly: stills with Ken Burns, clip stacking, karaoke caption pills, ducked music — good for 9:16 explainers built from images | `pip install moviepy` |
| **AI video / image generation** | Short motion b-roll, illustrations, backgrounds — never for text that must be readable | Whatever generation skill or connector is available in the session (e.g. ai-video-generation skill, Higgsfield) |

Hybrids are fine (PIL background + HyperFrames layer on top; Remotion composition embedding a Manim render).

## Rules for every engine

- Render at the exact output spec: resolution, fps, `yuv420p`, CRF 18 for masters.
- Verify with `ffprobe` (duration, dimensions, fps) before reporting the slot done.
- Assert fonts loaded: in a browser engine `await document.fonts.ready; if (!document.fonts.check('700 76px "Inter"')) throw new Error('font')`. In PIL pass `ImageFont.truetype(<explicit path>, size)`; never the default font.
- Windows font paths: `C:/Windows/Fonts/` (segoeui.ttf, arialbd.ttf, Nirmala.ttf for Indic scripts). Linux: `/usr/share/fonts/`. macOS: `/System/Library/Fonts/`.
- Transparent overlays: WebM VP9 with alpha (`-c:v libvpx-vp9 -pix_fmt yuva420p`) or ProRes 4444 `.mov`. Composite with `overlay` after `setpts=PTS-STARTPTS+T/TB`.

## Remotion quick reference

```tsx
const frame = useCurrentFrame(); const {fps} = useVideoConfig();
const x = interpolate(frame, [0, 18], [40, 0], {easing: Easing.out(Easing.exp), extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
const s = spring({frame, fps, config: {damping: 15, stiffness: 100}}); // ζ≈0.75
<Sequence from={30} durationInFrames={90}><Title/></Sequence>
<OffthreadVideo src={staticFile('demos/a.mp4')} playbackRate={2}/>   // constant rate only
<Audio src={staticFile('audio/vo.mp3')} volume={(f) => interpolate(f, [0, 15], [0, 1], {extrapolateRight: 'clamp'})}/>
```

- `playbackRate` must be constant — pre-process variable speed with ffmpeg.
- Load fonts with `@remotion/google-fonts` or `loadFont` from `@remotion/fonts`, and `delayRender` until loaded.
- Use `staticFile()` for everything in `public/`; a missing file fails the render.
- Official reference skills: `npx skills add remotion-dev/skills`.

## PIL card pattern

```python
from PIL import Image, ImageDraw, ImageFont
W, H, FPS, DUR = 1920, 1080, 30, 5.0
font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 96)
ease = lambda t: 1 - (1 - t) ** 3
for i in range(int(DUR * FPS)):
    t = min(1, i / (0.6 * FPS)); a = ease(t)
    im = Image.new("RGB", (W, H), (10, 10, 10)); d = ImageDraw.Draw(im)
    text = "Anna Daan"; tw = d.textlength(text, font=font)      # centre on the FULL string
    d.text(((W - tw) / 2, H / 2 - 48 + (1 - a) * 30), text, font=font, fill=(255, 255, 255))
    im.save(f"frames/f_{i:04d}.png")
```

Opacity in PIL: draw on an RGBA layer and `Image.alpha_composite` with alpha `int(255 * a)`.
