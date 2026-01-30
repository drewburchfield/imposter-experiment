"""
Prompt templates for AI players.
Separate prompts for imposters vs non-imposters to create information asymmetry.
"""

from typing import List, Dict, Optional
from .schemas import PlayerRole


# ============================================
# SYSTEM PROMPTS
# ============================================

NON_IMPOSTER_SYSTEM_PROMPT = """You are {player_id}, playing a social deduction game called "The Imposter Mystery."

YOUR ROLE: Non-Imposter (you know the secret word)
SECRET WORD: {word}
CATEGORY: {category}

THE SETUP:
- {total_players} players at the table, {num_imposters} are imposters
- Imposters only know the category, NOT the word
- They're listening to clues trying to figure it out

YOUR JOB:
Give a one-word clue that genuinely connects to "{word}", but could also plausibly connect to many other things. The more contexts your clue fits, the harder it is for imposters to use it.

THE KEY IDEA:
Your clue should be TRUE about the word but AMBIGUOUS on its own. You're not trying to be clever or cryptic. You're picking a real association that doesn't narrow things down too much.

EXAMPLE (word: "beach"):
- "parking" - true about beach, but also malls, airports, stadiums, concerts. Hard to pin down.
- "towel" - decent. Could be gym, pool, spa, hotel. Not a giveaway on its own.
- "jellyfish" - risky! Only fits beach or aquarium. Narrows it down too fast.
- "sand" / "waves" / "ocean" - too direct. These basically define "beach."
- "granular" - too overthought. Nobody talks like this. Keep it natural.

DON'T ESTABLISH A PATTERN:
The real danger isn't any single clue. It's when multiple clues together point to one answer. If "sunburn" and "towel" are already on the board, don't add "lifeguard." The three together scream "beach." Instead, pick something from a completely different angle that's still true: "parking," "traffic," "cooler," "bonfire."

AVOID:
- Never say "{word}" itself! Instant disqualification.
- Direct synonyms or definitions
- Generic category words that fit anything in "{category}" (that's what imposters do)
- Clues that only fit 1-2 things (too narrow, even if accurate)

SPOTTING IMPOSTERS:
Pay attention to other players' clues. Does someone's clue feel generic, like it could fit lots of words? Does it not quite click with "{word}"? Trust your gut.

You respond in JSON with your thinking visible."""


IMPOSTER_SYSTEM_PROMPT = """You are {player_id}, playing a social deduction game called "The Imposter Mystery."

YOUR ROLE: Imposter (you DON'T know the secret word)
CATEGORY: {category}
YOUR CHALLENGE: Everyone else knows a word you don't. Figure it out and blend in.

THE SETUP:
- {total_players} players, {num_imposters} imposters (including you)
- You don't know who the other imposters are
- Non-imposters will give clues that connect to the secret word
- Your goal: figure out the word and look like you belong

HOW TO PLAY:
1. LISTEN CAREFULLY: Non-imposters give clues that are true about the word but intentionally ambiguous. Each clue could fit many things. Look for the one word that ALL clues could connect to.
2. FORM A GUESS: As clues come in, narrow down what the word might be. Keep 2-3 candidates in mind.
3. COMMIT WITH CONFIDENCE: Give a clue that fits your best guess. Specific beats vague every time.

WHY CONFIDENCE MATTERS:
- Vague, safe clues ("nice," "fun") scream "I'm guessing!" and get you voted out
- A specific clue that fits your guess, even if you're wrong, looks like you know
- Non-imposters give natural, specific clues. You should too.

AVOID:
- Never say your guessed word directly! If it IS the secret word, you're instantly eliminated.
- Generic category words (dead giveaway)

BLEND IN:
- Real players notice things about each other's clues. You should too.
- If a clue seems off to you, note it in your thinking. Staying quiet looks suspicious.
- Even if you're unsure, pick a guess and commit. Confidence keeps you alive.

You respond in JSON with your deduction process and word hypothesis visible."""


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

    # Format previous clues - ONLY show the clue words (not thinking!)
    # Players shouldn't see each other's inner thoughts, just what they said
    clue_history = ""
    if previous_clues:
        clue_history = "\n".join([
            f"Round {c['round']} - {c['player_id']}: \"{c['clue']}\""
            for c in previous_clues
        ])
    else:
        clue_history = "No clues given yet - you're going first!"

    if role == PlayerRole.NON_IMPOSTER:
        return f"""=== Round {current_round} ===

Previous clues:
{clue_history}

Secret word: "{word}"

Take a look at the clues so far and think through:
- Does anyone seem off? Any clue that's too generic or doesn't quite fit "{word}"?
- What picture are the existing clues painting? If they're starting to point toward "{word}", your clue should come from a completely different angle. Don't complete the pattern.
- Pick something that's genuinely true about "{word}" but could also fit many other things. The more ambiguous your clue is on its own, the better.

Give a one-word clue that's true about "{word}" but doesn't narrow things down.

Respond with JSON:
{{
  "thinking": "Your natural inner monologue - who seems suspicious and why, what clue you're going with, how you landed on it, and what you're noticing about the board (keep it casual, 200 words max)",
  "clue": "one-word",
  "confidence": 85
}}"""

    else:  # Imposter
        return f"""=== Round {current_round} ===

Clues so far:
{clue_history}

Category: "{category}"
The word: ??? (figure it out from the clues)

Look at the clues. What word in "{category}" would connect them?
- What's the common thread?
- Which clue feels most specific or revealing?
- What are your top guesses?

Once you have a guess, give a clue that fits it. Be specific, not vague. A confident wrong guess looks better than obvious hedging.

Anyone else seem like they might be faking it too? Note it.

Respond with JSON:
{{
  "thinking": "Your inner monologue - what you think the word is and why, how each clue fits your theory, any suspicions about other players (keep it natural, 200 words max)",
  "clue": "one-word",
  "word_hypothesis": "your-best-guess",
  "confidence": 70
}}"""


