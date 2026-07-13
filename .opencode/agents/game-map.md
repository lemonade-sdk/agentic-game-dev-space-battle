# game.html — Live Code Map

> Use **section markers** as primary navigation — search for `// === SECTION: <NAME> ===`.
> Line numbers are approximate and may drift after agent edits. Update this file after each agent pass.

## Section Index

| Section marker          | Approx line | Functions / contents                                         |
|-------------------------|-------------|--------------------------------------------------------------|
| `SECTION: STATE`        | 16          | `const state = { ... }` — single authoritative state object |
| `SECTION: SETUP`        | 31          | `canvas`, `ctx`, `canvas.width/height`, `initStars()`       |
| `SECTION: PHYSICS`      | 52          | `keys{}`, `createPlayer()`, `createBullet()`, `spawnEnemy()`, `aabb()`, `checkCollisions()`, `updatePhysics()` |
| `SECTION: GAMEPLAY`     | 162         | `explode()`, `checkLevelUp()`, `spawnEnemyWave()`, `resetGame()`, R/P key listeners |
| `SECTION: DRAW`         | 211         | `draw()` — all canvas rendering: stars, enemies, player, bullets, particles, HUD, overlays |
| `SECTION: LOOP`         | 359         | `loop()`, bootstrap (`createPlayer`, `initStars`, `loop`)   |

## Canonical State Schema

```js
const state = {
  player:          { x, y, w:40, h:40, speed:5, shootCooldown:0, shootRate:15 },
  bullets:         [],   // { x, y, w:4, h:12, vy:-10, color }
  enemies:         [],   // { x, y, w, h, hp, speed, angle, color, pts, type }
  particles:       [],   // { x, y, vx, vy, life, decay, r, color }
  stars:           [],   // { x, y, speed, brightness, r }
  score:           0,
  lives:           3,
  level:           1,
  gameOver:        false,
  paused:          false,
  enemySpawnTimer: 0,
};
```

## Function Quick Reference

| Function               | Section    | Signature / notes                                               |
|------------------------|------------|-----------------------------------------------------------------|
| `initStars()`          | SETUP      | Populates `state.stars[]` with 120 stars                        |
| `createPlayer()`       | PHYSICS    | Returns player object, positioned at bottom-center              |
| `createBullet(x, y)`   | PHYSICS    | Returns bullet `{ x, y, w:4, h:12, vy:-10, color:'#00e5ff' }`  |
| `spawnEnemy()`         | PHYSICS    | Returns one enemy (drone/cruiser/bomber) weighted by level      |
| `aabb(a, b)`           | PHYSICS    | Collision test — returns bool                                   |
| `checkCollisions()`    | PHYSICS    | bullets-vs-enemies + enemies-vs-player, calls `explode()`       |
| `updatePhysics()`      | PHYSICS    | Input, movement, shooting, off-screen cleanup, calls `checkCollisions()` |
| `explode(x,y,color,n)` | GAMEPLAY   | Pushes `n` (default 18) particles into `state.particles[]`     |
| `checkLevelUp()`       | GAMEPLAY   | `if (score >= level * 500) level++`                             |
| `spawnEnemyWave()`     | GAMEPLAY   | Timer-based spawning: interval = `max(30, 90 - level*8)`       |
| `resetGame()`          | GAMEPLAY   | Resets all state, recreates player, re-inits stars              |
| `draw()`               | DRAW       | Full canvas render every frame                                  |
| `loop()`               | LOOP       | RAF loop — calls update → spawn → particles → levelup → draw   |

## Color Palette

| Element         | Color      |
|-----------------|------------|
| Background      | `#03060f`  |
| Player/bullets  | `#00e5ff`  |
| Engine glow     | `#ff6b35`  |
| Drone enemy     | `#ff4757`  |
| Cruiser enemy   | `#ffa502`  |
| Bomber enemy    | `#eccc68`  |
| HUD text        | `#00e5ff`  |

## Enemy Type Reference

| Type    | w  | h  | hp | speed | color     | pts |
|---------|----|----|----|-------|-----------|-----|
| drone   | 28 | 28 | 1  | 2.0   | `#ff4757` | 10  |
| cruiser | 42 | 36 | 3  | 1.2   | `#ffa502` | 30  |
| bomber  | 50 | 44 | 5  | 0.7   | `#eccc68` | 60  |

Speed multiplied by `1 + (level - 1) * 0.1` at spawn time.

## Draw Hygiene Rule

Always reset after glow/particle draws:
```js
ctx.shadowBlur = 0;
ctx.globalAlpha = 1;
```
Failure causes shadow bleed into HUD text.
