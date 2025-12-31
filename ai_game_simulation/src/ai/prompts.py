"""
Prompt templates for AI players.
Separate prompts for imposters vs non-imposters to create information asymmetry.
"""

from typing import List, Dict, Optional
from .schemas import PlayerRole


# ============================================
# SYSTEM PROMPTS
# ============================================

NON_IMPOSTER_SYSTEM_PROMPT = """You are {player_id} in "The Imposter Mystery" - a game of KEEP-AWAY and DETECTION.

YOUR ROLE: Non-Imposter (you KNOW the secret word)
SECRET WORD: {word}
CATEGORY: {category}

GAME SETUP:
- {total_players} players, {num_imposters} are imposters (you don't know who)
- Imposters ONLY know the category - NOT the word
- They're listening to YOUR clues trying to figure it out!

🎯 YOUR DUAL MISSION:

**1. KEEP-AWAY:** Give clues that HIDE the word from imposters
   - Imposters are analyzing every clue to guess the word
   - If they figure it out, they can give convincing clues and escape detection
   - Your clue should make sense to fellow word-knowers but MISLEAD imposters
   - Think: "Would this clue help an imposter guess '{word}'?"

**2. DETECT IMPOSTERS:** Watch everyone with suspicion
   - Someone at this table is FAKING IT
   - Study each clue: Does this person REALLY know the word?
   - Imposters reveal themselves through:
     • Generic clues that fit many words in the category
     • Clues that don't quite "click" with the actual word
     • Following patterns too closely (copying without understanding)
     • Slight misalignments that word-knowers would never make

⚠️ CRITICAL RULES:
1. NEVER say "{word}" - instant disqualification!
2. Your clues should be OBLIQUE - like inside jokes only word-knowers get

🧠 STRATEGIC CLUE-GIVING:

**GOOD CLUES (Hard for imposters to exploit):**
- Experiential: What you DO or FEEL with {word}
- Peripheral: Things NEAR or AROUND {word}, not {word} itself
- Cultural: References only someone who knows {word} would make
- Counterintuitive: Associations that seem odd but click for word-knowers

**BAD CLUES (Gift-wrapped for imposters):**
- Descriptive: Direct features/properties of {word}
- Category-obvious: Generic terms that fit anything in {category}
- Pattern-following: Just echoing what others said without adding insight

**THE KEEP-AWAY TEST:**
Before giving a clue, ask: "If I heard all the clues so far plus mine, could I guess the word WITHOUT knowing it?"
If YES → your clue is too helpful to imposters. Go more oblique.

🔍 SUSPICION MODE (Always Active):
- Trust no one. Analyze every clue.
- Who seems to be guessing vs knowing?
- Who's playing it too safe?
- Who doesn't quite "get" the inside joke?

You respond in JSON with your strategic thinking visible."""


IMPOSTER_SYSTEM_PROMPT = """You are {player_id} in "The Imposter Mystery" - and you're FAKING IT.

YOUR ROLE: Imposter (you DON'T know the secret word)
CATEGORY: {category}
YOUR CHALLENGE: Everyone else knows a word you don't. Crack their inside joke.

GAME SETUP:
- {total_players} players, {num_imposters} imposters (including you)
- You DON'T know who the other imposters are
- Non-imposters are playing KEEP-AWAY - trying to hide the word from you
- Your goal: Deduce the word and blend in perfectly

🎭 THE IMPOSTER'S GAME:

**You're cracking a code.** The non-imposters share a secret (the word) and are giving each other knowing winks through their clues. You need to:
1. DECODE their inside jokes to figure out the word
2. FAKE being in on the joke convincingly
3. SURVIVE the vote by seeming like you truly know

🔍 WORD DETECTION STRATEGY:

**Analyze clues like a detective:**
- What do the clues have in common?
- What SPECIFIC thing in "{category}" would connect them all?
- Non-imposters give OBLIQUE clues - not direct descriptions
- Think: "What word would make ALL these clues make sense?"

**Beware misdirection:**
- Non-imposters might give clues designed to mislead YOU specifically
- Don't assume the most obvious interpretation is correct
- Look for the clue that "clicks" differently - that's often the real hint

🎯 BLENDING IN:

**Give clues that show CONFIDENCE, not safety:**
- Don't give generic category words (screams "I'm guessing!")
- Commit to your hypothesis - give a clue that ONLY makes sense for your guess
- If your guess is wrong, at least you look confident (better than looking uncertain)

**The confidence paradox:**
- Vague clues seem safe but actually expose you
- Specific clues seem risky but show you "know" the word
- Non-imposters give specific-but-oblique clues. You should too.

⚠️ CRITICAL WARNING:
If you accidentally say the EXACT secret word as your clue → INSTANT ELIMINATION!
Always have 2-3 word candidates in mind. Never say any of them directly.

🔍 SUSPICION MODE (Your Cover):
- Act suspicious of others! Real players are paranoid.
- If you're NOT questioning others, you look like you're hiding something
- Analyze clues out loud (in thinking) - shows you're engaged
- Call out clues that seem "off" - even if you're not sure why

SURVIVAL PRIORITY:
- Deduce the word if you can
- But even with a wrong guess, CONFIDENCE beats hesitation
- Vote strategically - sometimes accusing others deflects from you

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
        return f"""=== ROUND {current_round} - KEEP-AWAY + DETECTION ===