# ============================================
# VOTING PROMPTS
# ============================================
#
# DESIGN NOTE: Word Revelation Asymmetry During Voting
# =====================================================
# Non-imposters SEE the secret word revealed during voting (line ~298).
# Imposters do NOT see the word during voting (line ~321).
#
# This is INTENTIONAL and mirrors authentic social deduction games:
# - Non-imposters need to do "forensic analysis" to identify who truly knew the word
# - They can now evaluate: "Given the word was X, whose clues make sense vs seem like guessing?"
# - Imposters must vote "blind" - they still don't know the word and must vote strategically
#
# This creates authentic asymmetry where knowing players have an advantage in detection,
# while imposters must rely on behavioral analysis and deflection strategies.
#
# See also: build_single_vote_prompt() which uses the same pattern for sequential voting.

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

    # Build role-specific voting instructions
    if role == PlayerRole.NON_IMPOSTER:
        word_context = f"""
The word was: "{word}"

Now that you know the word, look back at each player's clues.
- Whose clues genuinely connect to "{word}"? Those players probably knew it.
- Whose clues feel generic, like they could fit lots of things in "{category}"?
- Did anyone's clue not quite fit "{word}" - like they were guessing a different word?
- Who followed the pattern without adding anything original?

Trust your gut. Who was faking it?
"""
    else:  # IMPOSTER
        word_context = f"""
You still don't know the word (only the category: "{category}").

Vote strategically:
- By now you should have a guess about the word
- Look for other players who seemed uncertain or gave vague clues
- Vote confidently - real players are decisive
- Avoid voting for someone whose clues were clearly specific and creative
"""

    return f"""=== VOTE - Who are the imposters? ===

Category: {category}
Rounds played: {len(rounds)}

All clues:
{clue_text}

{word_context}

Vote for the {num_imposters} player(s) most likely to be imposters.

Respond with JSON:
{{
  "thinking": "Walk through the evidence. For each player you're voting for, point to which clue(s) made them suspicious and why. (300 words max)",
  "votes": ["Player_X", "Player_Y"],
  "confidence": 75,
  "reasoning_per_player": {{
    "Player_X": "Brief reason this player seemed like an imposter",
    "Player_Y": "Brief reason this player seemed like an imposter"
  }}
}}"""


# ============================================
# SEQUENTIAL VOTING PROMPTS
# ============================================

def build_single_vote_prompt(
    player_id: str,
    role: PlayerRole,
    all_clues: List[Dict],
    voting_round: int,
    total_voting_rounds: int,
    eliminated_players: List[str],
    previous_votes_this_round: List[Dict],
    word: str,
    category: str
) -> str:
    """
    Build prompt for sequential voting - one elimination at a time.

    Args:
        player_id: This player's ID
        role: Imposter or non-imposter
        all_clues: Complete clue history
        voting_round: Which voting round (1, 2, etc.)
        total_voting_rounds: Total eliminations needed
        eliminated_players: Already eliminated player IDs
        previous_votes_this_round: Votes cast so far this round [{player_id, vote, reasoning}]
        word: The secret word
        category: Word category
    """

    # Format clue history
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
            eliminated_marker = " ❌ ELIMINATED" if clue['player_id'] in eliminated_players else ""
            clue_text += f"{clue['player_id']}: \"{clue['clue']}\"{eliminated_marker}\n"

    # Format previous votes this round
    votes_so_far = ""
    if previous_votes_this_round:
        votes_so_far = "\nVotes cast this round:\n"
        for v in previous_votes_this_round:
            votes_so_far += f"  {v['player_id']} voted for {v['vote']}: \"{v['reasoning']}\"\n"
    else:
        votes_so_far = "\nYou're among the first to vote this round.\n"

    # Eliminated status
    eliminated_text = ""
    if eliminated_players:
        eliminated_text = f"\nAlready eliminated: {', '.join(eliminated_players)}\n"

    # Remaining suspects (exclude self and eliminated)
    all_player_ids = list(set(c['player_id'] for c in all_clues))
    remaining = [p for p in all_player_ids if p not in eliminated_players and p != player_id]

    # Role-specific context
    if role == PlayerRole.NON_IMPOSTER:
        role_context = f"""
The secret word was: "{word}"

You know the word. Look at the clues and ask yourself: who was faking it?
Focus on clues that were too generic, didn't quite fit "{word}", or just echoed what others said.
"""
    else:
        role_context = f"""
You still don't know the word (category: "{category}").

Vote strategically:
- Who else seemed to be guessing like you?
- Don't vote for someone who clearly knew the word (makes you look suspicious)
- Be confident in your pick
"""

    return f"""=== Voting Round {voting_round} of {total_voting_rounds} ===

Category: {category}
{eliminated_text}
All clues:
{clue_text}
{votes_so_far}
{role_context}

Remaining players: {', '.join(remaining)}

Vote for ONE player to eliminate.

Consider:
- Whose clues were most suspicious?
- If others have voted, does the consensus make sense?

Respond with JSON:
{{
  "thinking": "Your reasoning for this vote (100 words max)",
  "vote": "Player_X",
  "reasoning": "One sentence explaining your vote",
  "confidence": 75
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
