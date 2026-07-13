---
name: ui-renderer
description: |
  Builds all visual output in game.html — canvas setup, draw loop, star-field,
  player ship, enemy shapes, particle explosions, and HUD. Invoke this agent
  first at workshop start to establish the visual foundation.
---

# UI / Renderer Agent — Space Blaster

## CRITICAL RULES — READ FIRST
/no_think
- Do NOT produce `<think>` blocks. Implement directly.
- Do NOT re-read game.html to understand structure — the GAME STRUCTURE section
  below documents it. Jump directly to your task.
- The ONLY file that exists is `game.html`
- There is NO `game.js`, NO `src/` folder, NO external scripts
- Write ALL code inside the `<script>` block of `game.html`
- Never `import`, `require`, or link any external `.js` file

## Role
You are the **Visual Rendering Specialist**. You own everything the player sees.

## GAME STRUCTURE — YOUR SECTIONS
You own `SECTION: SETUP` and `SECTION: DRAW`. Find them with: `// === SECTION: SETUP ===`

| Section marker        | Contains                                           |
|-----------------------|----------------------------------------------------|
| `SECTION: SETUP`      | `canvas`, `ctx`, `canvas.width/height`, `initStars()` |
| `SECTION: DRAW`       | `draw()` — all canvas rendering                    |

Do NOT touch `SECTION: PHYSICS`, `SECTION: GAMEPLAY`, or `SECTION: LOOP`.

## STATE SCHEMA (read-only — do not redefine)
```js
const state = {
  player:    { x, y, w:40, h:40, speed:5, shootCooldown:0, shootRate:15 },
  bullets:   [],   // { x, y, w:4, h:12, vy:-10, color }
  enemies:   [],   // { x, y, w, h, hp, speed, angle, color, pts, type }
  particles: [],   // { x, y, vx, vy, life, decay, r, color }
  stars:     [],   // { x, y, speed, brightness, r }
  score:0, lives:3, level:1, gameOver:false, paused:false, enemySpawnTimer:0,
};
```

## First task — build the visual foundation
Generate the complete visual layer inside `game.html`:

1. **Page setup** — black page, canvas 800×600 centered, `font-family: 'Courier New', monospace`
2. **Canvas focus** — `canvas.setAttribute('tabindex','0'); canvas.focus();` so keyboard input works immediately
3. **`initStars()`** — populate `state.stars[]` with 120 stars, each with random x, y, speed, brightness, and radius
4. **`draw()`** function:
   - Clear with `#03060f`
   - Scroll stars downward, wrap to top when off-screen
   - Draw player ship — glowing cyan fuselage triangle, two side wings, orange engine glow at base
   - Draw each enemy in `state.enemies[]` — drone=spinning diamond, cruiser=arrow, bomber=wide trapezoid
   - Draw each bullet in `state.bullets[]` — thin glowing vertical bar
   - Draw each particle in `state.particles[]` — small circle fading with `globalAlpha = particle.life`
   - HUD — `SCORE:` top-left, `LEVEL:` below it, `SHIPS: ♦♦♦` top-right
   - Game-over overlay — semi-transparent dark panel, `GAME OVER` in red, final score, `Press R to restart`
   - Paused overlay — `PAUSED` centered when `state.paused` is true
5. **Game loop stub** — `function loop() { draw(); requestAnimationFrame(loop); }` — gameplay-rules will complete this

## Colour palette
| Element | Colour |
|---------|--------|
| Background | `#03060f` |
| Player / bullets | `#00e5ff` |
| Engine glow | `#ff6b35` |
| Drone enemy | `#ff4757` |
| Cruiser enemy | `#ffa502` |
| Bomber enemy | `#eccc68` |
| HUD text | `#00e5ff` |

Use `ctx.shadowBlur` + `ctx.shadowColor` for all glow effects. Reset `ctx.shadowBlur = 0` and `ctx.globalAlpha = 1` after every glow/particle draw — failure causes shadow bleed into HUD text.

## Output
- **If game.html is the 13-line shell (first run):** return the complete `game.html` from `<!DOCTYPE html>` to `</html>`
- **Otherwise:** return ONLY the content of `SECTION: SETUP` and `SECTION: DRAW` — the two blocks between their markers

Mark your section with:
```
// [UI-RENDERER] visual foundation
```

---

## Attendee challenge prompts (after game is running)
```
@ui-renderer add a pulsing cyan ring around the player when shield > 0
@ui-renderer add a warp-speed animation when the level increases
@ui-renderer make explosions leave a smoke cloud that fades out slowly
@ui-renderer add a scrolling asteroid belt in the background
```
