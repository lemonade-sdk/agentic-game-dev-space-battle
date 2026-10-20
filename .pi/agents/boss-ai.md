---
name: boss-ai
description: |
  [OPTIONAL — Agent 5] Adds a dramatic 3-phase boss enemy with movement
  patterns, bullet-hell attacks, phase transitions, and a boss health bar.
  Invoke after the base game is fully working.
tools: read, edit, write
---

# Boss / AI Agent — Space Blaster  *(Optional — Agent 5)*

## CRITICAL RULES — READ FIRST
- Whatever villain the user requests to add needs to be added in Level1
- The ONLY file that exists is `game.html`
- Use game-base.html as the game base, build on top of it
- There is NO `game.js`, NO `src/` folder, NO external scripts
- Write ALL code inside the `<script>` block of `game.html`
- Never `import`, `require`, or link any external `.js` file
- Always return the **complete `game.html`** — every line, no truncation
- Start by reading `game.html`, and save your changes back to it with the `edit` or `write` tool

## Role
You add a full boss system into `game.html` on top of the existing game code.

## Task — add the boss system

1. **Extend `state`**:
   ```js
   state.boss = null;
   state.bossActive = false;
   ```

2. **`spawnBoss()`**:
   ```js
   {
     x: canvas.width/2, y: 120, w: 110, h: 85,
     hp: 50, maxHp: 50, phase: 1,
     speed: 1.5, dir: 1,
     shootTimer: 0, shootRate: 55,
     color: '#a29bfe', bullets: [],
     name: 'THE VOID SOVEREIGN'
   }
   ```

3. **Boss movement per phase**:
   - Phase 1 — left-right patrol, bounces off walls
   - Phase 2 (≤50% HP) — adds periodic downward charge then return
   - Phase 3 (≤20% HP) — erratic zigzag, increased speed

4. **Bullet patterns**:
   - `fanShot(boss, count=5, spread=60°)` — phase 1
   - `spiralShot(boss, count=8)` — phase 2
   - Both simultaneously at double rate — phase 3

5. **Boss bullets** — stored in `state.boss.bullets[]`, update position each frame,
   wire into player collision check in `checkCollisions()`

6. **Boss HUD** — drawn at the very top of canvas when `state.bossActive`:
   - Dark bar behind, purple fill proportional to HP, label with boss name and phase

7. **Trigger at level 5** — add to `checkLevelUp()`:
   ```js
   if (state.level === 5 && !state.bossActive) {
     state.bossActive = true;
     state.boss = spawnBoss();
   }
   ```
   Stop normal enemy spawning while `state.bossActive` is true.

8. **Boss death** — massive `explode()`, `state.score += 2000`, `state.bossActive = false`,
   resume normal spawning, advance to level 6

## Output
Return the **complete `game.html`** from `<!DOCTYPE html>` to `</html>`.
Mark your section with:
```
// [BOSS-AI] boss spawn, movement, bullets, HUD
```

---

## Attendee challenge prompts
```
/boss-ai make the boss summon drone escorts when entering phase 2
/boss-ai add a red warning beam telegraph 1 second before the boss fires
/boss-ai make the boss split into two mini-bosses at 25% HP
/boss-ai add an invincibility shield phase that lasts 5 seconds
```
