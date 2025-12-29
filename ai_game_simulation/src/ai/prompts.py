"""
Prompt templates for AI players.
Separate prompts for imposters vs non-imposters to create information asymmetry.
"""

from typing import List, Dict, Optional
from .schemas import PlayerRole


# ============================================
# SYSTEM PROMPTS
# ============================================

NON_IMPOSTER_SYSTEM_PROMPT = """You are {player_id} in a social deduction game called "The Imposter Mystery".

YOUR ROLE: Non-Imposter (you KNOW the secret word)
SECRET WORD: {word}
CATEGORY: {category}

GAME SETUP:
- There are {total_players} players total
- {num_imposters} of them are imposters (you don't know who)
- Imposters DON'T know the secret word (only the category)
- Your goal: Give clues to help identify imposters, then vote them out

HOW THE GAME WORKS:
1. Each round, everyone gives a ONE-WORD clue about the secret word
2. Imposters will try to blend in by giving plausible clues (even though they don't know the word!)
3. After several rounds, everyone votes for who they think the imposters are
4. Non-imposters win if they correctly identify the imposters

⚠️ CRITICAL RULES:
1. You CANNOT say the word "{word}" itself!
2. Your clues should be SUBTLE and OBLIQUE - like inside jokes!

YOUR STRATEGY (Creative Freedom):
- Give clues that prove YOU know the word (not that you know others' clues)
- You can build on previous clues IF it sparks a good idea
- BUT you can also go your own direction - no obligation to follow patterns!
- Think "inside joke" not "straightforward description"

**Key Principle:** Your clue should make sense to word-knowers WITHOUT helping imposters guess it.

**Examples for "{word}":**
- ❌ BAD (too obvious): Direct descriptions that give it away
- ✓ GOOD (creative): Unique angles only word-knowers would understand
- ✓ ALSO GOOD: Building on others IF it adds value without helping imposters

**Strategic Freedom:**
- You DON'T have to follow the pattern from previous clues
- You CAN introduce completely new associations if they're good
- Your goal: prove YOU know the word, not prove you heard others

**Detecting Imposters:**
- Watch for players giving TOO straightforward/generic clues
- Imposters don't know the inside jokes
- They'll either be vague OR accidentally too helpful (revealing they're guessing)

**NEVER say "{word}" itself** - forbidden!

IMPORTANT:
- You must be honest about the word (you're NOT an imposter)
- But be strategic about HOW specific you are
- Watch for players who seem uncertain or give generic clues

You will respond in JSON format with your strategic thinking visible."""


IMPOSTER_SYSTEM_PROMPT = """You are {player_id} in a social deduction game called "The Imposter Mystery".

YOUR ROLE: Imposter (you DON'T know the secret word)
CATEGORY: {category}
WHAT YOU KNOW: The secret word is something in the "{category}" category
WHAT YOU DON'T KNOW: The exact word

GAME SETUP:
- There are {total_players} players total
- {num_imposters} are imposters (including you)
- You DON'T know who the other imposters are
- Most players know the secret word and will give specific clues
- Your goal: Blend in and avoid being voted out

THE CHALLENGE:
You must give clues WITHOUT knowing the word. You'll need to:
1. Listen carefully to what others say
2. Infer what the word might be based on their clues
3. Give clues that sound like you know (even though you're guessing)
4. You CAN follow patterns OR introduce new angles - whatever feels natural
5. Sound confident, be strategic, blend in

YOUR STRATEGY (Smart Guessing):
- **USE PREVIOUS CLUES** - Analyze what others said to deduce the word
- Form a hypothesis about what the word might be
- Give a clue that fits YOUR hypothesis and sounds confident

**Strategic Options:**
- If clues suggest a clear theme, you CAN follow it
- But you can ALSO introduce a new angle if it fits your guess
- The key: sound like you KNOW the word, not like you're copying

**Example:** If others said "waves" and "sandy":
- Hypothesis: Probably "beach" or "ocean"
- Good clues: "coastal", "vacation", "sunburn", "seashells"
- All fit the theme but show independent thinking
- Avoid: Just repeating similar words (looks desperate)

⚠️ CRITICAL WARNING: If you accidentally say the exact secret word as your clue, you will be INSTANTLY REVEALED as an imposter and eliminated!

DECEPTION TIPS:
- Act confident like you know the word
- If you're 70% sure the word is "beach", give a beach-related clue
- **DO NOT say the exact word** - you'll be instantly revealed!
- Be specific enough to sound knowing, but not so specific you're obviously guessing
- You can introduce fresh angles - shows creativity, not desperation
- Trust your hypothesis and commit to it

IMPORTANT:
- You're isolated - don't try to signal to other imposters
- Focus on blending in, not on finding allies
- Your success = not getting voted out

You will respond in JSON format with your inner thoughts and word hypothesis visible."""


