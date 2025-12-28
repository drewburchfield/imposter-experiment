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

YOUR STRATEGY (Advanced Deception):
- Give clues that ONLY make sense if you know the word
- Think "inside joke" not "straightforward description"
- **Dodge giving context** to imposters - don't help them guess!
- Be creative, indirect, clever - NOT obvious

**Examples for "{word}":**
- ❌ BAD (too obvious): Straightforward descriptions help imposters
- ✓ GOOD (subtle): Oblique references only word-knowers would get

**Strategic Balance:**
- Prove to other non-imposters you know it (they'll understand the inside joke)
- BUT don't give imposters enough context to figure it out
- Straightforward clues are LAST RESORT only!

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
3. Give clues that FIT the pattern without being too obvious about not knowing
4. Sound confident even when you're guessing

YOUR STRATEGY (CRITICAL - This is how you survive):
- **USE PREVIOUS CLUES** - This is your PRIMARY information source!
- Analyze what others have said to deduce the word
- **Build directly on their clues** - echo their themes
- Give clues that:
  * Mirror the pattern you see in others' clues
  * Use words that connect to what's already been said
  * Sound confident like you know the word
  * Fit the category "{category}"
- **Example:** If others said "waves" and "sandy", you could say "coastal" or "vacation"
- **NEVER be first** to introduce a completely new theme (huge red flag!)
- **NEVER give generic** clues that could fit any word in the category
- **ALWAYS reference** what you've heard - blend in with the consensus!

⚠️ CRITICAL WARNING: If you accidentally say the exact secret word as your clue, you will be INSTANTLY REVEALED as an imposter and eliminated!

DECEPTION TIPS:
- Act like you know the word (fake it till you make it)
- If you're 70% sure the word is "beach", give a beach-related clue like "sandy" or "waves"
- **DO NOT say what you think the word is** - say something RELATED to it
- Better to be specific and potentially wrong than vague and suspicious
- Build on the consensus - don't contradict the group
- **NEVER guess the exact word in your clue** - you'll instantly lose!

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
        return f"""=== ROUND {current_round} - Your Turn ===

Previous clues:
{clue_history}

Now it's YOUR turn to give a clue about "{word}".

Remember:
- Make it relevant to "{word}"
- Help other non-imposters understand
- But don't make it SO obvious that imposters can guess the word
- Consider what's already been said - add new information
- Be creative but relevant

Respond with JSON containing:
- "thinking": Your strategic thoughts (2-3 sentences about what you're considering)
- "clue": Your one-word clue
- "confidence": How confident you are (0-100)"""

    else:  # Imposter
        return f"""=== ROUND {current_round} - Your Turn (You're Blending In!) ===

Previous clues you've observed:
{clue_history}

Based on these clues, what do you think the secret word might be?
Remember: You only know it's in the "{category}" category.

Your task: Give a clue that makes it seem like you KNOW the word!

Strategy:
- Look for patterns in others' clues
- What word would connect all these clues?
- Give something that fits both the category and the pattern
- Sound confident!

Respond with JSON containing:
- "thinking": What you're inferring from the clues, your strategy (2-3 sentences)
- "clue": Your one-word clue (make it sound like you know the word!)
- "word_hypothesis": What you currently think the word might be
- "confidence": How confident you are in your blending (0-100)"""


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
- "thinking": Your detailed analysis of the clues and reasoning (3-5 sentences)
- "votes": List of {num_imposters} player IDs you're voting for (e.g., ["Player_3", "Player_7"])
- "confidence": How confident you are in your votes (0-100)
- "reasoning_per_player": Dict with brief explanation for each person you're voting for

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
