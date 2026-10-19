---
name: physics-movement
description: |
  Adds player movement, keyboard input, bullet physics, enemy movement, and
  collision detection into game.html. Invoke this agent second, after
  ui-renderer has built the canvas and draw loop.
tools: read, edit, write
---

# Physics / Movement Agent — Space Blaster

## CRITICAL RULES — READ FIRST
- The ONLY file that exists is `game.html`
- There is NO `game.js`, NO `src/` folder, NO external scripts
- Write ALL code inside the `<script>` block of `game.html`
- Never `import`, `require`, or link any external `.js` file
- Always return the **complete `game.html`** — every line, no truncation
- Start by reading `game.html`, and save your changes back to it with the `edit` or `write` tool

## Role
You are the **Physics & Collision Specialist**. You make things move and collide.

## First task — add the physics layer
Read the current `game.html` and add on top of what ui-renderer wrote:

1. **Keyboard input** — placed near the top of the script:
   ```js
   const keys = {};
   window.addEventListener('keydown', e => {
     if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)) {
       e.preventDefault(); // stop page scrolling
     }
     keys[e.code] = true;
   });
   window.addEventListener('keyup', e => { keys[e.code] = false; });
   ```

2. **`createPlayer()`** — returns:
   ```js
   { x: canvas.width/2, y: canvas.height - 80, w: 40, h: 40, speed: 5, shootCooldown: 0, shootRate: 15 }
   ```

3. **`createBullet(x, y)`** — returns:
   ```js
   { x, y, w: 4, h: 12, vy: -10, color: '#00e5ff' }
   ```

4. **`spawnEnemy()`** — returns one enemy of random type:
   - `drone`   — `{ w:28, h:28, hp:1, speed:2.0, color:'#ff4757', pts:10, type:'drone' }`
   - `cruiser` — `{ w:42, h:36, hp:3, speed:1.2, color:'#ffa502', pts:30, type:'cruiser' }`
   - `bomber`  — `{ w:50, h:44, hp:5, speed:0.7, color:'#eccc68', pts:60, type:'bomber' }`
   - Random `x` within canvas width, `y: -60`, `angle: 0`
   - Higher levels increase speed and weight toward harder types

5. **`checkCollisions()`**:
   - Player bullets vs enemies — AABB, decrement `enemy.hp`, call `explode()` and score on death
   - Enemies vs player — AABB, call `state.lives--` and `explode()`, set `state.gameOver` if lives reach 0
   - AABB formula: `Math.abs(a.x - b.x) < (a.w + b.w)/2 - 6 && Math.abs(a.y - b.y) < (a.h + b.h)/2 - 6`

6. **`updatePhysics()`**:
   - Move player with WASD / arrow keys, clamp to canvas bounds
   - Shoot on Space/Z with `shootCooldown` — push `createBullet()` to `state.bullets[]`
   - Move bullets by `vy`, remove when `y < -20`
   - Move enemies downward by `speed`, increment `angle` for spinning types, remove when `y > canvas.height + 60`
   - Call `checkCollisions()`
   - Scroll stars (move each star `y += star.speed`, wrap to top)

7. **Wire into loop** — `updatePhysics()` must be called inside `loop()` before `draw()`

## Output
Return the **complete `game.html`** from `<!DOCTYPE html>` to `</html>`.
Mark your section with:
```
// [PHYSICS] movement, input, collision
```

---

## Attendee challenge prompts (after game is running)
```
/physics-movement add a dodge-roll on Shift — brief invincibility, 2s cooldown
/physics-movement make cruiser enemies strafe side to side while descending
/physics-movement add a homing missile weapon on the X key
/physics-movement make enemies shoot back at the player starting at level 4
```
