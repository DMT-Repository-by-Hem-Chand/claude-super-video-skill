# Motion craft

Numbers for how things move, and the defaults that make a video look AI-generated. Adapted from claude-code-video-toolkit's motion-craft notes (MIT), which in turn adapt HyperFrames' measured motion references (HeyGen, Apache-2.0). Frame counts at 30 fps. A brand guideline or a user reference always wins over these.

## Moves

| Rule | Seconds | Frames @30 |
|---|---|---|
| Fast move (card, panel, camera punch) | 0.3–0.6 s | 9–18 |
| Exit vs entrance | exit 40–50% shorter | 18f in → ~10f out |
| Next element starts when previous is | 30–50% done | |
| Stagger letters / words / list items | 1f / 2–4f / 1–2f | |

- Arrive slow, leave clean. One move = one interpolation (don't chain tweens to fake an ease).
- Fully sequential looks robotic; all-at-once looks cheap; overlap 30–50% is the middle.

## Ease by role

| Role | Ease | Remotion | GSAP / CSS |
|---|---|---|---|
| Arrival | long-tailed ease-out | `Easing.out(Easing.exp)` | `expo.out` |
| Camera move, colour flood | ease in-out | `Easing.inOut(Easing.cubic)` | `power2.inOut` |
| Exit, zoom through | accelerate | `Easing.in(Easing.poly(4))` | `power3.in` |
| Constant motion that is the point (progress, rotation) | linear | `Easing.linear` | `none` |

Python (PIL frames): `ease_out_cubic = lambda t: 1-(1-t)**3`; `ease_in_out_cubic = lambda t: 4*t**3 if t<.5 else 1-(-2*t+2)**3/2`.

## Springs

Name a spring by damping ratio ζ = damping / (2·√(stiffness·mass)). Remotion's default (10/100/1) is ζ = 0.5 — playful, not neutral.

| ζ | Reads as | damping @ stiffness 100 |
|---|---|---|
| 1.0 | no bounce | 20 |
| 0.7–0.85 | premium, settled | 14–17 |
| 0.4–0.6 | playful | 8–12 |

Position and size may bounce. Opacity and colour never (use `interpolate` or `overshootClamping: true`). UI never bounces unless the brand is playful.

## Text

- A landed title is dead still — no drift, breathe or creep.
- Vary entrances inside one video. Alternatives to fade-slide-up: per-word blur 6px→0 over 4f, 2f apart; per-word grey→ink; whole-line blur 8px→0; per-letter for a name, 3f apart; slot-machine roll of one word.
- Read time: 0.5 s + 0.3 s per word; last line ≥ 2 s.
- Size: titles 4–9% of frame height; body 2.5–4%; nothing readable under 2.6% of the short side (28 px @1080p).
- Highlight one meaningful word in the accent colour, not decorative ones.

## Rhythm

- Montage cuts every 4–24 frames; UI demos hold 7–10 s while the UI acts; most shots 1.8–3 s with motion inside.
- Hold 0.3–0.75 s before a payoff, then play it at normal speed.
- No dead air > 3 s. Fill with a real next action, not a drift or a blinking caret.

**Beat grid:** `beatFrame(i) = round(i * fps * 60 / bpm)` — compute from the index, never accumulate rounded beats (drifts). Cut on the beat, change layout on the bar.

## Transitions with a cause

Use 3–5 kinds per video, each motivated by something on screen. At most ~⅓ of scene seams are hard cuts.

| Transition | Build |
|---|---|
| Zoom through a button | camera tracks to it (~18f), button scales 8%→250% in ~10f, strong ease-in; its fill becomes the next scene |
| Object becomes the world | a card grows past the frame (~20f), corner radius shrinking, surroundings blur 15px and fade |
| Morph | one container widens into the next in ~6f with horizontal blur 12→0 |
| Colour flood | hero stays, background colour changes in ~12f |
| Whip | 4–9f directional smear; arriving element lands blurred, sharpens in ~4f |
| Iris from the click | `clip-path: circle()` opens from the click point in ~5f |
| Dip cut | outgoing frame darkens ~40% for 3f, then hard cut |
| Blur swap | out: fade + 8px blur 4–6f; in: blur→0 4f; background never cuts |

Cut at the fastest frame of a move, matching direction and speed on both sides.

## Defaults that look generated — off unless the brand uses them

Dark navy void with small floating elements · glow, bloom, neon, lens flares, orbs, particles · purple/blue mesh gradients, glass cards · cream paper + serif + italic accent + "01 / 02" labels + mono caps chips · everything centred, fading in at once, sliding up · text moving while being read · breathing/pulsing loops as fake motion · bounce on UI, click rings · every scene entering the same way · corner brackets, HUD readouts · three cards in a row, KPI grids, title over a dimmed screenshot · logo docked in a corner.

When a scene shows one, name it and replace it with something taken from the subject, the brand or the medium (for a temple: textures of the actual place, real faces, real food, real light — not stock gold glows).