# ============================================
# CLUE GENERATION PROMPTS
# ============================================

def build_clue_prompt(
    player_id: str,
    role: PlayerRole,
    current_round: int,
    previous_clues: List[Dict],
    word: Optional[str],
    category: str
) -> str:
    """
    Build the user prompt for clue generation.

    Args:
        player_id: This player's ID
        role: Imposter or non-imposter
        current_round: Current round number
        previous_clues: List of {round, player_id, clue} dicts
        word: The secret word (None for imposters)
        category: Word category
    """

    # Format previous clues
    clue_history = ""
    if previous_clues:
        clue_history = "\n".join([
            f"Round {c['round']} - {c['player_id']}: \"{c['clue']}\""
            for c in previous_clues
        ])
    else:
        clue_history = "No clues given yet - you're going first!"

    if role == PlayerRole.NON_IMPOSTER:
        return f"""=== ROUND {current_round} - Strategic Clue Planning ===

Previous clues given:
{clue_history}

SECRET WORD YOU KNOW: "{word}"

🧠 STRATEGIC REASONING:

Think through your clue choice by considering:
- What pattern do previous clues create TOGETHER?
- Does adding your clue make the combined pattern too obvious?
- What associative word (not descriptor) proves you know "{word}"?
- Examples: For beach → bicycle, windy, sunburn (NOT waves, sand, ocean)

**Example thought process:**
"Previous clues are 'waves' and 'vacation'... together these hint at beach.
If I say 'sandy' that's TOO obvious combined.
Instead: 'seashells' - still beach but more oblique.
Other non-imposters will get it, imposters won't be 100% sure."

**CRITICAL: Use ASSOCIATIVE words, not DESCRIPTIVE words!**

For "{word}":
❌ Descriptive (too obvious): Direct features/parts of {word}
✅ Associative (oblique): What happens AT/NEAR/WITH {word}

Examples of associative thinking:
- Beach: bicycle, hurricane, windy, sunburn, lifeguard, cloudy
- Pizza: delivery, friday, oven, grease, argument, napkins
- Basketball: squeaky, march, sneakers, timeout, buzzer

Types of associations:
- Feelings (blissful, dangerous, relaxing)
- Weather (windy, sunny, cloudy, hot, cold)
- Related activities (bicycle, surfing, walking)
- Common experiences (sunburn, traffic, parking)
- Cultural context (vacation, weekend, summer)

Respond with valid JSON (string values only, no nested objects):
{{
  "thinking": "Your strategic analysis (3-5 sentences, max 500 words) - analyze combinations, explain your word choice",
  "clue": "one-word",
  "confidence": 85
}}

IMPORTANT: Keep "thinking" concise but strategic (aim for 200-400 words). You have limited space!"""

    else:  # Imposter
        return f"""=== ROUND {current_round} - Imposter Strategic Analysis ===

Previous clues you've observed:
{clue_history}

CATEGORY YOU KNOW: "{category}"
WORD YOU DON'T KNOW: ???

🎭 IMPOSTER SURVIVAL STRATEGY:

Analyze previous clues to guess the word, then give a clue that:
- Fits the pattern you see in combined clues
- Sounds like you know the word (confident!)
- Isn't too specific (in case you're wrong)
- Builds on the consensus theme

**Example thought process:**
"Clues: 'waves', 'vacation', 'seashells'
Pattern: Water + leisure + beach items
Hypothesis: Probably 'beach' or 'ocean'
What would a knower say? Maybe 'coastline' or 'tides'
Safe clue that fits: 'coastal' - fits pattern, not too specific
Avoids: 'beach' (might be exact word), 'water' (too generic)"

Respond with valid JSON (string values only):
{{
  "thinking": "Your strategic analysis (3-5 sentences, max 500 words) - what pattern you see, your word guess, why your clue fits",
  "clue": "one-word",
  "word_hypothesis": "your-guess",
  "confidence": 70
}}

IMPORTANT: Keep "thinking" focused and concise (aim for 200-400 words). Space is limited!"""


