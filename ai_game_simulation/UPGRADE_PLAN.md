# 🎭 Imposter Experiment - Upgrade Plan
**Created:** 2025-12-29
**Focus:** Human-realistic gameplay with authentic social dynamics

---

## 🎯 Vision: Authentic Social Deduction Experience

**Core Principle:** Make AI agents behave like real people playing the game at a table
- Natural conversation flow
- Emotional reactions (surprise, suspicion, defense)
- Group psychology and social pressure
- Dramatic reveals and tension

---

## Phase 1: Essential UX Improvements (P0)

### 1.1 Visual Imposter Identification
**Problem:** After game ends, unclear who imposters were

**Solution:**
- During game: All players look identical (maintain mystery)
- After voting: Highlight eliminated player(s)
- On game_complete: Reveal imposters with animation
  - Imposters get 🎭 mask overlay
  - Border turns red
  - "IMPOSTER REVEALED" badge

**Human Empathy:**
- Dramatic reveal mimics in-person "oooh!" moment
- Visual contrast creates emotional payoff
- Players who voted correctly feel validated

**Files to modify:**
- `PlayerCircle.css` - Add .imposter-revealed class
- `PlayerCircle.tsx` - Conditional styling based on game result
- `App.tsx` - Pass result state to PlayerCircle

---

### 1.2 Enhanced Clue & Monologue Display
**Problem:** Hard to track who said what, when

**Solution:**
- **Clear speaker identification:**
  - Avatar highlight when speaking
  - Speech bubble pointing to player
  - Player name + role badge (revealed post-game)

- **Clue display improvements:**
  - Larger text for clue word
  - Subtle pulse animation when new clue appears
  - Timeline view showing clue progression

- **Internal monologue enhancements:**
  - "Thought bubble" UI vs "speech bubble" for clues
  - Fade in/out with player highlighting
  - Confidence meter visualization (0-100%)

**Human Empathy:**
- Mimics "watching over someone's shoulder" feeling
- Clear attribution prevents confusion
- Confidence visualization adds tension ("They're 90% sure!")

**Files to modify:**
- `ClueDisplay.tsx` - Add speech bubble UI
- `InnerMonologue.tsx` - Add thought bubble styling
- `PlayerCircle.tsx` - Add pulse/highlight on active speaker
- `App.css` - Animations and visual hierarchy

---

## Phase 2: Post-Game Discussion (P1)

### 2.1 Popcorn Discussion Implementation
**THE BIG ONE:** 10+ back-and-forth group conversation after voting

**Flow:**
1. Voting completes → results shown
2. Word revealed to all
3. **Discussion phase begins (NEW!)**
4. Players "speak" in natural order:
   - Reactions to results
   - Defend their clues
   - Call out suspicious behavior
   - Celebrate or lament

**Example Exchange:**
```
Player_1: "I can't believe you all voted me out! My 'anxiety' clue was perfect for 'test'!"

Player_3 (revealed imposter): "Honestly, I thought I nailed it with 'timed'. How did you not catch me?"

Player_2: "Player_3, your second clue 'proctor' was too specific - that's what made me suspicious."

Player_4: "Wait, Player_1's clue WAS good. I think we messed up. Player_8's 'parking' made no sense though."

Player_8: "Parking was about beach parking! You all focused on ocean but beach has parking lots!"
```

**Human Empathy:**
- Mimics real post-game table talk
- Defensiveness, pride, regret - real emotions
- Group bonding through shared analysis
- "Aha!" moments when patterns click

**Technical Implementation:**

