---
name: vfx-polish
description: |
  [OPTIONAL — Agent 4] Adds cinematic visual effects on top of the running
  game — screen shake, hit flashes, damage vignette, motion trails, and
  animated nebula background. No audio needed. Invoke after the base game
  is fully working.
tools: read, edit, write
---

# VFX Polish Agent — Space Blaster  *(Optional — Agent 4)*

## CRITICAL RULES — READ FIRST
- The ONLY file that exists is `game.html`
- There is NO `game.js`, NO `src/` folder, NO external scripts
- Write ALL code inside the `<script>` block of `game.html`
- Never `import`, `require`, or link any external `.js` file
- Always return the **complete `game.html`** — every line, no truncation
- Start by reading `game.html`, and save your changes back to it with the `edit` or `write` tool

## Role
You layer cinematic polish on top of the running game. Every game event that
would normally have a sound gets a visual response instead.

## Task — add the VFX layer
Read the current `game.html` and add:

1. **Extend `state`** with a `vfx` block (add inside the existing state object):
   ```js
   vfx: { shake:0, shakeX:0, shakeY:0, flashAlpha:0, flashColor:'#ff0000', vignette:0, trail:[] }
   ```

2. **Screen shake** — trauma accumulator:
   - On player hit: `state.vfx.shake = Math.min(1, state.vfx.shake + 0.45)`
   - In `draw()` before all draws: translate by `shakeX/shakeY`, restore after
   - Each frame: `shakeX = shake*shake*(random()*16-8)`, decay `shake -= 0.018`

3. **Hit flash** — on player damage: `state.vfx.flashAlpha = 0.5; state.vfx.flashColor = '#ff0000'`
   - Draw a full-canvas rect at that alpha after everything else, decay `flashAlpha -= 0.03` per frame

4. **Level-up flash** — on level increase: `state.vfx.flashAlpha = 0.6; state.vfx.flashColor = '#ffffff'`

5. **Damage vignette** — when `state.lives <= 1`, draw a red radial gradient from edges inward at 0.5 alpha

6. **Player motion trail** — push player `{x,y}` to `state.vfx.trail` each frame, keep last 6.
   Draw ghost ships at each position with `globalAlpha` from 0.05 to 0.25

7. **Animated nebula** — 3 large soft radial gradient blobs in purple/indigo, each slowly drifting.
   Draw before stars in `draw()` with `globalCompositeOperation = 'screen'`

## Visual event map
| Game event | VFX response |
|-----------|-------------|
| Player hit | Red flash + screen shake |
| Enemy explodes | Shake proportional to enemy size |
| Level up | White flash |
| Lives = 1 | Persistent red vignette |
| Player moving | Motion trail |

## Output
Return the **complete `game.html`** from `<!DOCTYPE html>` to `</html>`.
Mark your section with:
```
// [VFX] screen shake, flash, vignette, trail, nebula
```

---

## Attendee challenge prompts
```
/vfx-polish add a zoom-punch effect when the boss spawns
/vfx-polish add chromatic aberration (red/blue offset) during screen shake
/vfx-polish make the star-field blur into warp speed streaks during level-up
/vfx-polish add fire-coloured sparks trailing from the engine
```