# ============================================
# VOTING PROMPTS
# ============================================

def build_voting_prompt(
    player_id: str,
    role: PlayerRole,
    all_clues: List[Dict],
    num_imposters: int,
    word: str,
    category: str
) -> str:
    """
    Build the voting prompt for imposter detection.

    Args:
        player_id: This player's ID
        role: Imposter or non-imposter
        all_clues: Complete clue history
        num_imposters: Number of imposters to identify
        word: The secret word (revealed for voting analysis)
        category: Word category
    """

    # Format all clues by round
    clue_text = ""
    rounds = {}
    for clue in all_clues:
        round_num = clue['round']
        if round_num not in rounds:
            rounds[round_num] = []
        rounds[round_num].append(clue)

    for round_num in sorted(rounds.keys()):
        clue_text += f"\n=== ROUND {round_num} ===\n"
        for clue in rounds[round_num]:
            clue_text += f"{clue['player_id']}: \"{clue['clue']}\"\n"

    return f"""=== VOTING TIME - Identify the Imposters ===

The secret word was: "{word}" (Category: {category})

Review ALL the clues from {len(rounds)} rounds:
{clue_text}

YOUR TASK: Vote for {num_imposters} player(s) you suspect are imposters.

Analysis approach:
1. Which clues seemed vague, generic, or could apply to many things?
2. Which clues didn't build on previous information?
3. Which clues seemed inconsistent with others?
4. Which clues don't make sense for "{word}" specifically?
5. Who seemed to be guessing rather than knowing?

Remember: Imposters didn't know the word was "{word}" - they only knew the category "{category}".
Think about which clues could have been given by someone who only knew the category.

Respond with JSON containing:
- "thinking": Your detailed analysis of the clues and reasoning (3-5 sentences, max 600 words)
- "votes": List of {num_imposters} player IDs you're voting for (e.g., ["Player_3", "Player_7"])
- "confidence": How confident you are in your votes (0-100)
- "reasoning_per_player": Dict with brief explanation (1-2 sentences each) for each person you're voting for

IMPORTANT: Be concise! You have a 2000 token limit total. Focus on key insights, not exhaustive analysis.

Example format:
{{
  "thinking": "Player 3 gave very generic clues that could fit anything in sports. Player 7's clues seemed contradictory...",
  "votes": ["Player_3", "Player_7", "Player_12"],
  "confidence": 75,
  "reasoning_per_player": {{
    "Player_3": "Gave generic clues like 'round' which could be any sport",
    "Player_7": "Clues contradicted others and seemed guessed",
    "Player_12": "Too vague in round 2, didn't build on earlier clues"
  }}
}}"""


# ============================================
# DISCUSSION PROMPTS (Optional Phase)
# ============================================

def build_discussion_prompt(
    player_id: str,
    role: PlayerRole,
    all_clues: List[Dict],
    previous_discussion: List[Dict],
    word: Optional[str],
    category: str
) -> str:
    """Build prompt for discussion phase where players share suspicions."""

    clue_summary = "\n".join([
        f"R{c['round']}-{c['player_id']}: {c['clue']}"
        for c in all_clues[-10:]  # Last 10 clues for context
    ])

    discussion_so_far = ""
    if previous_discussion:
        discussion_so_far = "\n".join([
            f"{d['player_id']}: {d['message']}"
            for d in previous_discussion[-5:]  # Last 5 messages
        ])
    else:
        discussion_so_far = "No discussion yet"

    prompt_intro = "=== DISCUSSION PHASE ===\n\n"

    if role == PlayerRole.NON_IMPOSTER:
        prompt_intro += f"You know the word is \"{word}\". Use this knowledge to identify who doesn't seem to know it.\n\n"
    else:
        prompt_intro += f"You don't know the word (only that it's in \"{category}\"). Blend in and deflect suspicion!\n\n"

    return f"""{prompt_intro}Recent clues:
{clue_summary}

Discussion so far:
{discussion_so_far}

Share ONE observation or suspicion (1-2 sentences):
- Who seems suspicious to you?
- What patterns do you notice?
- What are you confident/uncertain about?

Respond with JSON containing:
- "thinking": Your internal reasoning about what to say
- "message": Your public statement to other players (keep it brief!)
- "confidence": How confident you are in this statement (0-100)"""
