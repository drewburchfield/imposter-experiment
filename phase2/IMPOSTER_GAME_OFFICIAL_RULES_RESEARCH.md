# Complete Imposter Word Game Official Rules Research

**Research Date:** December 27, 2025
**Purpose:** Comprehensive documentation of official imposter word game rules across all major variants to validate implementation accuracy.

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Game Variants Overview](#game-variants-overview)
3. [Standard Imposter Game Rules](#standard-imposter-game-rules)
4. [Spyfall Rules (Complete)](#spyfall-rules-complete)
5. [The Chameleon Rules (Complete)](#the-chameleon-rules-complete)
6. [Undercover Rules (Complete)](#undercover-rules-complete)
7. [Insider Rules (Complete)](#insider-rules-complete)
8. [Comparative Analysis](#comparative-analysis)
9. [Edge Cases Handbook](#edge-cases-handbook)
10. [Common Variations & House Rules](#common-variations--house-rules)
11. [Implementation Validation Checklist](#implementation-validation-checklist)

---

## Executive Summary

**What is an Imposter Word Game?**
A social deduction party game where most players receive the same secret word and must identify imposters who have a different word (or no word) while giving clues subtle enough not to reveal the word to the imposters.

**Core Mechanics Across All Variants:**
- **Role Assignment:** Majority get the same word (Civilians/Non-Spies), minority get different/no word (Imposters/Spy/Chameleon)
- **Clue-Giving:** Players take turns describing their word without saying it
- **Discussion:** Group debates who seems suspicious
- **Voting:** Players vote to eliminate suspected imposters
- **Win Conditions:** Civilians win by catching imposters; imposters win by surviving or guessing the word

**Key Finding:** While the basic premise is consistent, official rules vary significantly in mechanics like voting systems, round structure, scoring, and edge case handling.

---

## Game Variants Overview

### 1. **Generic "Imposter Game"** (Online/Mobile Apps)
- **Origin:** Modern digital adaptation, no single official publisher
- **Platforms:** playimposter.com, wordimpostor.com, impostergame.net, mobile apps
- **Complexity:** Low (casual party game)
- **Best For:** Casual groups, online play, flexible rules

### 2. **Spyfall** (Hobby Games, 2014)
- **Publisher:** Hobby Games / Cryptozoic Entertainment
- **Designer:** Aleksandr Ushan
- **Players:** 3-8 (Spyfall 2 supports up to 12)
- **Complexity:** Medium (location-based theme, role cards)
- **Best For:** Groups who want structured gameplay with locations/roles

### 3. **The Chameleon** (Big Potato Games, 2017)
- **Publisher:** Big Potato Games
- **Designer:** Rikki Tahta
- **Players:** 4-6 (variants for 3, 7-8)
- **Complexity:** Medium (dice/code card mechanics)
- **Best For:** Groups who want physical components and structured scoring

### 4. **Undercover** (Yanstar Studio)
- **Origin:** Chinese party game adaptation
- **Players:** 3-20
- **Complexity:** Medium (three distinct roles)
- **Best For:** Large groups, apps, includes "Mr. White" blank role

### 5. **Insider** (Oink Games, 2016)
- **Publisher:** Oink Games
- **Players:** 4-8
- **Complexity:** Medium-High (combines 20 Questions with social deduction)
- **Best For:** Groups who want asymmetric information and time pressure

### 6. **A Fake Artist Goes to New York** (Oink Games, 2012)
- **Publisher:** Oink Games
- **Players:** 5-10
- **Complexity:** Medium (drawing instead of words)
- **Best For:** Creative groups who prefer drawing to word clues

---

## Standard Imposter Game Rules

**Source Compilation:** playimposter.com, impostergame.net, wordimpostor.com, Game On Family

### 1. SETUP

#### Player Count
- **Minimum:** 3 players (barely functional)
- **Recommended:** 4-12 players
- **Maximum:** Varies by platform (some support up to 99 in local mode)
- **Sweet Spot:** 6-8 players

#### Number of Imposters
**General Rule:** 1 imposter per 4-6 players

**Specific Recommendations:**
- **3 players:** 1 imposter (very difficult, paranoia-heavy)
- **4-6 players:** 1 imposter
- **7-8 players:** 1-2 imposters (2 recommended for balance)
- **9-12 players:** 2 imposters
- **12+ players:** Consider splitting into two groups

**Source:** [PlayImposter.com Group Size Guide](https://playimposter.com/guide/imposter-game/group-size/)

#### Word Assignment
- **Civilians:** All receive identical secret word
- **Imposters (Standard Mode):** Receive a related but different word
- **Imposters (Blank/Mr. White Mode):** Receive NO word at all

**Word Selection Methods:**
- Manual selection by moderator
- Random generation from word lists
- Category-based selection (food, animals, places, etc.)

### 2. COMPLETE GAME FLOW

#### Phase 1: Role Distribution
1. Players receive roles privately (via app, cards, or moderator whisper)
2. Players look at their word without revealing it
3. Imposters identify they have a different/no word
4. Game begins

#### Phase 2: Clue-Giving Rounds

**Number of Rounds:** 2-3 rounds of clues before voting
- **3-5 players:** 2 full rounds recommended
- **6+ players:** 2-3 rounds (more rounds = more information but longer game)

**Clue Format (CRITICAL RULE):**
- **Standard Rule:** ONE WORD per player per round
- **Common Variation:** Short phrases allowed (3-5 words)
- **Prohibited:** Cannot say the secret word itself
- **Prohibited:** Cannot use direct synonyms (e.g., "Basketball" can't use "Hoops" or "NBA")
- **Prohibited:** Cannot use rhyming words or spell out the word

**Turn Order:**
- Clockwise around circle OR random order
- Each player gives one clue
- No skipping turns
- No passing

**Example Clue Quality:**
| Secret Word | Good Clue | Too Obvious | Too Vague |
|-------------|-----------|-------------|-----------|
| Apple | "Red fruit" | "iPhone logo" | "Thing" |
| Basketball | "Orange sport" | "Michael Jordan's game" | "Round" |
| Pizza | "Italian food" | "Pepperoni and cheese" | "Popular" |

#### Phase 3: Discussion Phase

**Timing:** After clue rounds complete, before voting
**Duration:** Flexible (2-5 minutes typical)

**Discussion Activities:**
- Players debate who seems suspicious
- Point out vague or odd clues
- Form alliances or accusatory arguments
- Imposters attempt to blend in or redirect suspicion

**No Official Rules For:**
- Speaking order (freeform discussion)
- Time limits (group decides)
- Interruptions (group decides)

#### Phase 4: Voting

**When Voting Occurs:** After 2-3 clue rounds + discussion

**Voting Method (most common):**
1. All players vote simultaneously
2. Common methods:
   - Point at suspect on count of 3
   - Write name on paper
   - Use app voting buttons
   - Raise hand for each suspect in turn

**Vote Counting:**
- **Standard:** Simple majority (player with most votes)
- **Tie Handling:** NOT OFFICIALLY SPECIFIED in generic imposter rules
  - Common house rules:
    - Revote between tied players
    - No elimination on ties (imposters win)
    - Random selection among tied players
    - Moderator/dealer decides

**Elimination:**
- Player with most votes is eliminated
- Their role is immediately revealed
- Game continues or ends based on win conditions

### 3. WIN CONDITIONS

#### Civilians Win If:
1. **All imposters are eliminated** through voting
2. Game typically ends immediately when last imposter eliminated

#### Imposters Win If:
1. **Survive until the end** without being voted out
   - **Specific threshold varies by variant:**
     - When imposters equal or outnumber civilians
     - When only 3 players remain and civilian voted out
     - When voting fails to identify any imposter
2. **Correctly guess the civilians' secret word** (if this rule is enabled)
   - Timing: Usually when eliminated OR at end of game
   - Only gets one guess
   - Immediate win even if caught

### 4. SCORING (MULTI-ROUND GAMES)

**Single Round Scoring:**
- **Civilians win:** 1 point per civilian (or 2 points total team score)
- **Imposter wins:** 1 point for surviving + 1 bonus point for guessing word

**Multi-Game Tournaments:**
- Track wins across multiple rounds
- Rotate who has been imposter for fairness
- First to X points wins (commonly 5 points)

### 5. TIMING

**Per-Round Duration:**
- **Quick Mode:** 5-10 minutes total
- **Standard:** 10-15 minutes total
- **Extended:** 15-20 minutes with larger groups

**Phase Timers (Optional):**
- Clue-giving: 30-60 seconds per player
- Discussion: 2-5 minutes
- Voting: 1 minute

---

## Spyfall Rules (Complete)

**Official Sources:**
- [Spyfall Official Rulebook PDF](https://cdn.1j1ju.com/medias/99/c4/5e-spyfall-rulebook.pdf)
- [UltraBoardGames Spyfall Rules](https://www.ultraboardgames.com/spyfall/game-rules.php)
- [OfficialGameRules.org Spyfall](https://officialgamerules.org/game-rules/spyfall/)

### KEY DIFFERENCES FROM GENERIC IMPOSTER

**Major Distinctions:**
1. **Questioning System** instead of clue-giving
2. **Location Theme** - 26 different locations with specific roles
3. **Spy Reveal Mechanic** - spy can stop game and guess location
4. **8-Minute Timer** - strict time limit per round
5. **Accusation System** - players can stop clock to accuse

### 1. SETUP

#### Components
- **208 cards total**
- **26 location decks** (8 cards each)
  - 7 identical location cards with specific roles
  - 1 spy card
- **Ziplock bags** for organizing decks
- **Timer** (8 minutes)

#### Player Count & Spy Distribution
- **Minimum:** 3 players (functional but challenging)
- **Maximum:** 8 players (standard) / 12 players (Spyfall 2)
- **Spy Count:**
  - **6 or fewer players:** 1 spy
  - **7-9 players:** 1-2 spies (2 recommended for Spyfall 2)
  - **10+ players:** 2 spies (Spyfall 2 only)

#### Setup Procedure
1. Dealer (most suspicious-looking player in Round 1) shuffles location bags
2. Dealer randomly selects one location deck
3. Dealer shuffles the 8-card deck
4. Dealer distributes one card face-down to each player (extras returned to bag)
5. Players secretly look at their cards
6. **Non-spies:** Note the location and their specific role
7. **Spy:** Notes they have the spy card (no location/role)
8. All players study the location reference sheet before first game

#### Location Examples (26 Total)
- Airplane, Bank, Beach, Casino, Circus Tent
- Corporate Party, Crusader Army, Day Spa, Embassy
- Hospital, Hotel, Military Base, Movie Studio, Ocean Liner
- Passenger Train, Pirate Ship, Polar Station, Police Station
- Restaurant, School, Service Station, Space Station
- Submarine, Supermarket, Theater, University

### 2. COMPLETE GAME FLOW

#### Round Start
1. Start 8-minute timer
2. Dealer begins by asking ANY player a question

#### Questioning Mechanics (UNIQUE TO SPYFALL)

**Question Rules:**
- **Format:** Questions about the location (e.g., "Is this a place where children are welcome?")
- **Asking:** Dealer asks first, then questioned player asks next (chain continues)
- **Restrictions:**
  - NO follow-up questions allowed
  - Cannot ask the person who just asked you
  - Questions should be open-ended, not yes/no only
- **Answers:** No restrictions on answer format (can be evasive, detailed, creative)

**Strategic Considerations:**
- Non-spies try to prove they know the location without revealing it
- Spy tries to ask/answer plausibly without knowing location
- Too-specific questions reveal location to spy
- Too-vague answers make you look like the spy

#### Round Ending Conditions (THREE WAYS)

**Ending #1: 8-Minute Timer Expires**
1. Timer runs out
2. Starting with dealer, each player makes ONE accusation (going around circle)
3. For each accusation:
   - Accuser names a suspect
   - All other players (except suspect) vote yes/no
   - **Vote must be UNANIMOUS to convict**
   - If not unanimous, continue to next accuser
4. If someone convicted: Reveal card
   - **Spy card:** Non-spies win, score points
   - **Location card:** Spy wins, scores 4 points
5. If nobody convicted: Spy wins, scores 2 points

**Ending #2: Mid-Round Accusation**
1. Any player can stop the clock ONCE per round
2. Player declares a suspect and asks others to vote
3. All players except suspect vote yes/no
4. **Vote must be UNANIMOUS to convict**
5. If unanimous:
   - Reveal card (same scoring as Ending #1)
6. If NOT unanimous:
   - Restart clock
   - Accuser loses their accusation privilege
   - Accuser can still accuse after timer expires

**Ending #3: Spy Self-Reveal**
1. Spy can stop clock at any time (except during another player's accusation)
2. Spy reveals their spy card
3. Spy attempts to guess the location
4. Spy chooses from 26 locations on reference sheet
5. **Correct guess:** Spy wins, scores 4 points
6. **Wrong guess:** Non-spies win, score points

### 3. SCORING SYSTEM

**Spy Victory Scoring:**
- **2 points:** Spy never accused (timer expired, no convictions)
- **4 points:** Non-spy wrongly convicted
- **4 points:** Spy correctly guessed location after revealing

**Non-Spy Victory Scoring:**
- **1 point:** Each non-spy player receives 1 point
- **2 points:** Player who initiated successful accusation receives 2 points (instead of 1)
- **0 points:** If spy wins

**Game Length:**
- **Recommended:** 5 rounds (approximately 1 hour)
- **Tournament:** Track cumulative scores
- **Winner:** Highest score after agreed number of rounds

### 4. ROLE CARDS (OPTIONAL ROLEPLAY)

Each location card shows a specific role at that location:

**Example - Airplane Roles:**
- First Class Passenger
- Air Marshal
- Mechanic
- Economy Class Passenger
- Flight Attendant
- Co-Pilot
- Captain

**Roleplay Option:**
Players can agree beforehand to roleplay their positions (or ignore roles)

### 5. SUBSEQUENT ROUNDS

- Previous round's spy becomes next dealer
- New location deck selected randomly
- Scores accumulate across rounds

### 6. SPYFALL-SPECIFIC EDGE CASES

**What if everyone accuses different people after timer expires?**
- If no unanimous conviction achieved, spy wins (2 points)

**Can the spy stop the clock to accuse someone else?**
- No. Spy can only stop clock to reveal and guess location.

**What if two spies in play (Spyfall 2)?**
- Both spies win/lose together
- If one spy caught, the other is also eliminated
- Spies don't know each other's identity

**Can players take notes?**
- Rules don't prohibit it, but discouraged as it slows gameplay

**What if someone accidentally reveals the location?**
- Not officially addressed; house rule needed
- Common approach: That player is obviously not the spy, round continues

---

## The Chameleon Rules (Complete)

**Official Sources:**
- [Big Potato Games - How to Play The Chameleon](https://bigpotato.com/blogs/blog/how-to-play-the-chameleon-instructions)
- [UltraBoardGames The Chameleon Rules](https://www.ultraboardgames.com/the-chameleon/game-rules.php)
- [Official Game Rules The Chameleon](https://officialgamerules.org/game-rules/the-chameleon/)

### KEY DIFFERENCES FROM GENERIC IMPOSTER

**Major Distinctions:**
1. **Dice & Code Card Mechanic** - coordinates determine secret word
2. **Chameleon gets one guess** after being caught
3. **Structured scoring system** - first to 5 points wins
4. **Topic Cards** - 16 words visible to everyone, only one is secret
5. **Dealer tiebreaker** - specific tie resolution rule

### 1. SETUP

#### Components
- **Blue Code Cards** (one set)
- **Green Code Cards** (one set)
- **1 Blue Chameleon Card**
- **1 Green Chameleon Card**
- **Yellow 6-sided die**
- **Blue 8-sided die**
- **Topic Cards** (double-sided, 16 words per side)

#### Player Count
- **Standard:** 4-6 players
- **3-Player Variant:** Special rules (see below)
- **7-8 Player Variant:** Special rules (see below)

#### Setup Procedure
1. Choose Blue or Green card set for the round
2. Take matching Code Cards + Chameleon Card
3. Shuffle Chameleon Card into Code Cards
4. Deal one card face-down to each player
5. Players secretly look at their card
6. Dealer reveals a Topic Card in center of table
7. Dealer rolls yellow and blue dice

### 2. CODE CARD SYSTEM (UNIQUE MECHANIC)

**How It Works:**
1. **Yellow die** shows a number (1-6) = Row coordinate
2. **Blue die** shows a number (1-8) = Column coordinate
3. **Example:** Yellow = 3, Blue = 6 → Coordinate is "3-6"

**For Non-Chameleon Players:**
1. Look at your Code Card
2. Find the coordinate (e.g., Row 3, Column 6)
3. The coordinate shows a grid position (e.g., "A4", "B2", "D7")
4. Look at the Topic Card
5. Find the word at that grid position (e.g., position B3 = "Basketball")
6. **This is the secret word**

**For the Chameleon:**
1. Chameleon has the Chameleon Card (not a Code Card)
2. Chameleon sees the Topic Card but doesn't know which word is secret
3. Chameleon sees 16 possible words, must deduce the correct one from clues

**Example Topic Card Layout:**
```
        A          B           C          D
1    Apple      Dog         Car        Tree
2    Pizza      Cat         Truck      Flower
3    Banana     Bird        Bus        Plant
4    Burger     Fish        Train      Grass
```
If dice show coordinate leading to B2, secret word is "Cat"

### 3. COMPLETE GAME FLOW

#### Phase 1: Clue-Giving

**Starting Player:** Dealer goes first
**Turn Order:** Clockwise

**Clue Rules:**
- **ONE WORD** per player related to secret word
- **Cannot say the secret word itself**
- **Strategy Balance:**
  - Too obvious: Chameleon figures out the word
  - Too vague: You look like the Chameleon

**Example Round:**
- Secret Word: "Basketball"
- Player 1: "Sport"
- Player 2: "Orange"
- Player 3 (Chameleon): "Round" (improvising)
- Player 4: "Hoops"
- Player 5: "NBA"

#### Phase 2: Discussion

**Timing:** After all players give one-word clues
**Duration:** Flexible (usually 2-4 minutes)

**Activities:**
- Players debate who the Chameleon is
- Point out suspicious clues
- Defend your own clue
- Form alliances
- Accuse others

#### Phase 3: Voting

**Voting Method:**
1. Someone calls for a vote (usually after discussion)
2. On count of three, everyone points at their suspect
3. Count votes for each player
4. Player with **most votes** is accused

**Tie Resolution:**
- **Official Rule:** Dealer for that round breaks the tie
- Dealer chooses which tied player to accuse

#### Phase 4: Card Reveal & Chameleon Guess

**If Accused Player has Code Card:**
1. Flip card to show it's a Code Card
2. **Chameleon escaped!**
3. Chameleon scores 2 points
4. Others score 0 points
5. Round ends

**If Accused Player has Chameleon Card:**
1. Flip card to show Chameleon Card
2. **Chameleon caught!**
3. Chameleon gets **ONE GUESS** at the secret word
4. Chameleon chooses from the 16 words on Topic Card

**Chameleon Guess Outcomes:**
- **Correct Guess:**
  - Chameleon scores 1 point
  - All others score 0 points
  - (Chameleon still "escapes" with reduced points)
- **Wrong Guess:**
  - Chameleon scores 0 points
  - All other players score 2 points

### 4. SCORING SYSTEM

| Outcome | Chameleon Points | Other Players Points |
|---------|------------------|---------------------|
| Chameleon not caught | 2 | 0 each |
| Chameleon caught, guesses correctly | 1 | 0 each |
| Chameleon caught, guesses wrong | 0 | 2 each |

**Winning the Game:**
- **First player to 5 points wins**
- Typically takes 3-5 rounds

### 5. SUBSEQUENT ROUNDS

1. Chameleon from previous round becomes dealer
2. Shuffle Chameleon Card back into Code Cards
3. Deal new cards
4. Reveal new Topic Card
5. Roll dice for new coordinates

### 6. VARIANT RULES

#### 3-Player Variant
**Rule Change:** Chameleon gets **TWO GUESSES** if caught (instead of one)
**Reason:** Harder to hide with fewer players

#### 7-8 Player Variant
**Rule Change:** After clue-giving phase, dealer turns Topic Card **face-down**
**Reason:** Makes it much harder for Chameleon to guess from 16 words (must remember them)
**Impact:** Significantly increases difficulty for Chameleon

### 7. THE CHAMELEON-SPECIFIC EDGE CASES

**What if Chameleon says the secret word during clues?**
- Not officially addressed
- Common house rule: Chameleon is immediately revealed and loses (0 points)

**What if non-Chameleon accidentally says secret word?**
- Not officially addressed
- Common approach: That player is obviously not Chameleon, continue round

**What if unanimous vote (everyone agrees)?**
- Dealer tiebreaker not needed
- Proceed directly to card reveal

**What if Chameleon votes for themselves?**
- Allowed but strategically poor
- Could be a bluffing tactic

**Can you reuse the same Topic Card side?**
- Rules don't prohibit it
- Recommended to flip or use different cards for variety

---

## Undercover Rules (Complete)

**Official Sources:**
- [Yanstar Studio - Undercover Official Rules](https://www.yanstarstudio.com/undercover-how-to-play)
- [Undercover Game Official Rules](https://www.undercovergame.com/rules)

### KEY DIFFERENCES FROM GENERIC IMPOSTER

**Major Distinctions:**
1. **Three distinct roles** - Civilians, Undercover, Mr. White
2. **Mr. White has NO WORD** - must improvise completely
3. **Mr. White guess mechanic** - can win by guessing word when eliminated
4. **Elimination-based** - players removed each round until victory
5. **Supports 3-20 players** - highly scalable

### 1. SETUP

#### Player Count
- **Minimum:** 3 players
- **Maximum:** 20 players
- **Optimal:** 6-12 players

#### Role Distribution

**Three Roles:**

1. **Civilians (Majority)**
   - Receive the same secret word
   - Goal: Eliminate all Undercovers and Mr. Whites
   - Win: 2 points

2. **Undercover (Minority)**
   - Receive a DIFFERENT but related word
   - Don't know they're Undercover at first
   - Goal: Survive until only 1 Civilian remains
   - Win: 10 points

3. **Mr. White (Optional Role)**
   - Receives NO WORD at all
   - Must improvise descriptions
   - Goal: Survive OR guess Civilians' word when eliminated
   - Win: 6 points (if survives) or instant win (if guesses correctly)

**Example Word Pairs:**
- Civilians: "Apple" / Undercover: "Orange"
- Civilians: "Spider-Man" / Undercover: "Batman"
- Civilians: "Basketball" / Undercover: "Football"
- Mr. White: [NO WORD]

#### Setup Procedure
1. Select word pair (or single word if including Mr. White)
2. App/moderator assigns roles randomly
3. Players view roles privately
4. Game begins

### 2. COMPLETE GAME FLOW

**Structure:** Repeating 3-phase cycle until win condition met

#### Phase 1: Description Phase

**Turn Order:** Random starting player, then clockwise

**Description Rules:**
- Each player describes their word using **"a word or phrase"**
- **Civilians:** Describe their word specifically enough to prove knowledge
- **Undercover:** Describe their different word (not knowing it's different initially)
- **Mr. White:** Improvises generic descriptions that could fit anything

**Strategic Considerations:**
- Civilians want to give clues that prove they know the word but don't reveal it to Undercover/Mr. White
- Undercover wants to give clues that fit both their word and possibly the Civilians' word
- Mr. White wants to give extremely vague clues while gathering intel

**Example Round:**
- Civilians' Word: "Dog"
- Undercover's Word: "Cat"
- Mr. White: [no word]

| Player | Role | Clue |
|--------|------|------|
| Player 1 | Civilian | "Loyal pet" |
| Player 2 | Undercover | "Furry companion" |
| Player 3 | Civilian | "Man's best friend" |
| Player 4 | Mr. White | "Common animal" |
| Player 5 | Civilian | "Barks" |

#### Phase 2: Discussion Phase

**Activities:**
- Players openly debate who might be Undercover or Mr. White
- Point out inconsistencies in descriptions
- Form alliances
- Gather more clues about words
- **Mr. White tries to deduce the Civilians' word from discussion**

**Duration:** Flexible, no official time limit

**Strategic Goals by Role:**
- **Civilians & Undercover:** Discover their identity (whether they're Civilian or Undercover)
- **Civilians:** Build alliances, identify enemies
- **Undercover:** Realize they're Undercover, blend in
- **Mr. White:** Figure out Civilians' secret word

#### Phase 3: Elimination Phase (Voting)

**Voting Method:**
1. All remaining players vote
2. Each player votes for ONE person to eliminate
3. Count votes
4. **Player with most votes is eliminated**

**Tie Handling:**
- Not officially specified in rules
- Common implementations: revote, random selection, or no elimination

**Elimination & Role Reveal:**
1. Eliminated player's role is revealed to all
2. **Special Rule for Mr. White:**
   - If Mr. White eliminated, they get **ONE GUESS** at Civilians' word
   - **Correct Guess:** Mr. White wins immediately (entire game)
   - **Wrong Guess:** Mr. White is out, game continues

**After Elimination:**
- Return to Phase 1 (Description) with remaining players
- Repeat cycle until win condition met

### 3. WIN CONDITIONS

**Civilians Win:**
- **Condition:** All Undercovers AND all Mr. Whites are eliminated
- **Scoring:** Each Civilian earns 2 points

**Infiltrators Win (Undercover + Mr. White):**
- **Condition:** Infiltrators survive until only 1 Civilian remains
- **Scoring:**
  - Undercover: 10 points
  - Mr. White: 6 points (if survives to end)

**Mr. White Special Win:**
- **Condition:** Mr. White correctly guesses Civilians' word when eliminated
- **Result:** Mr. White wins immediately, everyone else loses
- **Scoring:** Mr. White earns 6 points

### 4. MR. WHITE STRATEGY

**Key Tactics:**
- Give extremely generic descriptions: "common," "everyday," "noun," "you see it often"
- Listen carefully to all descriptions
- During discussion, ask leading questions to gather info
- Deduce word from patterns in Civilians' descriptions
- Save guess for when you have high confidence

**Example Mr. White Descriptions:**
- "Popular"
- "Well-known"
- "Everyone knows this"
- "Common item"
- "Typical thing"

### 5. SPECIAL ROLES (ADVANCED VARIANT)

Undercover app includes "Special Spirits and Personalities" for added complexity:
- Details vary by app implementation
- Typically add special abilities or rule modifications
- Not part of standard game

### 6. PLAY MODES

**Pass-and-Play Mode:**
- 1 phone/device
- Players physically in same room
- Each player views role privately, then passes device

**Private Room Mode:**
- Each player on own device
- Can be physically together or remote
- Host creates room, shares code

**Public Room Mode:**
- Online matchmaking
- Play with strangers
- Automated role assignment

### 7. UNDERCOVER-SPECIFIC EDGE CASES

**What if Undercover realizes they're Undercover?**
- They should continue playing, trying to survive
- They can help identify Mr. White while protecting themselves

**What if Civilian is voted out first?**
- Game continues
- Reduces Civilian majority, makes it harder for Civilians to win

**What if there are multiple Undercovers?**
- They don't know each other's identity
- Each plays independently
- All must be eliminated for Civilians to win

**What if Mr. White says the Civilians' word during description?**
- Not officially addressed
- Common house rule: Mr. White is immediately revealed and eliminated, no guess allowed

**Can Mr. White guess when eliminated mid-discussion instead of during vote?**
- Rules specify guess happens when "voted out" during Elimination Phase
- No mention of guessing during other eliminations

---

## Insider Rules (Complete)

**Official Sources:**
- [UltraBoardGames Insider Rules](https://www.ultraboardgames.com/insider/game-rules.php)
- [Oink Games Insider](https://oinkgames.com/en/games/analog/insider/)

### KEY DIFFERENCES FROM GENERIC IMPOSTER

**Major Distinctions:**
1. **Combines 20 Questions with social deduction**
2. **Two-phase structure:** Word-guessing THEN imposter-finding
3. **Yes/No questions only** - no open-ended clues
4. **Sand timer** - strict time pressure
5. **Judge role** - one player knows word, answers questions
6. **Insider secretly knows word** - tries to guide without being obvious

### 1. SETUP

#### Components
- **42 theme cards** (words to guess)
- **8 role cards** (Judge, Insider, Citizens)
- **Sand timer**
- **Judge's tile** (for marking card)

#### Player Count
- **Minimum:** 4 players
- **Maximum:** 8 players
- **Optimal:** 5-7 players

#### Roles

**Judge (1 player):**
- Knows the secret word
- Answers yes/no questions
- Revealed role (everyone knows who Judge is)
- Wins with Citizens if Insider caught

**Insider (1 player):**
- Secretly knows the word (like Judge)
- Hidden role (players don't know who Insider is)
- Tries to guide Citizens to correct answer without being obvious
- Wins if not caught OR if word not guessed

**Citizens (Remaining players):**
- Don't know the word
- Ask yes/no questions to figure it out
- Win if they guess word AND catch Insider

#### Setup Procedure
1. Collect role tiles matching player count (always include Judge + Insider)
2. Shuffle and distribute role tiles face-down
3. Judge reveals their role to everyone
4. Other players keep roles secret
5. Shuffle theme deck

### 2. COMPLETE GAME FLOW

#### Phase 1: Theme Selection

1. Judge instructs all players (except Judge) to close eyes
2. Judge reveals top theme card
3. Judge taps Insider on shoulder (or signals them to open eyes)
4. **Insider opens eyes, sees the word**
5. Judge places card face-down, marks it with Judge's tile
6. All players open eyes

**Both Judge and Insider now know the word; Citizens do not.**

#### Phase 2: Questions Phase (MAIN GAMEPLAY)

**Starting the Timer:**
- Flip sand timer (5 minutes typical)
- Citizens and Insider ask questions

**Question Rules:**
- **Format:** Questions must be answerable with "Yes," "No," or "I don't know"
- **Judge answers** all questions
- **Anyone can ask** (Citizens and Insider)
- **No turn order** - freeform questioning
- **No limit** on number of questions

**Strategic Dynamics:**
- **Citizens:** Ask questions to narrow down the word
- **Insider:** Asks strategic questions to guide Citizens toward answer WITHOUT being obvious
- **Judge:** Answers honestly, watches for who might be Insider

**Example Question Round:**
- Word: "Basketball"
- Citizen 1: "Is it alive?" → Judge: "No"
- Citizen 2: "Is it a sport?" → Judge: "Yes"
- Insider: "Is it played indoors?" → Judge: "Yes" (helpful leading question)
- Citizen 3: "Is it soccer?" → Judge: "No"
- Citizen 2: "Is it basketball?" → Judge: "Yes!"

**Round Outcomes:**

**SUCCESS:** Someone guesses the word correctly within time limit
- Note who asked the winning question
- Proceed to Phase 3

**FAILURE:** Timer runs out without correct guess
- **Everyone loses** (Judge, Citizens, Insider all lose)
- Insider is revealed
- Game over

#### Phase 3: Discussion Phase

**Timing:** Remaining sand in timer (flip if needed)
**Duration:** Until timer expires

**Activities:**
- Judge and Citizens discuss who might be the Insider
- Analyze question patterns:
  - Who asked leading questions?
  - Who seemed to know too much?
  - Who asked unhelpful questions?
  - Who asked the winning question?
- **Insider tries to deflect suspicion**

#### Phase 4: Voting

**Voting Method:**
1. When discussion ends (timer or group decision), call for vote
2. All players (including Judge and Insider) vote simultaneously
3. Point at suspected Insider on count of three

**Vote Counting:**
- Count votes for each player
- **Player with most votes is accused**

**Tie Resolution:**
- **Official Rule:** Whoever correctly guessed the word breaks the tie
- If guesser not involved in tie, unclear (house rule needed)

#### Phase 5: Reveal & Results

**Accused player reveals their role card:**

**If Insider Revealed:**
- **Judge and Citizens WIN**
- Insider loses

**If Citizen Revealed (wrong accusation):**
- **Insider WINS**
- Judge and Citizens lose

### 3. WIN CONDITIONS SUMMARY

| Scenario | Citizens & Judge Win? | Insider Wins? |
|----------|----------------------|---------------|
| Word NOT guessed in time | ❌ | ❌ |
| Word guessed, Insider caught | ✅ | ❌ |
| Word guessed, Citizen wrongly accused | ❌ | ✅ |

### 4. INSIDER-SPECIFIC EDGE CASES

**What if Insider asks the winning question?**
- Allowed but extremely risky
- Makes Insider very obvious
- Citizens should heavily suspect the person who guessed it

**What if Judge accidentally gives wrong answer?**
- Not addressed in rules
- House rule needed (common: retract immediately and correct)

**What if multiple people guess simultaneously?**
- First person to speak gets credit
- If truly simultaneous, group decides (or both credited)

**Can players take notes?**
- Not prohibited, but slows game
- App versions often show question history

**What if nobody asks questions (silence)?**
- Time runs out, everyone loses
- Unlikely in practice

---

## Comparative Analysis

### Game Comparison Matrix

| Feature | Generic Imposter | Spyfall | The Chameleon | Undercover | Insider |
|---------|------------------|---------|---------------|------------|---------|
| **Player Count** | 3-12 | 3-8 (12 in v2) | 4-6 (3,7-8 variants) | 3-20 | 4-8 |
| **Clue Format** | One word/phrase | Questions & answers | One word | Word/phrase | Yes/No questions |
| **Imposter Knowledge** | Different word OR blank | Nothing (spy) | Sees 16 options | Different word OR blank (Mr. White) | Full knowledge (Insider) |
| **Voting System** | Simple majority | Unanimous OR majority | Simple majority, dealer breaks ties | Simple majority | Simple majority, guesser breaks ties |
| **Timer** | Optional | 8 minutes strict | None (optional) | None (optional) | Sand timer (5 min) |
| **Scoring** | Points per round | Cumulative points | First to 5 wins | Points per round | Win/loss only |
| **Elimination** | One vote at end | Accusations during play | One vote at end | Repeated eliminations | One vote at end |
| **Imposter Guess** | Optional rule | Spy can reveal & guess location | Chameleon guesses if caught | Mr. White guesses if eliminated | N/A |
| **Multiple Rounds** | Optional | 5 rounds recommended | Until someone hits 5 points | Elimination cycles | Single round |
| **Physical Components** | None (digital/oral) | 208 cards | Cards, dice, code cards | None (app-based) | Cards, timer |
| **Complexity** | Low | Medium | Medium | Medium | Medium-High |

### Core Mechanic Comparison

#### Clue-Giving Mechanics

**Generic Imposter / The Chameleon / Undercover:**
- Players give **descriptive clues** about their word
- Format: One word or short phrase
- Goal: Prove you know the word without revealing it

**Spyfall:**
- Players ask and answer **questions**
- Format: Open-ended questions about location
- Goal: Prove you know the location through questions/answers

**Insider:**
- Players ask **yes/no questions** to guess the word
- Format: Deductive questions answered by Judge
- Goal: Citizens guess word; Insider guides subtly

#### Win Condition Comparison

**Majority Wins (Civilians/Non-Spies):**
- **Generic:** Eliminate all imposters
- **Spyfall:** Catch spy OR spy fails to guess location
- **Chameleon:** Catch Chameleon AND Chameleon fails to guess
- **Undercover:** Eliminate all Undercover + Mr. White
- **Insider:** Guess word AND catch Insider

**Minority Wins (Imposters/Spy/Chameleon):**
- **Generic:** Survive OR guess word
- **Spyfall:** Avoid detection (2pts) OR wrong accusation (4pts) OR guess location (4pts)
- **Chameleon:** Avoid detection (2pts) OR guess word when caught (1pt)
- **Undercover (Undercover):** Survive until 1 Civilian left
- **Undercover (Mr. White):** Survive until 1 Civilian left OR guess word when eliminated
- **Insider:** Avoid detection OR word not guessed in time

### Voting System Comparison

| Game | Voting Type | Tie Resolution | Timing |
|------|-------------|----------------|--------|
| Generic Imposter | Simple majority | Not specified (house rule) | After 2-3 clue rounds |
| Spyfall | **Unanimous** (or majority variant) | N/A (unanimous only) | Any time (accusations) OR at 8min |
| The Chameleon | Simple majority | **Dealer breaks tie** | After clue + discussion |
| Undercover | Simple majority | Not specified | After each description cycle |
| Insider | Simple majority | **Word-guesser breaks tie** | After guessing success |

**Key Insight:** Voting systems vary significantly:
- **Spyfall** is strictest (unanimous required)
- **The Chameleon** has clearest tie rule (dealer decides)
- **Most games** don't specify tie handling

---

## Edge Cases Handbook

### Universal Edge Cases (Apply to All Variants)

#### 1. Player Says the Secret Word During Clues

**Official Rules:** NOT addressed in any game
**Common House Rules:**
- **Option A:** Player automatically eliminated (obviously not imposter if Civilian)
- **Option B:** Round ends, restart with new word
- **Option C:** Player considered "confirmed Civilian," continue
- **Option D:** No penalty, continue (word is out)

**Recommendation:** Decide before game starts

#### 2. Vote Ties

**Official Rules by Game:**
- **Spyfall:** N/A (unanimous voting)
- **The Chameleon:** Dealer breaks tie ✅
- **Insider:** Word-guesser breaks tie ✅
- **Generic Imposter:** Not specified
- **Undercover:** Not specified

**Common House Rules for Unspecified:**
- Revote between tied players
- Random selection (coin flip, die roll)
- Moderator/host decides
- No elimination (advantage imposters)
- All tied players eliminated (extreme)

#### 3. Player Disconnects/Leaves Mid-Game

**Official Rules:** Not addressed
**Common Approaches:**
- **If imposter:** Reveal role, that imposter caught
- **If civilian:** Continue without them
- **Either role:** Restart round
- **App-based games:** Often have auto-replacement or pause features

#### 4. Multiple Imposters Remain

**Official Rules:** Varies by game
- **Spyfall:** Both spies win/lose together
- **Undercover:** Multiple Undercover/Mr. White can exist, win when 1 Civilian left
- **Generic:** Game continues until all imposters eliminated

**Win Condition:**
- Civilians must eliminate **ALL** imposters to win
- Imposters win when they equal/outnumber Civilians (common threshold)

#### 5. Imposter Gives Perfect Clues

**Official Rules:** Not addressed
**Reality:** Skilled imposters can blend in perfectly
**Not a Rule Violation:** This is valid strategy

**Example:** In Undercover, an Undercover with "Cat" while Civilians have "Dog" can say "furry pet" (fits both)

#### 6. Player Reveals Role Accidentally

**Official Rules:** Not addressed
**Common Approaches:**
- If Civilian reveals: Continue (everyone knows they're not imposter)
- If imposter reveals accidentally: Imposter loses, round over
- Either: Restart round with new roles

#### 7. Imposter Guessing

**When Imposter Can Guess:**
- **Spyfall:** Spy can reveal and guess location any time
- **The Chameleon:** Only if caught by vote
- **Undercover (Mr. White):** Only if eliminated by vote
- **Generic Imposter:** Varies (some variants allow, others don't)

**Guess Limits:**
- **Spyfall:** Choose from 26 locations
- **The Chameleon:** Choose from 16 words on Topic Card
- **Undercover:** Open-ended guess of Civilians' word
- **Generic:** Usually from word list/category

**Number of Guesses:**
- **Standard:** ONE guess only
- **The Chameleon (3 players):** TWO guesses

#### 8. Running Out of Time (Timed Games)

**Spyfall (8-minute timer):**
- Timer expires → Accusation round with each player
- If no unanimous conviction → Spy wins (2 points)

**Insider (sand timer):**
- Timer expires in guessing phase → Everyone loses
- Timer expires in discussion → Vote happens anyway

**Generic Imposter:**
- Usually no official timer
- Optional phase timers can be added

### Game-Specific Edge Cases

#### Spyfall Edge Cases

**9. Can Spy Ask Questions?**
- **Yes:** Spy participates in questioning like everyone else
- **Strategy:** Ask vague questions that could apply to many locations

**10. What if Location is Accidentally Revealed?**
- **Not addressed officially**
- **Common:** Round ends, spy loses (can't guess already-revealed location)

**11. Can Player Stop Clock Multiple Times?**
- **No:** Each player can stop clock **ONCE** per round for accusation
- If accusation fails (not unanimous), can still accuse after timer expires

**12. Two Spies in Spyfall 2 - Do They Know Each Other?**
- **No:** Spies don't know each other's identity
- **Strategy:** Spies can accidentally accuse each other

#### The Chameleon Edge Cases

**13. Can You Reuse Same Topic Card?**
- **Not prohibited**
- **Recommended:** Flip to other side or use different card for variety

**14. What if Chameleon Rolls the Dice?**
- **Not addressed**
- **Common:** Dealer rolls (who might be Chameleon)
- **Doesn't matter:** Chameleon still can't use coordinates without Code Card

**15. 7-8 Player Variant - When is Card Flipped Down?**
- **Timing:** After all players give clues, before discussion
- **Purpose:** Chameleon can't reference Topic Card when guessing

**16. Can Non-Chameleon See Chameleon Card?**
- **No:** All cards dealt face-down
- **Only revealed:** When player accused and must flip card

#### Undercover Edge Cases

**17. When Does Undercover Realize They're Undercover?**
- **Gradual:** Usually after hearing other players' descriptions
- **Strategic Moment:** Undercover realizes their word is different
- **Not Immediate:** May take 1-2 description rounds

**18. Can Mr. White Win After Eliminated if Infiltrators Win Later?**
- **No:** Mr. White's guess is their **only** win chance when eliminated
- **If guess fails:** Mr. White is out and cannot win later

**19. Multiple Undercovers - Do They Know Each Other?**
- **No:** Undercovers don't know each other (like spies in Spyfall)
- **Discovery:** They realize they're Undercover independently

**20. What if All Civilians Eliminated Before Infiltrators?**
- **Infiltrators Win:** Meet win condition (0 or 1 Civilian remaining)

#### Insider Edge Cases

**21. Can Citizens Refuse to Guess?**
- **Allowed but counterproductive**
- **If nobody guesses:** Timer runs out, everyone loses

**22. What if Judge is Suspected?**
- **Cannot happen:** Judge role is revealed (everyone knows who Judge is)
- **Judge cannot be Insider**

**23. Can Insider Vote for Themselves?**
- **Yes, strategically:** To appear innocent
- **Result:** Unlikely to be majority vote

**24. What if Question is Ambiguous?**
- **Judge interpretation:** Judge decides how to answer
- **Can say:** "I don't know" if genuinely ambiguous

---

## Common Variations & House Rules

### Variation Categories

#### 1. Clue Format Variations

**Standard:** One word only
**Variations:**
- **Short Phrases:** 3-5 words allowed
- **Full Sentences:** Complete descriptions allowed
- **Gestures Allowed:** Physical acting/pointing (keep muted though)
- **No Synonyms Rule:** Explicitly prohibit synonyms (standard in many)
- **Category Restriction:** Clues must fit specific format (adjectives only, verbs only, etc.)

#### 2. Imposter Type Variations

**Standard:** Imposters get related word
**Variations:**
- **Blank Role (Mr. White):** Imposter gets NO word
- **Double Imposter:** Two imposters, don't know each other
- **Triple Threat:** Three roles (Civilian, Undercover with related word, Blank with no word)
- **Team Imposters:** Imposters know each other's identity
- **Reverse:** Imposter knows word, Civilians have different words (rare)

#### 3. Voting Variations

**Standard:** Simple majority vote
**Variations:**
- **Unanimous:** Must all agree (like Spyfall)
- **Supermajority:** Requires 2/3 or 3/4 vote
- **Multiple Votes:** Vote out 2+ players per round
- **Vote by Logic:** Score points for convincing arguments even if wrong
- **No Elimination:** Just scoring based on votes, play fixed rounds
- **Blind Voting:** Write votes secretly, reveal simultaneously

#### 4. Scoring Variations

**Standard:** Points per round, first to X wins
**Variations:**
- **Roles Rotate:** Everyone plays each role once
- **Cumulative Points:** Track across many rounds
- **Best of X:** First to 3/5/7 round wins
- **Time-Based:** Most points in 30/60 minutes
- **Survival Tracking:** Track how often you survive as imposter

#### 5. Timer Variations

**Standard:** No timer OR fixed timer (varies by game)
**Variations:**
- **Phase Timers:** 30sec per clue, 3min discussion, 1min voting
- **Speed Round:** 3-minute total limit
- **Extended:** 15-20 minutes for large groups
- **Dynamic:** Timer reduces each round (10min → 8min → 6min)

#### 6. Word Selection Variations

**Standard:** Random word selection
**Variations:**
- **Category Mode:** Pick category first (animals, food, movies)
- **Difficulty Levels:** Easy/Medium/Hard word lists
- **Themed Nights:** All words from specific theme (80s movies, foods, etc.)
- **Player Suggestions:** Players submit words, moderator picks
- **Sequential Themes:** Related words across rounds (fruits → vegetables → grains)

#### 7. Group Size Variations

**Standard:** 4-8 players
**Variations:**
- **3-Player Minimum:** Special rules (harder for imposter)
- **Large Group Split:** 12+ players split into two simultaneous games
- **Mega Game:** 12-20 players, multiple imposters, longer rounds
- **Pairs Mode:** Players work in pairs (share role, collaborate)

#### 8. Discussion Phase Variations

**Standard:** Freeform discussion
**Variations:**
- **Structured Debate:** Each player gets 30sec to defend themselves
- **No Talking:** Only clues, then silent vote
- **Accuser Speaks First:** Person who called vote explains reasoning
- **Defense Round:** Accused players defend before vote
- **Cross-Examination:** Players can ask direct yes/no questions to suspects

#### 9. Multi-Round Variations

**Standard:** Independent rounds
**Variations:**
- **Campaign Mode:** Carry roles across multiple rounds (if survive)
- **Elimination Tournament:** Losers eliminated from tournament
- **Story Mode:** Narrative connects rounds (app-based)
- **Escalation:** Each round adds complexity (more imposters, harder words)

#### 10. Role Reveal Variations

**Standard:** Role revealed when eliminated/accused
**Variations:**
- **Hidden Roles:** Never reveal roles, just announce winners
- **Delayed Reveal:** Reveal all roles only at end of game
- **Partial Reveal:** Only reveal if Civilian (keep Imposter secret if caught)
- **Public Reveal:** All roles revealed before voting (just for fun variant)

---

## Implementation Validation Checklist

Use this checklist to validate your imposter game implementation against official rules.

### Core Mechanics Validation

#### Setup & Configuration
- [ ] Configurable player count (3-20 range)
- [ ] Configurable number of imposters (1-3 based on player count)
- [ ] Role assignment options:
  - [ ] Standard Imposter (related word)
  - [ ] Blank role (no word)
  - [ ] Undercover variant (two different words)
- [ ] Word selection methods:
  - [ ] Random from list
  - [ ] Category-based
  - [ ] Manual input
  - [ ] Related word pairs (for Undercover mode)

#### Game Flow
- [ ] Round structure configurable:
  - [ ] Number of clue rounds before voting (default 2-3)
  - [ ] Optional discussion phase
  - [ ] Voting phase
- [ ] Turn order implementation:
  - [ ] Clockwise rotation
  - [ ] Random order option
  - [ ] Tracks whose turn it is
- [ ] Phase transitions:
  - [ ] Clear indication of phase changes
  - [ ] Cannot skip phases (unless configuration allows)

#### Clue-Giving Mechanics
- [ ] Clue format restrictions:
  - [ ] One-word mode
  - [ ] Phrase mode (optional)
  - [ ] Character/word limits configurable
- [ ] Clue validation:
  - [ ] Cannot be secret word itself (detected/warned)
  - [ ] Optional synonym detection
- [ ] Clue history visible to all players
- [ ] All players must give clue before round ends

#### Voting Mechanics
- [ ] Voting methods supported:
  - [ ] Simple majority (default)
  - [ ] Unanimous (Spyfall mode)
  - [ ] Configurable threshold
- [ ] Tie-breaking rules:
  - [ ] Configurable (dealer, random, revote)
  - [ ] Clear indication of tie situation
- [ ] Vote tallying:
  - [ ] Accurate vote counts
  - [ ] Eliminated player revealed
  - [ ] Role revealed upon elimination

#### Win Condition Detection
- [ ] Civilians win when all imposters eliminated
- [ ] Imposters win when:
  - [ ] Survive until end/majority
  - [ ] Optional: Correctly guess word
- [ ] Clear win/loss announcement
- [ ] Optional: Score tracking across rounds

### Game-Specific Validations

#### Generic Imposter Mode
- [ ] 2-3 clue rounds before voting
- [ ] Simple majority voting
- [ ] Optional imposter guess at end
- [ ] Supports 3-12 players

#### Spyfall Mode
- [ ] Location-based (26 locations or custom)
- [ ] Question & answer format instead of clues
- [ ] 8-minute timer
- [ ] Accusation system (stop clock)
- [ ] Spy can reveal and guess location
- [ ] Unanimous OR majority voting (configurable)
- [ ] Supports 3-8 players (or 3-12 in Spyfall 2 mode)
- [ ] Role cards per location
- [ ] Scoring: 2pts (spy no accusation), 4pts (wrong accusation), 4pts (correct location guess), 1pt per non-spy

#### The Chameleon Mode
- [ ] Dice rolling mechanic (yellow d6, blue d8)
- [ ] Code card coordinate system
- [ ] Topic card with 16 words visible
- [ ] Chameleon sees Topic Card but not coordinate
- [ ] One-word clue format only
- [ ] Simple majority voting
- [ ] Dealer breaks ties
- [ ] Chameleon guess mechanic if caught
- [ ] Scoring system:
  - [ ] Chameleon escapes: 2pts
  - [ ] Caught but correct guess: 1pt Chameleon, 0pts others
  - [ ] Caught and wrong guess: 0pts Chameleon, 2pts others
- [ ] First to 5 points wins
- [ ] 3-player variant: 2 guesses for Chameleon
- [ ] 7-8 player variant: Topic Card face-down after clues
- [ ] Supports 4-6 players (3, 7-8 variants)

#### Undercover Mode
- [ ] Three role types: Civilian, Undercover, Mr. White
- [ ] Civilians and Undercover get different words (related)
- [ ] Mr. White gets no word
- [ ] Word or phrase descriptions allowed
- [ ] Three-phase cycle: Description → Discussion → Elimination
- [ ] Repeated eliminations until win condition
- [ ] Mr. White special guess when eliminated
- [ ] Win conditions:
  - [ ] Civilians: All infiltrators eliminated
  - [ ] Infiltrators: Survive until 1 Civilian left
  - [ ] Mr. White: Guess correctly when eliminated (instant win)
- [ ] Scoring: Civilians 2pts, Mr. White 6pts, Undercover 10pts
- [ ] Supports 3-20 players

#### Insider Mode
- [ ] Role assignment: 1 Judge (revealed), 1 Insider (hidden), rest Citizens
- [ ] Theme selection: Judge and Insider see word, Citizens don't
- [ ] Two-phase gameplay:
  - [ ] Phase 1: Yes/No question guessing (timer)
  - [ ] Phase 2: Insider identification (discussion + vote)
- [ ] Judge answers all questions
- [ ] Timer implementation (sand timer equivalent)
- [ ] Win conditions:
  - [ ] Word not guessed in time: Everyone loses
  - [ ] Word guessed + Insider caught: Citizens & Judge win
  - [ ] Word guessed + Citizen accused: Insider wins
- [ ] Tie-breaking: Word-guesser breaks ties
- [ ] Supports 4-8 players

### Edge Case Handling

#### Critical Edge Cases
- [ ] Player says secret word during clue
  - [ ] Configurable behavior (eliminate, restart, ignore)
- [ ] Vote ties
  - [ ] Configurable resolution (dealer, random, revote, no elimination)
- [ ] Player disconnects/leaves
  - [ ] Graceful handling (reveal role if imposter, continue if civilian)
- [ ] Multiple imposters remaining
  - [ ] Correct win condition logic (all must be caught)
- [ ] Imposter gives perfect clues
  - [ ] Allowed (valid strategy)
- [ ] Imposter guess mechanics
  - [ ] Timing: When allowed (varies by mode)
  - [ ] Guess source: From list/category
  - [ ] Number of guesses: 1 (or 2 in Chameleon 3-player)
  - [ ] Win on correct guess

#### Game-Specific Edge Cases
- [ ] **Spyfall:** Player stops clock multiple times → Prevent (1 per player)
- [ ] **Spyfall:** Location accidentally revealed → Configurable handling
- [ ] **Spyfall:** Two spies don't know each other → Implemented correctly
- [ ] **Chameleon:** Same Topic Card reuse → Allow with warning/tracking
- [ ] **Chameleon:** Dealer tiebreaker → Implemented
- [ ] **Undercover:** Undercover realizes gradually → No forced revelation
- [ ] **Undercover:** Multiple Undercovers don't know each other → Correct implementation
- [ ] **Insider:** Judge answer ambiguity → Judge decides interpretation
- [ ] **Insider:** Insider votes for self → Allowed

### User Experience Validation

#### Clarity & Communication
- [ ] Clear role display (private to player)
- [ ] Clear secret word display (private, appropriate to role)
- [ ] Turn indicators (whose turn, what phase)
- [ ] Phase transitions announced clearly
- [ ] Vote results displayed clearly
- [ ] Win/loss announcements prominent
- [ ] Game history/log available

#### Accessibility
- [ ] Configurable timers (or no timers)
- [ ] Text size options
- [ ] Color-blind friendly design
- [ ] Screen reader compatibility (if digital)
- [ ] Pause/resume functionality

#### Flexibility
- [ ] Configurable rules (house rules support)
- [ ] Custom word lists
- [ ] Adjustable player count
- [ ] Adjustable imposter count
- [ ] Mode selection (different game variants)

### Testing Scenarios

#### Minimum Viable Scenarios
- [ ] **3 players, 1 imposter:** Game completes successfully
- [ ] **4 players, 1 imposter:** Civilians win by catching imposter
- [ ] **4 players, 1 imposter:** Imposter wins by surviving
- [ ] **6 players, 1 imposter:** Multiple clue rounds function correctly
- [ ] **8 players, 2 imposters:** Both imposters must be caught to win
- [ ] **Vote tie:** Tie-breaking rule executes correctly
- [ ] **Imposter guess:** Guess mechanic works, correct guess = imposter wins

#### Advanced Scenarios
- [ ] **Spyfall mode:** Full round with accusations, timer, scoring
- [ ] **Chameleon mode:** Dice/code cards, Chameleon guess, scoring to 5
- [ ] **Undercover mode:** Three roles, repeated eliminations, Mr. White guess
- [ ] **Insider mode:** Two-phase gameplay, yes/no questions, Insider caught
- [ ] **Multi-round:** Scores accumulate, roles rotate (if configured)
- [ ] **Edge case battery:** All critical edge cases handled gracefully

---

## Conclusion & Key Takeaways

### What's Consistent Across All Variants

**Universal Mechanics:**
1. **Role asymmetry:** Majority know word, minority don't (or have different word)
2. **Information gathering:** Clues/questions reveal knowledge
3. **Social deduction:** Players deduce roles from behavior
4. **Voting:** Group eliminates suspected imposters
5. **Win conditions:** Majority wins by catching imposters, imposters win by surviving

### What Varies Significantly

**Major Variations:**
1. **Clue format:** One-word vs phrases vs questions vs yes/no
2. **Voting systems:** Simple majority vs unanimous vs supermajority
3. **Tie-breaking:** Dealer, random, revote, or unspecified
4. **Imposter knowledge:** Different word vs blank vs full knowledge (Insider)
5. **Guess mechanics:** When, how, and whether imposters can guess
6. **Elimination:** Single vote vs repeated eliminations
7. **Scoring:** Per-round points vs cumulative vs first-to-X
8. **Timers:** No timer vs phase timers vs round timers

### Critical Implementation Decisions

**To validate your implementation, decide:**

1. **Which variant are you implementing?**
   - Generic (flexible rules)
   - Spyfall (question-based, locations, 8-min timer)
   - The Chameleon (dice/code cards, scoring to 5)
   - Undercover (three roles, eliminations)
   - Insider (two-phase, yes/no questions)
   - Hybrid/Custom

2. **What are your default rules?**
   - Clue format (one word or phrases)
   - Voting system (simple majority or other)
   - Tie resolution
   - Imposter guess timing and method
   - Number of clue rounds before voting
   - Win conditions

3. **What's configurable vs fixed?**
   - Player count range
   - Imposter count ratio
   - House rule variations
   - Timers (optional or required)
   - Scoring system

4. **How do you handle edge cases?**
   - Player says word during clue
   - Vote ties
   - Player disconnects
   - Multiple imposters
   - Imposter perfect play

### Official vs House Rules

**Clearly Official (Documented):**
- The Chameleon: Dealer breaks ties ✅
- Spyfall: Unanimous voting, 8-min timer, spy reveal mechanic ✅
- Insider: Word-guesser breaks ties, two-phase structure ✅
- Undercover: Three roles, Mr. White guess ✅

**Common but Unofficial (House Rules):**
- Synonyms prohibited (common but not always stated)
- Player saying word = elimination (not officially addressed)
- Tie resolution in generic imposter (most games don't specify)
- Number of imposters per player count (general guidelines, not fixed)
- Imposter guess at end (varies by implementation)

### Validation Summary

**Your implementation is accurate if:**
1. ✅ Core mechanics match chosen variant (role asymmetry, clue-giving, voting, win conditions)
2. ✅ Critical rules implemented (voting system, elimination, scoring match variant)
3. ✅ Edge cases handled gracefully (documented behavior for ties, word-saying, disconnects)
4. ✅ Configurable options clearly marked as variants (not claimed as "official")
5. ✅ House rules labeled as such (if deviating from official rules)

**Red Flags (Inaccuracies):**
- ❌ Claiming specific rules are "official" when they're unspecified
- ❌ Mixing variant mechanics without labeling (e.g., Spyfall voting in Chameleon mode)
- ❌ Incorrect win conditions (e.g., imposter wins before all others eliminated)
- ❌ Missing critical mechanics (e.g., Chameleon guess, Mr. White guess, Spy reveal)
- ❌ Unhandled edge cases (game crashes or undefined behavior on ties, word-saying, etc.)

---

## Sources & References

### Primary Official Sources

**Spyfall:**
- [Spyfall Official Rulebook PDF](https://cdn.1j1ju.com/medias/99/c4/5e-spyfall-rulebook.pdf)
- [UltraBoardGames Spyfall Rules](https://www.ultraboardgames.com/spyfall/game-rules.php)
- [Official Game Rules - Spyfall](https://officialgamerules.org/game-rules/spyfall/)
- [Spyfall.app Game Rules](https://www.spyfall.app/gamerules)

**The Chameleon:**
- [Big Potato Games - How to Play The Chameleon](https://bigpotato.com/blogs/blog/how-to-play-the-chameleon-instructions)
- [UltraBoardGames The Chameleon Rules](https://www.ultraboardgames.com/the-chameleon/game-rules.php)
- [Official Game Rules - The Chameleon](https://officialgamerules.org/game-rules/the-chameleon/)
- [BoardGameGeek The Chameleon](https://boardgamegeek.com/boardgame/227072/the-chameleon)

**Undercover:**
- [Yanstar Studio - Undercover Official Rules](https://www.yanstarstudio.com/undercover-how-to-play)
- [Undercover Game Official Rules](https://www.undercovergame.com/rules)

**Insider:**
- [UltraBoardGames Insider Rules](https://www.ultraboardgames.com/insider/game-rules.php)
- [Oink Games Insider](https://oinkgames.com/en/games/analog/insider/)

**Generic Imposter Game:**
- [PlayImposter.com - How to Play](https://playimposter.com/guide/imposter-game/how-to-play/)
- [ImposterGame.net - Game Rules](https://impostergame.net/imposter-game-rules)
- [Game On Family - Imposter Tutorial](https://gameonfamily.com/blogs/tutorials/imposter)
- [WordImpostor.com](https://www.wordimpostor.com/)

**A Fake Artist Goes to New York:**
- [UltraBoardGames A Fake Artist Goes to New York](https://www.ultraboardgames.com/a-fake-artist-goes-to-new-york/game-rules.php)
- [Oink Games A Fake Artist Goes to New York](https://oinkgames.com/en/games/analog/a-fake-artist-goes-to-new-york/)

### Secondary Sources & Community Discussions

**BoardGameGeek Forums:**
- [Spyfall BGG Page](https://boardgamegeek.com/boardgame/166384/spyfall)
- [The Chameleon BGG Page](https://boardgamegeek.com/boardgame/227072/the-chameleon)
- [Spyfall Voting Discussion](https://boardgamegeek.com/thread/1278579/question-about-the-voting)
- [Spyfall Old vs New Rules](https://boardgamegeek.com/thread/1552336/how-voting-works-old-vs-new-rules)

**Strategy & Guides:**
- [PlayImposter.com Group Size Guide](https://playimposter.com/guide/imposter-game/group-size/)
- [PlayImposter.com Blank Role Strategy](https://playimposter.com/guide/imposter-game/blank-role-survival-bible/)
- [ImposterGame.net Ultimate Guide](https://impostergame.net/blog/ultimate-imposter-game-guide)
- [StationeryPal Guess the Imposter Guide](https://stationerypal.com/blogs/how-to/guess-the-imposter-word-game-categories-strategy-amp-how-to-play)

### Wikipedia & General References

- [The Chameleon (party game) - Wikipedia](https://en.wikipedia.org/wiki/The_Chameleon_(party_game))
- [Spyfall (card game) - Wikipedia](https://en.wikipedia.org/wiki/Spyfall_(card_game))

---

**Document Version:** 1.0
**Last Updated:** December 27, 2025
**Compiled By:** Research Agent for phase2 imposter experiment validation