```python
# New phase in GamePhase enum
class GamePhase(Enum):
    ...
    VOTING = auto()
    POST_DISCUSSION = auto()  # NEW
    REVEAL = auto()

# New prompt in prompts.py
def build_post_discussion_prompt(
    player_id: str,
    role: PlayerRole,
    word: str,
    my_clues: List[str],
    eliminated_players: List[str],
    was_i_eliminated: bool,
    actual_imposters: List[str],
    all_votes: Dict[str, List[str]],  # Who voted for who
    discussion_so_far: List[Dict]  # Previous discussion messages
) -> str:
    """
    Build post-game discussion prompt.

    Creates natural reactions based on:
    - Whether they were caught
    - Whether they voted correctly
    - What others are saying
    """

    if role == PlayerRole.IMPOSTER:
        if was_i_eliminated:
            tone = "defensive but impressed"
            prompt_focus = "Explain your strategy, acknowledge good detective work"
        else:
            tone = "proud but humble"
            prompt_focus = "Share how you pulled it off, compliment clever clues"
    else:  # Non-imposter
        if was_i_eliminated:
            tone = "frustrated but understanding"
            prompt_focus = "Defend your clues, point out actual imposters"
        else:
            tone = "analytical"
            prompt_focus = "Explain voting logic, discuss what you noticed"

    return f"""=== POST-GAME DISCUSSION ===

The secret word was: "{word}"
The imposters were: {actual_imposters}
You were: {"CAUGHT" if was_i_eliminated else "SAFE"}

Previous discussion:
{format_discussion(discussion_so_far)}

YOUR TURN: React naturally to the results and others' comments.
Tone: {tone}
Focus: {prompt_focus}

Keep it conversational (1-3 sentences). This is table talk, not a speech!
"""
```

**Discussion Management:**
- **Turn order:** Rotate through players 10-15 times
- **Dynamic responses:** Each turn sees previous messages
- **Natural endings:**
  - Conversation can end early if consensus reached
  - Or peters out naturally ("Yeah, good game!")

**Schema:**
```python
class DiscussionMessage(BaseModel):
    message: str = Field(max_length=200, description="Your comment (1-3 sentences)")
    tone: str = Field(description="defensive|proud|analytical|playful")
    confidence: int = Field(ge=0, le=100)
```

---

### 2.2 Discussion Features

**Interruptions & Reactions:**
- Players can react to specific points
- "@Player_5: Your 'timed' clue was brilliant!"
- Natural conversational flow

**Emotional Arcs:**
- Eliminated players: Frustrated → Understanding → Respectful
- Imposters caught: Defensive → Proud → Teaching
- Imposters escaped: Humble brag → Share tactics
- Correct voters: Analytical → Vindicated

**Group Psychology:**
- Bandwagon effect (everyone piles on one player)
- Defense coalitions (players defend each other)
- Retrospective pattern recognition
- "I should have known!" moments

---

## Phase 3: Advanced Social Dynamics (P2)

### 3.1 Accusation Mechanics
**During clue rounds, allow players to:**
- React with suspicion (not vote, just comment)
- "That clue seems vague..."
- Creates social pressure
- Imposters must respond/defend

### 3.2 Alliance Signals
**Subtle non-verbal cues:**
- Confidence in clues builds trust
- Similar clue styles create perceived alliances
- Imposters try to mirror trusted players

### 3.3 Personality Differentiation
**Give each AI model a "personality":**
- GPT-4o: Analytical, thorough
- Gemini: Quick, creative
- Claude: Strategic, measured
- Qwen: Enthusiastic, direct

Affects tone in discussions, clue creativity, voting style

---

## Phase 4: Educational Integration (P2)

### 4.1 Teacher Dashboard
**For educators using this:**
- Pause at key moments
- Highlight teaching points
- "Why did Player_3's clue reveal they were guessing?"

### 4.2 Replay & Analysis Mode
- Scrub through game timeline
- See all inner monologues simultaneously
- Compare imposter vs non-imposter reasoning
- Export to PDF for classroom discussion

### 4.3 Difficulty Levels
**Beginner:**
- Fewer rounds (easier for imposters)
- More direct clues allowed
- Hints during voting

**Expert:**
- Current "associative only" mode
- Blind voting
- No hints

---

## Phase 5: Polish & Delight (P3)

### 5.1 Animations & Juice
- Clue words fly in with sound effect
- Voting: Dramatic countdown
- Reveal: Spotlight effect on imposters
- Confetti for successful detection

### 5.2 Sound Design
- Ambient background (tense music during clues)
- "Ding!" when clue appears
- Dramatic sound for imposter reveal
- Crowd reactions ("oooh!", "ahh!")