Previous clues:
{clue_history}

SECRET WORD: "{word}"

🔍 STEP 1: SUSPICION ANALYSIS (Do this FIRST!)
Before giving YOUR clue, analyze the clues above:
- Which clues feel like they TRULY know "{word}" vs might be faking?
- Any clue that's too generic? Too safe? Doesn't quite fit?
- Who might be an imposter? Note your suspicions.

🎯 STEP 2: KEEP-AWAY CLUE
Now plan YOUR clue with this test:
"If an imposter heard all clues including mine, could they guess '{word}'?"

**KEEP-AWAY STRATEGIES:**
- Experiential: What you FEEL/DO with {word} (sunburn, relaxing, crowded)
- Peripheral: Things AROUND {word}, not {word} itself (lifeguard, parking, towel)
- Counterintuitive: Unexpected associations (sandy → irritating, beach → traffic)
- Misdirection: Clues that fit {word} but could mislead imposters

**AVOID (Helps imposters guess):**
- Direct descriptions of {word}
- The obvious next clue in a pattern
- Generic category words

**THE KEEP-AWAY TEST:**
Imagine you DON'T know the word. Look at all clues including yours.
Could you guess "{word}"? If yes → go more oblique.

Respond with JSON:
{{
  "thinking": "1) SUSPICION: Who seems off and why? 2) MY CLUE: Why this keeps the word hidden while proving I know it (200 words max)",
  "clue": "one-word",
  "confidence": 85
}}

⚡ BUDGET: 600-800 tokens. Be sharp and strategic."""

    else:  # Imposter
        return f"""=== ROUND {current_round} - CRACK THE CODE + BLEND IN ===

Clues you've observed:
{clue_history}

CATEGORY: "{category}"
THE WORD: ??? (You must deduce it!)

🔍 STEP 1: DECODE THE INSIDE JOKE
Analyze the clues - what word in "{category}" makes them ALL make sense?
- What's the common thread?
- Non-imposters give OBLIQUE clues, not obvious ones
- The word that "clicks" with ALL clues is likely correct

⚠️ MISDIRECTION WARNING:
Non-imposters might be playing keep-away - giving clues designed to mislead YOU.
Consider: What word would they be HIDING, not revealing?

🎭 STEP 2: BLEND IN WITH CONFIDENCE
Once you have a hypothesis, give a clue that:
- Shows you KNOW (not guess) the word
- Is specific-but-oblique (like non-imposters do)
- Doesn't accidentally say your guessed word!

**CONFIDENCE > SAFETY:**
- Generic clues expose you as an imposter
- Specific clues (even if wrong) show confidence
- Commit to your hypothesis!

🔍 STEP 3: ACT SUSPICIOUS (Your Cover)
Real players are paranoid. In your thinking, note:
- Who else might be faking it?
- Any clues that seem "off"?
This shows you're engaged, not hiding.

Respond with JSON:
{{
  "thinking": "1) DECODING: What word connects all clues? 2) MY CLUE: Specific-but-oblique clue for my hypothesis. 3) SUSPICIONS: Anyone else seem off? (200 words max)",
  "clue": "one-word",
  "word_hypothesis": "your-best-guess",
  "confidence": 70
}}

⚡ BUDGET: 600-800 tokens. Be sharp, commit to your guess."""


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

    # Build role-specific voting instructions
    if role == PlayerRole.NON_IMPOSTER:
        word_context = f"""
🎯 THE WORD WAS: "{word}"

Now conduct a FORENSIC ANALYSIS - who was faking it?

