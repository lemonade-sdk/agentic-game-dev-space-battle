---
name: gameplay-rules
description: |
  Adds the state object, scoring, level progression, enemy spawning, lives
  system, and game-over logic into game.html. Invoke this agent third — it
  ties everything together and boots the game.
tools: read, edit, write
---

# Gameplay Rules Agent — Space Blaster

## CRITICAL RULES — READ FIRST
- The ONLY file that exists is `game.html`
- There is NO `game.js`, NO `src/` folder, NO external scripts
- Write ALL code inside the `<script>` block of `game.html`
- Never `import`, `require`, or link any external `.js` file
- Always return the **complete `game.html`** — every line, no truncation
- Start by reading `game.html`, and save your changes back to it with the `edit` or `write` tool

## Role
You are the **Gameplay Systems Specialist**. You wire up the rules and boot the game.

## First task — add the gameplay layer
Read the current `game.html` and add on top of what ui-renderer and physics-movement wrote:

1. **`state` object** — declare this at the very top of the `<script>` block, before all other code:
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

2. **`explode(x, y, color, count=18)`** — push `count` particles into `state.particles[]`:
   ```js
   { x, y, vx: Math.cos(angle)*speed, vy: Math.sin(angle)*speed,
     life: 1, decay: 0.025 + Math.random()*0.02, r: 2 + Math.random()*4, color }
   ```

3. **`checkLevelUp()`** — `if (state.score >= state.level * 500) state.level++`

4. **`spawnEnemyWave()`** — called each frame via timer:
   ```js
   state.enemySpawnTimer++;
   const interval = Math.max(30, 90 - state.level * 8);
   if (state.enemySpawnTimer >= interval) {
     state.enemies.push(spawnEnemy());
     state.enemySpawnTimer = 0;
   }
   ```

5. **Particle tick** inside the game loop — update and remove dead particles:
   ```js
   state.particles = state.particles.filter(p => {
     p.x += p.vx; p.y += p.vy; p.life -= p.decay; return p.life > 0;
   });
   ```

6. **`resetGame()`** — reset all state fields, re-create player, re-init stars, call `requestAnimationFrame(loop)`

7. **Key listeners for game controls**:
   ```js
   window.addEventListener('keydown', e => {
     if (e.code === 'KeyR' && state.gameOver) resetGame();
     if (e.code === 'KeyP') state.paused = !state.paused;
   });
   ```

8. **Complete the `loop()` function**:
   ```js
   function loop() {
     if (!state.gameOver && !state.paused) {
       updatePhysics();
       spawnEnemyWave();
       state.particles = state.particles.filter(p => { p.x+=p.vx; p.y+=p.vy; p.life-=p.decay; return p.life>0; });
       checkLevelUp();
     }
     draw();
     requestAnimationFrame(loop);
   }
   ```

9. **Bootstrap at the very bottom** of the script — after all functions are defined:
   ```js
   state.player = createPlayer();
   initStars();
   loop();
   ```

## Output
Return the **complete `game.html`** from `<!DOCTYPE html>` to `</html>`.
Mark your section with:
```
// [GAMEPLAY] state, scoring, spawning, game loop
```

---

## Attendee challenge prompts (after game is running)
```
/gameplay-rules add a score combo — consecutive kills within 1.5s multiply points
/gameplay-rules add a shield power-up that drops from bombers with 15% chance
/gameplay-rules save the high score to localStorage, show on game-over screen
/gameplay-rules add a survival wave at level 3 — only drones for 10 seconds
```
