# Efficiency Analysis Report

## Overview

This report identifies several areas in the codebase where efficiency improvements could be made. The analysis covers both the Python backend (AI game simulation) and the frontend (React/TypeScript).

---

## Issue 1: Repeated List Comprehensions in `_calculate_results()` (HIGH IMPACT)

**Location:** `ai_game_simulation/src/game_engine/engine.py`, lines 567-582

**Problem:** The `_calculate_results()` method iterates over `self.players` multiple times with similar list comprehensions to extract the same data:

```python
# Line 567-571: First iteration to get actual_imposters
actual_imposters = [
    p.player_id
    for p in self.players
    if p.role == PlayerRole.IMPOSTER
]

# Line 578-582: Second iteration in check_win_condition call
win_check = check_win_condition(
    eliminated_players=all_eliminated,
    all_imposters=actual_imposters,
    remaining_players=[p.player_id for p in self.players if p.player_id not in all_eliminated],
    num_civilians=len([p for p in self.players if p.role == PlayerRole.NON_IMPOSTER])
)
```

**Impact:** With 8+ players, this creates 3 separate iterations over the player list when one would suffice. While not critical for small games, this pattern is inefficient.

**Recommended Fix:** Extract all needed data in a single pass:

```python
# Single pass extraction
actual_imposters = []
non_imposter_count = 0
remaining_players = []

for p in self.players:
    if p.role == PlayerRole.IMPOSTER:
        actual_imposters.append(p.player_id)
    else:
        non_imposter_count += 1
    
    if p.player_id not in all_eliminated:
        remaining_players.append(p.player_id)
```

---

## Issue 2: New `aiohttp.ClientSession` Created Per Request (MEDIUM IMPACT)

**Location:** `ai_game_simulation/src/ai/openrouter.py`, lines 108-115

**Problem:** The legacy OpenRouter client creates a new `aiohttp.ClientSession` for every single API call:

```python
for attempt in range(3):
    try:
        async with aiohttp.ClientSession() as session:  # New session each call!
            async with session.post(...) as response:
                ...
```

**Impact:** Creating a new session for each request adds overhead from TCP connection establishment, TLS handshake, and connection pool setup. With 8 players making multiple API calls per game, this adds significant latency.

**Recommended Fix:** Create the session once in `__init__` and reuse it:

```python
def __init__(self, ...):
    self.session = None

async def _get_session(self):
    if self.session is None or self.session.closed:
        self.session = aiohttp.ClientSession()
    return self.session

async def call(self, ...):
    session = await self._get_session()
    async with session.post(...) as response:
        ...
```

Note: The SDK client (`openrouter_sdk.py`) already handles this correctly via the OpenAI SDK.

---

## Issue 3: Redundant `_get_clue_dicts()` Calls (MEDIUM IMPACT)

**Location:** `ai_game_simulation/src/game_engine/engine.py`, lines 317 and 444

**Problem:** The `_get_clue_dicts()` method is called multiple times during a game, and each call creates new dictionary objects from the same data:

```python
# In _execute_clue_round (line 317)
context = GameContext(
    current_round=self.current_round,
    clues_so_far=self._get_clue_dicts()  # Called for each player
)

# In _execute_voting (line 444)
messages = player.build_voting_messages(
    all_clues=self._get_clue_dicts(),  # Called for each player
    word=self.config.word
)
```

**Impact:** For 8 players over 3 rounds, this creates 24+ redundant list comprehensions and dictionary creations during clue rounds, plus 8 more during voting.

**Recommended Fix:** Cache the result and only regenerate when clues are added:

```python
def __init__(self, ...):
    self._clue_dicts_cache = None
    self._clue_dicts_valid = False

def _invalidate_clue_cache(self):
    self._clue_dicts_valid = False

def _get_clue_dicts(self) -> List[Dict]:
    if not self._clue_dicts_valid:
        self._clue_dicts_cache = [
            {"round": c.round, "player_id": c.player_id, "clue": c.clue}
            for c in self.all_clues
        ]
        self._clue_dicts_valid = True
    return self._clue_dicts_cache
```

---

## Issue 4: Frontend Event Array Grows Unbounded (LOW IMPACT)

**Location:** `ai_game_simulation/frontend/src/hooks/useGameStream.ts`, line 52

**Problem:** Events are appended to an array that grows throughout the game:

```typescript
eventSource.onmessage = (event) => {
    const gameEvent: GameEvent = JSON.parse(event.data);
    setEventQueue(prev => [...prev, gameEvent]);  // Creates new array each time
};
```

**Impact:** Each new event creates a copy of the entire event array. For games with many events, this causes O(n^2) memory operations.

**Recommended Fix:** Use a more efficient update pattern or limit event history:

```typescript
// Option 1: Use functional update that doesn't spread
setEventQueue(prev => {
    prev.push(gameEvent);
    return prev;
});

// Option 2: Limit history size
const MAX_EVENTS = 500;
setEventQueue(prev => {
    const newQueue = [...prev, gameEvent];
    return newQueue.length > MAX_EVENTS ? newQueue.slice(-MAX_EVENTS) : newQueue;
});
```

---

## Issue 5: Duplicate Model Registry Definitions (CODE QUALITY)

**Location:** 
- `ai_game_simulation/src/ai/openrouter_sdk.py`, lines 185-307
- `ai_game_simulation/src/ai/openrouter.py`, lines 206-228

**Problem:** The `AVAILABLE_MODELS` dictionary is defined in both files with different content. This creates maintenance burden and potential inconsistencies.

**Impact:** When adding new models, developers must update both files. The legacy client has outdated model information.

**Recommended Fix:** Create a single `models.py` file with the canonical model registry and import it in both clients.

---

## Issue 6: Synchronous Database Operations in Async Context (LOW IMPACT)

**Location:** `ai_game_simulation/src/api/main.py`, lines 264-286

**Problem:** The `list_games` endpoint uses synchronous SQLite operations in an async function:

```python
@app.get("/api/games/list")
async def list_games(limit: int = 10):
    conn = sqlite3.connect("./data/games.db")  # Blocking!
    cursor = conn.cursor()
    cursor.execute(...)  # Blocking!
```

**Impact:** Synchronous database calls block the event loop, preventing other async operations from running. This can cause latency spikes under load.

**Recommended Fix:** Use `aiosqlite` for async database operations or run in a thread pool:

```python
import aiosqlite

async def list_games(limit: int = 10):
    async with aiosqlite.connect("./data/games.db") as conn:
        cursor = await conn.execute(...)
        rows = await cursor.fetchall()
```

---

## Summary

| Issue | Impact | Complexity to Fix |
|-------|--------|-------------------|
| 1. Repeated list comprehensions in `_calculate_results()` | High | Low |
| 2. New aiohttp session per request | Medium | Medium |
| 3. Redundant `_get_clue_dicts()` calls | Medium | Low |
| 4. Frontend event array growth | Low | Low |
| 5. Duplicate model registry | Code Quality | Low |
| 6. Sync DB in async context | Low | Medium |

## Recommendation

Start with **Issue 1** (repeated list comprehensions) as it has high impact and low complexity. This change will make the results calculation more efficient and serves as a good example of the optimization pattern that can be applied elsewhere in the codebase.