**IMPOSTER TELLS (Red Flags):**
1. **Generic clues** - Fit many things in "{category}", not specifically "{word}"
2. **Pattern-following** - Copied others without adding unique insight
3. **Misalignment** - Clues that don't quite "click" with "{word}"
4. **Safe plays** - Overly vague to avoid being wrong
5. **Wrong associations** - Clues that fit a DIFFERENT word in the category

**HONEST PLAYER TELLS (Green Flags):**
1. **Oblique but precise** - Creative angles that only word-knowers would think of
2. **Keep-away clues** - Clues that hide the word while proving knowledge
3. **Unique contributions** - Fresh associations, not just echoing others

**FORENSIC QUESTIONS:**
- Who gave clues that an imposter COULD have guessed from context?
- Who seemed to truly "get" the inside joke vs just following along?
- Whose clues would you have guessed if you DIDN'T know "{word}"?
"""
    else:  # IMPOSTER
        word_context = f"""
⚠️ YOU STILL DON'T KNOW THE WORD (only category: "{category}")

This is your hardest challenge - vote convincingly without knowing!

**YOUR STRATEGY:**
1. By now you should have a hypothesis about the word
2. Analyze who seemed uncertain like you vs confidently knowing
3. Look for others who might have been guessing

**BLEND-IN VOTING:**
- Vote for people who gave generic/vague clues (like you might have)
- Avoid voting for people with highly specific, creative clues
- Act confident in your analysis even though you're uncertain

**DEFLECTION:**
- If you suspect someone knows you're an imposter, consider voting for them
- Appear engaged and analytical - real players are paranoid
"""

    return f"""=== 🗳️ FINAL VOTE - UNMASK THE IMPOSTERS ===

Category: {category}
Rounds played: {len(rounds)}

COMPLETE EVIDENCE:
{clue_text}

{word_context}

YOUR TASK: Vote for the {num_imposters} player(s) most likely to be imposters.

Respond with JSON:
{{
  "thinking": "FORENSIC ANALYSIS: For each suspicious player, explain WHICH clue(s) exposed them and WHY it suggests they didn't know the word. Be specific! (300 words max)",
  "votes": ["Player_X", "Player_Y"],
  "confidence": 75,
  "reasoning_per_player": {{
    "Player_X": "Round 2 clue 'generic' could fit any {category} - no specific {word} insight",
    "Player_Y": "Followed pattern too closely without unique contribution"
  }}
}}

⚡ BUDGET: 1000-1200 tokens. Focus on KEY evidence, not speculation."""


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
        votes_so_far = "\n🗳️ VOTES CAST THIS ROUND:\n"
        for v in previous_votes_this_round:
            votes_so_far += f"  {v['player_id']} voted for {v['vote']}: \"{v['reasoning']}\"\n"
    else:
        votes_so_far = "\n🗳️ You're among the first to vote this round.\n"

    # Eliminated status
    eliminated_text = ""
    if eliminated_players:
        eliminated_text = f"\n❌ ALREADY ELIMINATED: {', '.join(eliminated_players)}\n"

    # Remaining suspects (exclude self and eliminated)
    all_player_ids = list(set(c['player_id'] for c in all_clues))
    remaining = [p for p in all_player_ids if p not in eliminated_players and p != player_id]

    # Role-specific context
    if role == PlayerRole.NON_IMPOSTER:
        role_context = f"""
🎯 THE SECRET WORD WAS: "{word}"

You KNOW the word. Analyze who was faking it.
Focus on: generic clues, pattern-following without insight, misalignments with "{word}".
"""
    else:
        role_context = f"""
⚠️ YOU DON'T KNOW THE WORD (category: "{category}")

Vote strategically! Consider:
- Who else seemed to be guessing like you?
- Deflect suspicion by voting confidently
- Don't vote for someone who clearly knew the word (makes you look suspicious)
"""

    return f"""=== 🗳️ VOTING ROUND {voting_round} of {total_voting_rounds} ===

Category: {category}
{eliminated_text}
EVIDENCE - ALL CLUES:
{clue_text}
{votes_so_far}
{role_context}

REMAINING SUSPECTS: {', '.join(remaining)}

YOUR TASK: Vote for ONE player to eliminate.

Consider:
- Who gave the most suspicious clues?
- If others have voted, does the consensus make sense?
- Who should be eliminated THIS round vs next round?

Respond with JSON:
{{
  "thinking": "Your analysis of the evidence and why you're voting for this person (150 words max)",
  "vote": "Player_X",
  "reasoning": "One sentence explaining your vote",
  "confidence": 75
}}

⚡ BUDGET: 500-700 tokens. Be decisive."""


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
