# 🚨 Critical Issues Discovered During Live Testing

**Date:** 2025-12-29, 12:35 PM
**Discovered By:** User gameplay observation + log analysis

---

## Issue #1: Context Propagation Broken (GAME-BREAKING)

### Problem
**"Every player thinks they are going first and aren't being clued into previous words"**

### Root Cause
Players are called in **PARALLEL** within each round (`batch_call` on engine.py:335).

**Current Flow:**
1. Round starts
2. Context built ONCE with clues from PREVIOUS rounds only
3. ALL players in THIS round called simultaneously
4. Each player sees SAME context (no current-round clues)
5. Everyone thinks they're first!

**Code Location:** `engine.py:304-338`
```python
# Line 312: Context built ONCE before parallel calls
context = GameContext(
    current_round=self.current_round,
    clues_so_far=self._get_clue_dicts()  # Only previous rounds!
)

# Line 335: ALL players called at once
responses = await self.openrouter.batch_call(requests, ...)
```

### Impact
- Imposters can't build on others' clues (critical strategy!)
- Prompts say "analyze previous clues" but there are none (in round 1)
- Breaks core game mechanic of sequential deduction
- Makes imposters too easy to spot (can't adapt)

### Solution Options

**Option A: Sequential Calling (Authentic Game Mechanic)**
```python
# Call players ONE AT A TIME
for player in self.players:
    context = GameContext(
        current_round=self.current_round,
        clues_so_far=self._get_clue_dicts()  # Updated after each player!
    )
    messages = player.build_clue_messages(context)
    response = await self.openrouter.call(messages, ...)

    # Process clue IMMEDIATELY
    self.all_clues.append(clue_record)  # Add to history

    # Next player sees this clue!
```

**Pros:**
- ✅ Authentic imposter game mechanic
- ✅ Imposters can adapt and blend
- ✅ Strategic depth increases
- ✅ Matches official game rules

**Cons:**
- ❌ Slower (sequential not parallel)
- ❌ 8 players × 3 rounds × 3s = ~72 seconds vs ~9 seconds

**Option B: Update Prompts (Keep Parallel)**
Change prompts to say "You're all giving clues simultaneously" and remove references to "previous clues in this round".

**Pros:**
- ✅ Fast (keeps parallel calling)
- ✅ Minimal code change

**Cons:**
- ❌ Less strategic (imposters can't adapt)
- ❌ Doesn't match official game rules
- ❌ Less fun to watch

### Recommendation
**Use Option A with OPTIMIZATION:**
- Call players sequentially WITHIN a round
- But call rounds in sequence (already doing this)
- Add small delay between players (0.5s) for drama
- Total time: ~8 players × 3s × 3 rounds = ~72 seconds (acceptable!)

---

## Issue #2: Pydantic Schema Incompatibility with GPT-4o

### Problem
GPT-4o (via Azure) rejects VoteResponse schema:
```
Invalid schema: 'required' must include every key in properties.
Extra required key 'reasoning_per_player' supplied.
```

### Root Cause
The VoteResponse schema has `reasoning_per_player` with `default={}`, which creates an inconsistency:
- Pydantic marks it as "not required" (has default)
- But OpenAI's JSON schema includes it in "required" array
- Azure/GPT rejects this as invalid

**Code Location:** `schemas.py:62-65`
```python
reasoning_per_player: Dict[str, str] = Field(
    description="Brief explanation for each suspected player",
    default={}  # ← This causes the issue
)
```

### Impact
- GPT-4o models completely fail during voting
- Gemini models also affected (Azure provider)
- Reduces to only Claude/Qwen for voting
- 100% failure rate for OpenAI models

### Solution
**Option 1:** Make it truly optional
```python
reasoning_per_player: Optional[Dict[str, str]] = Field(
    default=None,
    description="..."
)
```

**Option 2:** Make it required (remove default)
```python
reasoning_per_player: Dict[str, str] = Field(
    description="...",
    # No default - always required
)
```

**Recommendation:** Option 2 (required)
- Forces models to provide reasoning
- Better for observability
- Cleaner schema

---

## Issue #3: Some Models Hit Token Limits

### Problem
```
Could not parse response content as the length limit was reached
```

Observed on:
- Qwen 72B
- DeepSeek R1
- Several others

### Root Cause
`max_tokens=500` too small for verbose models.

Reasoning models (DeepSeek R1, etc.) use "chain of thought" and generate 1000+ tokens before the actual JSON response.

### Solution
```python
# In openrouter_sdk.py
max_tokens: int = 1500  # Increased from 500
```

Or model-specific limits:
```python
VERBOSE_MODELS = {'deepseek-r1', 'qwen-72b', 'nous-hermes'}
max_tokens = 1500 if model in VERBOSE_MODELS else 500
```

---

## Issue #4: JSON Truncation

### Problem
```
Invalid JSON: EOF while parsing an object at line 2
input_value='{\n'
```

Some models' responses are getting cut off mid-JSON.

### Root Cause
- Either max_tokens too low
- Or streaming artifact
- Or model actually returning incomplete JSON

### Solution
Add validation in sanitize_json_response():
```python
def sanitize_json_response(text: str) -> str:
    # ... existing cleanup ...

    # Validate it's complete JSON
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError as e:
        # Try to salvage partial JSON
        if 'EOF' in str(e):
            # Incomplete - try to close braces
            open_braces = text.count('{') - text.count('}')
            text += '}' * open_braces
            return text
        raise
```

---

## Priority Fixes

### P0 - CRITICAL (Game-breaking)
1. **Fix context propagation** → Make clue-giving sequential
2. **Fix VoteResponse schema** → Remove default from reasoning_per_player

### P1 - HIGH (Reduces model availability)
3. **Increase max_tokens** → Set to 1500 for verbose models
4. **Fix JSON truncation** → Add completion logic

### P2 - MEDIUM
5. Add better error messages to frontend when stream fails
6. Add model availability checking before game creation

---

**Next Steps:**
1. Implement P0 fixes immediately
2. Test with working model set
3. Verify LangSmith captures proper traces
4. Document expected vs actual behavior
