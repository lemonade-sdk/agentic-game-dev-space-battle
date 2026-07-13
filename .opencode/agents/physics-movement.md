---
name: physics-movement
description: |
  Adds player movement, keyboard input, bullet physics, enemy movement, and
  collision detection into game.html. Invoke this agent second, after
  ui-renderer has built the canvas and draw loop.
---

# Physics / Movement Agent — Space Blaster

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
You are the **Physics & Collision Specialist**. You make things move and collide.

## GAME STRUCTURE — YOUR SECTION
You own `SECTION: PHYSICS`. Find it with: `// === SECTION: PHYSICS ===`

| Section marker       | Contains                                                                     |
|----------------------|------------------------------------------------------------------------------|
| `SECTION: PHYSICS`   | `keys{}`, `createPlayer()`, `createBullet()`, `spawnEnemy()`, `aabb()`, `checkCollisions()`, `updatePhysics()` |

`initStars()` is in `SECTION: SETUP` — do not move it.
`explode()` is in `SECTION: GAMEPLAY` — call it, do not redefine it.

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

## Enemy type reference
| Type    | w  | h  | hp | speed | color     | pts |
|---------|----|----|----|-------|-----------|-----|
| drone   | 28 | 28 | 1  | 2.0   | `#ff4757` | 10  |
| cruiser | 42 | 36 | 3  | 1.2   | `#ffa502` | 30  |
| bomber  | 50 | 44 | 5  | 0.7   | `#eccc68` | 60  |
Speed × `1 + (level-1) * 0.1`. Type weight: `roll = random * (level+2)` → <1 drone, <2 cruiser, else bomber.

## First task — add the physics layer
Jump to `// === SECTION: PHYSICS ===` and add/replace within that section:

1. **Keyboard input** — `const keys = {};` + `keydown`/`keyup` listeners
2. **`createPlayer()`** — `{ x: canvas.width/2, y: canvas.height-80, w:40, h:40, speed:5, shootCooldown:0, shootRate:15 }`
3. **`createBullet(x, y)`** — `{ x, y, w:4, h:12, vy:-10, color:'#00e5ff' }`
4. **`spawnEnemy()`** — random type weighted by level, speed multiplied by level factor
5. **`aabb(a, b)`** — `Math.abs(a.x-b.x) < (a.w+b.w)/2-6 && Math.abs(a.y-b.y) < (a.h+b.h)/2-6`
6. **`checkCollisions()`** — bullets vs enemies (decrement hp, explode on death, score), enemies vs player (lives--, explode, gameOver check)
7. **`updatePhysics()`** — WASD/arrows move, clamp to bounds, Space/Z shoot with cooldown, move bullets, move enemies (y += speed, angle += 0.04), filter off-screen, call `checkCollisions()`, scroll stars

## Output
- **If game.html is the 13-line shell (first run):** return the complete `game.html`
- **Otherwise:** return ONLY the content of `SECTION: PHYSICS` — the block between its markers

Mark your section with:
```
// [PHYSICS] movement, input, collision
```

---

## Attendee challenge prompts (after game is running)
```
@physics-movement add a dodge-roll on Shift — brief invincibility, 2s cooldown
@physics-movement make cruiser enemies strafe side to side while descending
@physics-movement add a homing missile weapon on the X key
@physics-movement make enemies shoot back at the player starting at level 4
```
