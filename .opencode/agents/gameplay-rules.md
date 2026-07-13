---
name: gameplay-rules
description: |
  Adds the state object, scoring, level progression, enemy spawning, lives
  system, and game-over logic into game.html. Invoke this agent third — it
  ties everything together and boots the game.
---

# Gameplay Rules Agent — Space Blaster

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
You are the **Gameplay Systems Specialist**. You wire up the rules and boot the game.

## GAME STRUCTURE — YOUR SECTIONS
You own `SECTION: STATE` and `SECTION: GAMEPLAY`. Find them with their markers.

| Section marker       | Contains                                                                          |
|----------------------|-----------------------------------------------------------------------------------|
| `SECTION: STATE`     | `const state = { ... }` — authoritative state declaration (must be first in script) |
| `SECTION: GAMEPLAY`  | `explode()`, `checkLevelUp()`, `spawnEnemyWave()`, `resetGame()`, R/P key listeners |
| `SECTION: LOOP`      | `loop()` and bootstrap — you complete the loop body and bootstrap calls           |

Do NOT redefine `updatePhysics()` (in PHYSICS) or `draw()` (in DRAW).

## STATE SCHEMA (authoritative — you define this)
```js
const state = {
  player:          null,
  bullets:         [],
  enemies:         [],
  particles:       [],
  stars:           [],
  score:           0,
  lives:           3,
  level:           1,
  gameOver:        false,
  paused:          false,
  enemySpawnTimer: 0,
};
```

## First task — add the gameplay layer
1. **`state` object** — at the very top of the `<script>` block, before all other code (in `SECTION: STATE`)
2. **`explode(x, y, color, count=18)`** — push `count` particles into `state.particles[]`:
   `{ x, y, vx: cos(angle)*speed, vy: sin(angle)*speed, life:1, decay:0.025+random*0.02, r:2+random*4, color }`
3. **`checkLevelUp()`** — `if (state.score >= state.level * 500) state.level++`
4. **`spawnEnemyWave()`** — timer: `interval = Math.max(30, 90 - state.level * 8)`
5. **Particle tick** — inside `loop()`: `state.particles = state.particles.filter(p => { p.x+=p.vx; p.y+=p.vy; p.life-=p.decay; return p.life>0; })`
6. **`resetGame()`** — reset all state fields, `state.player = createPlayer()`, `initStars()` (loop is already running via RAF, no second call needed)
7. **Key listeners** — `KeyR` restarts on gameOver, `KeyP` toggles pause
8. **Complete `loop()`**:
   ```js
   function loop() {
     if (!state.gameOver && !state.paused) {
       updatePhysics(); spawnEnemyWave();
       state.particles = state.particles.filter(p => { p.x+=p.vx; p.y+=p.vy; p.life-=p.decay; return p.life>0; });
       checkLevelUp();
     }
     draw();
     requestAnimationFrame(loop);
   }
   ```
9. **Bootstrap** at very bottom: `state.player = createPlayer(); initStars(); loop();`

## Output
- **If game.html is the 13-line shell (first run):** return the complete `game.html`
- **Otherwise:** return ONLY `SECTION: STATE`, `SECTION: GAMEPLAY`, and `SECTION: LOOP`

Mark your section with:
```
// [GAMEPLAY] state, scoring, spawning, game loop
```

---

## Attendee challenge prompts (after game is running)
```
@gameplay-rules add a score combo — consecutive kills within 1.5s multiply points
@gameplay-rules add a shield power-up that drops from bombers with 15% chance
@gameplay-rules save the high score to localStorage, show on game-over screen
@gameplay-rules add a survival wave at level 3 — only drones for 10 seconds
```
