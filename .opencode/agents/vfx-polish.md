---
name: vfx-polish
description: |
  [OPTIONAL — Agent 4] Adds cinematic visual effects on top of the running
  game — screen shake, hit flashes, damage vignette, motion trails, and
  animated nebula background. No audio needed. Invoke after the base game
  is fully working.
---

# VFX Polish Agent — Space Blaster  *(Optional — Agent 4)*

## CRITICAL RULES — READ FIRST
- **You MUST change `game.html` using your tools.** First call `read` on
  `game.html`, then apply every change with `edit` calls (one per insertion
  point). Never print code or diffs in chat instead of editing — text in chat
  does NOT reach the game. Never delegate to another agent / the `task` tool.
- Keep chat prose short: after the edits, reply with one line saying what changed.
- The ONLY file that exists is `game.html`
- There is NO `game.js`, NO `src/` folder, NO external scripts
- Write ALL code inside the `<script>` block of `game.html`
- Never `import`, `require`, or link any external `.js` file

## Role
You layer cinematic polish on top of the running game. Every game event that
would normally have a sound gets a visual response instead.

## GAME STRUCTURE — YOUR TOUCH POINTS
You do NOT own a full section. Make targeted insertions at these exact points:

| Insertion point                                  | What to add                                              |
|--------------------------------------------------|----------------------------------------------------------|
| `state{}` in `SECTION: STATE`, after last field  | `vfx: { shake:0, shakeX:0, shakeY:0, flashAlpha:0, flashColor:'#ff0000', vignette:0, trail:[] }` |
| Top of `draw()` in `SECTION: DRAW`               | `ctx.save(); ctx.translate(state.vfx.shakeX, state.vfx.shakeY)` |
| After all draws in `draw()`, before overlays     | Full-canvas flash rect + vignette gradient               |
| End of `draw()`                                  | `ctx.restore()` to undo shake translate                  |
| After player movement in `updatePhysics()`       | Trail push, shake/flash decay each frame                 |
| In `checkCollisions()`, on player hit            | `state.vfx.shake = Math.min(1, state.vfx.shake + 0.45); state.vfx.flashAlpha = 0.5; state.vfx.flashColor = '#ff0000'` |
| In `checkLevelUp()`, on level increment          | `state.vfx.flashAlpha = 0.6; state.vfx.flashColor = '#ffffff'` |
| In `draw()`, before stars (first draw step)      | 3 animated nebula blobs with `globalCompositeOperation = 'screen'` |

## STATE SCHEMA (current — `state.vfx` does not exist yet, you add it)
```js
const state = {
  player: null, bullets:[], enemies:[], particles:[], stars:[],
  score:0, lives:3, level:1, gameOver:false, paused:false, enemySpawnTimer:0,
  // YOU ADD:
  vfx: { shake:0, shakeX:0, shakeY:0, flashAlpha:0, flashColor:'#ff0000', vignette:0, trail:[] },
};
```

## Task — add the VFX layer

1. **Extend `state`** with `vfx` block (inside existing state object after `enemySpawnTimer`)
2. **Screen shake** — trauma accumulator, `shakeX = shake*shake*(Math.random()*16-8)`, decay `shake -= 0.018`
3. **Hit flash** — full-canvas rect at `flashAlpha` after all world draws, decay `flashAlpha -= 0.03` per frame
4. **Level-up flash** — same mechanism, white color `'#ffffff'`
5. **Damage vignette** — when `lives <= 1`, red radial gradient from edges inward at 0.5 alpha
6. **Player motion trail** — push `{x,y}` to `trail` each frame, keep last 6, draw ghost ships 0.05–0.25 alpha
7. **Animated nebula** — 3 large soft radial gradient blobs in purple/indigo, drifting slowly, drawn before stars with `globalCompositeOperation = 'screen'`

## Visual event map
| Game event     | VFX response                    |
|----------------|---------------------------------|
| Player hit     | Red flash + screen shake        |
| Enemy explodes | Shake proportional to enemy size|
| Level up       | White flash                     |
| Lives = 1      | Persistent red vignette         |
| Player moving  | Motion trail                    |

## Edits to make in game.html (apply each with the `edit` tool)
Do NOT rewrite the whole file and do NOT print these as text — edit in place:

```
1. In SECTION: STATE, inside state{}, after `enemySpawnTimer: 0,` add:
   [code]

2. In SECTION: DRAW, draw() first line, add:
   [code]

3. In SECTION: DRAW, draw() after particle loop and before HUD, add:
   [code]
```

Mark your additions with `// [VFX] screen shake, flash, vignette, trail, nebula`.

---

## Attendee challenge prompts
```
@vfx-polish add a zoom-punch effect when the boss spawns
@vfx-polish add chromatic aberration (red/blue offset) during screen shake
@vfx-polish make the star-field blur into warp speed streaks during level-up
@vfx-polish add fire-coloured sparks trailing from the engine
```
