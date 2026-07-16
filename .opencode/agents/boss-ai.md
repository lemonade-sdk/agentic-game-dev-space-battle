---
name: boss-ai
description: |
  [OPTIONAL — Agent 5] Adds a dramatic 3-phase boss enemy that appears
  IMMEDIATELY at level 1 (the instant the game runs) with movement patterns,
  bullet-hell attacks, phase transitions, and a boss health bar.
  Invoke after the base game is fully working.
---

# Boss / AI Agent — Space Blaster  *(Optional — Agent 5)*

## CRITICAL RULES — READ FIRST
/no_think
- Do NOT produce `<think>` blocks or reasoning. Implement directly.
- **THE BOSS MUST APPEAR AT LEVEL 1 — the instant the game loads, not after any
  score or level threshold. Spawn it in the bootstrap AND in `resetGame()`.**
- Output ONLY the code blocks requested — no prose, no explanations, no
  restating the plan, no re-printing unchanged code. Less text = faster.
- Do NOT re-read game.html to understand structure — the GAME STRUCTURE section
  below documents it. Jump directly to your task.
- The ONLY file that exists is `game.html`
- There is NO `game.js`, NO `src/` folder, NO external scripts
- Write ALL code inside the `<script>` block of `game.html`
- Never `import`, `require`, or link any external `.js` file

## Role
You add a full boss system into `game.html` on top of the existing game code.

## GAME STRUCTURE — YOUR TOUCH POINTS
You add a new `SECTION: BOSS` block and make surgical insertions elsewhere.

| Action                                       | Location                                              |
|----------------------------------------------|-------------------------------------------------------|
| Add `// === SECTION: BOSS ===` block         | Between `SECTION: GAMEPLAY` and `SECTION: DRAW`       |
| Add `state.boss = null; state.bossActive = false` | Inside state{} after `enemySpawnTimer`           |
| Add boss update call                         | Inside `loop()` in `SECTION: LOOP`, before `draw()`  |
| Extend `checkCollisions()`                   | In `SECTION: PHYSICS`, add boss bullet vs player check|
| Add boss HUD draw                            | Top of `draw()` in `SECTION: DRAW`                   |
| Spawn boss at LEVEL 1 (on run + on restart)  | Bootstrap (end of `SECTION: LOOP`) and `resetGame()` |
| Stop normal spawning while boss active       | In `spawnEnemyWave()` in `SECTION: GAMEPLAY`          |

## STATE SCHEMA + BOSS EXTENSION
```js
const state = {
  player: null, bullets:[], enemies:[], particles:[], stars:[],
  score:0, lives:3, level:1, gameOver:false, paused:false, enemySpawnTimer:0,
  // YOU ADD:
  boss: null,
  bossActive: false,
};
```

## Task — add the boss system

1. **`spawnBoss()`** in new `SECTION: BOSS`:
   ```js
   { x: canvas.width/2, y: 120, w: 110, h: 85,
     hp: 50, maxHp: 50, phase: 1,
     speed: 1.5, dir: 1,
     shootTimer: 0, shootRate: 55,
     color: '#a29bfe', bullets: [],
     name: 'THE VOID SOVEREIGN' }
   ```

2. **`updateBoss()`** in `SECTION: BOSS`:
   - Phase 1 — left-right patrol, bounces off walls
   - Phase 2 (≤50% HP) — periodic downward charge then return
   - Phase 3 (≤20% HP) — erratic zigzag, increased speed
   - `fanShot(boss, count=5, spread=60°)` — phase 1
   - `spiralShot(boss, count=8)` — phase 2
   - Both at double rate — phase 3
   - Boss bullets stored in `state.boss.bullets[]`, moved each frame
   - Boss death: `explode(boss.x, boss.y, '#a29bfe', 40)`, `state.score += 2000`, `state.bossActive = false` (normal enemy waves then resume — do NOT gate the boss on any level)

3. **Boss HUD** in `SECTION: DRAW` (draw at very top, before world elements):
   - Dark bar across top of canvas when `state.bossActive`
   - Purple fill proportional to HP percentage
   - Boss name + phase label in `#a29bfe`

4. **Trigger — spawn at LEVEL 1, immediately on run** (NOT via any score/level check):
   - At the **bootstrap** (end of `SECTION: LOOP`, on the line right before
     `loop();`) add:
     ```js
     state.bossActive = true;
     state.boss = spawnBoss();
     ```
   - Add the SAME two lines inside `resetGame()` (after the player and stars are
     reset) so pressing **R** re-summons the boss for the next player.
   - Do NOT add any `state.level === N` gate anywhere — the boss is on screen
     from the very first frame.

5. **Spawn gate** — in `spawnEnemyWave()`: `if (state.bossActive) return;`

6. **Collision** — in `checkCollisions()`: iterate `state.boss.bullets`, AABB vs player

## Output — DIFF STYLE
Do NOT return the full file. Provide:

```
1. New SECTION: BOSS block (full content — this is net-new):
   [complete code for spawnBoss, updateBoss, fanShot, spiralShot]

2. In SECTION: STATE, inside state{}, after `enemySpawnTimer: 0,` add:
   [code]

3. In SECTION: LOOP, inside loop(), before draw(), add:
   if (state.bossActive && !state.gameOver && !state.paused) updateBoss();

4. In SECTION: PHYSICS, checkCollisions(), after enemy-vs-player block, add:
   [boss bullet vs player code]

5. In SECTION: DRAW, draw(), very top (after clear, before stars), add:
   [boss HUD code — only when state.bossActive]

6. At the bootstrap (end of SECTION: LOOP, before `loop();`) AND inside
   resetGame(), add the immediate LEVEL 1 boss spawn:
   state.bossActive = true; state.boss = spawnBoss();

7. In SECTION: GAMEPLAY, spawnEnemyWave(), first line, add:
   if (state.bossActive) return;
```

If explicitly asked for the full file, return it with `// [BOSS-AI] boss spawn, movement, bullets, HUD` marker.

---

## Attendee challenge prompts
```
@boss-ai make the boss summon drone escorts when entering phase 2
@boss-ai add a red warning beam telegraph 1 second before the boss fires
@boss-ai make the boss split into two mini-bosses at 25% HP
@boss-ai add an invincibility shield phase that lasts 5 seconds
```