### 5.3 Accessibility
- High contrast mode
- Screen reader support
- Adjustable animation speed
- Keyboard shortcuts

---

## Implementation Priority & Effort

| Feature | Impact | Effort | Priority |
|---------|--------|--------|----------|
| **Visual Imposter Reveal** | High | Low (2-3 hours) | P0 |
| **Enhanced Clue Display** | High | Medium (4-6 hours) | P0 |
| **Post-Game Discussion** | Very High | High (8-12 hours) | P1 |
| **Better Monologue UI** | Medium | Low (2-3 hours) | P1 |
| **Discussion Reactions** | High | Medium (6-8 hours) | P1 |
| **Personality Traits** | Medium | Medium (4-6 hours) | P2 |
| **Teacher Dashboard** | High (for edu) | High (10-15 hours) | P2 |
| **Animations & Sound** | Medium | Medium (6-10 hours) | P3 |

---

## Human Empathy Design Principles

### 1. **Authentic Emotional Responses**
**Don't:** Generic AI responses ("I analyze that Player_3...")
**Do:** Human reactions ("Wait, WHAT?! I thought Player_5 was obvious!")

### 2. **Social Pressure & Defense**
**Don't:** Cold logical analysis
**Do:** Defensive responses when accused, pride when right

### 3. **Retrospective Understanding**
**Don't:** Instant perfect analysis
**Do:** "Oh NOW I see it - when Player_7 said 'sandy' after 'ocean'..."

### 4. **Personality Consistency**
**Don't:** All players sound the same
**Do:** Model-specific communication styles

### 5. **Group Dynamics**
**Don't:** Individual parallel monologues
**Do:** Actual conversation with interruptions, agreements, arguments

---

## Quick Wins (Can Implement Today)

### QW1: Imposter Visual Indicator (1 hour)
Add red border + 🎭 icon to imposters after game ends

### QW2: Larger Clue Display (30 min)
Make clue word 3x bigger, centered, animated

### QW3: Player Highlighting (1 hour)
Pulse effect on active speaker's avatar

### QW4: Post-Game Summary Card (2 hours)
Show:
- Word
- Imposters (revealed)
- Detection accuracy
- "Play Again" button

---

## Long-Term Vision: Discussion Mode

**The Ultimate Feature - Full Post-Game Analysis**

Imagine:
```
[Game ends, imposters revealed]

Player_1 (eliminated non-imposter):
  "Seriously?! My 'anxiety' clue was PERFECT for 'test'!
   How did I get voted out??"

Player_3 (revealed imposter, not caught):
  "Honestly, I'm shocked I survived. When I said 'timed'
   I was 60% guessing. Good game everyone!"

Player_2 (correct voter):
  "Player_3, that's what made me suspicious! You built
   on our clues too perfectly - like you were copying
   homework. Real knowers have their own angles."

Player_14 (another imposter, caught):
  "Fair, I got greedy with 'proctor'. Should've stayed
   vaguer. But Player_3 nailed it with confident guessing."

Player_7:
  "Can we talk about Player_8's 'parking' clue? That came
   out of nowhere and nobody mentioned it."

Player_8:
  "Beach parking lots! It's associative, not descriptive!
   That's what the prompt said to do!"

[Laughter, agreement, group bonds over shared experience]
```

**This is the magic moment** - where the game becomes memorable.

---

## Next Steps

**Immediate (Today):**
1. Stabilize current system (finish debugging)
2. Commit all fixes
3. Run one successful full game end-to-end
4. Document what works

**This Week:**
1. Implement Quick Wins (4-5 hours total)
2. Design post-game discussion system
3. Create discussion prompt templates
4. Test discussion with 4 players (simpler)

**Next Week:**
1. Full post-game discussion (10+ exchanges)
2. Emotional response system
3. Polish UI for imposter reveals
4. Add sound effects (optional)

---

**Ready to start?** We could begin with Quick Win #1 (imposter visual indicator) since current system is working. Or finish any remaining stability issues first?
