"""
Game rule validation and enforcement.
Handles word restrictions, win conditions, and edge cases.
"""

from typing import Optional, Dict, List
from dataclasses import dataclass
from .player import PlayerRole


@dataclass
class ValidationResult:
    """Result of validating a clue or action"""
    valid: bool
    reason: Optional[str] = None
    instant_reveal: bool = False
    game_over: bool = False
    message: Optional[str] = None


def validate_clue(
    clue: str,
    secret_word: str,
    player_id: str,
    role: PlayerRole
) -> ValidationResult:
    """
    Validate a clue according to game rules.

    Rules:
    1. Cannot say the exact secret word
    2. Cannot use direct synonyms (future enhancement)
    3. Must be reasonably short (one word or hyphenated)

    Args:
        clue: The clue given
        secret_word: The actual secret word
        player_id: Who gave the clue
        role: Their role (imposter or not)

    Returns:
        ValidationResult with validation status and consequences
    """

    # Rule 1: Cannot say the exact word
    if clue.lower().strip() == secret_word.lower().strip():
        if role == PlayerRole.IMPOSTER:
            # Imposter said the word - they reveal themselves!
            return ValidationResult(
                valid=False,
                reason="word_match",
                instant_reveal=True,
                game_over=False,  # Game continues without them
                message=f"{player_id} said '{clue}' - the secret word! Imposter revealed and eliminated!"
            )
        else:
            # Non-imposter said the word - rule violation
            return ValidationResult(
                valid=False,
                reason="word_match",
                instant_reveal=False,
                game_over=True,  # Can't continue, word is revealed
                message=f"{player_id} broke the rule by saying the secret word '{clue}'! Game over."
            )

    # Rule 2: Check for word contained in clue (partial match)
    if secret_word.lower() in clue.lower() or clue.lower() in secret_word.lower():
        if len(secret_word) > 3:  # Only check for longer words
            return ValidationResult(
                valid=False,
                reason="partial_word_match",
                instant_reveal=False,
                game_over=False,
                message=f"{player_id}'s clue '{clue}' contains part of the secret word!"
            )

    # Rule 3: Clue length check (warn if too long)
    word_count = len(clue.split())
    if word_count > 3:
        return ValidationResult(
            valid=True,  # Allow but flag
            reason="long_clue",
            message=f"{player_id} gave a {word_count}-word clue ('{clue}'). One word is standard."
        )

    # Clue is valid
    return ValidationResult(valid=True)


@dataclass
class WinCondition:
    """Game end state"""
    game_over: bool
    winner: Optional[str]  # 'civilians', 'imposters', or None
    reason: str
    eliminated_imposters: List[str]
    surviving_imposters: List[str]


def check_win_condition(
    eliminated_players: List[str],
    all_imposters: List[str],
    remaining_players: List[str],
    num_civilians: int
) -> WinCondition:
    """
    Check if game should end based on current state.

    Win Conditions:
    - Civilians win: ALL imposters eliminated
    - Imposters win: Imposters equal or outnumber civilians
    - Game continues: Otherwise

    Args:
        eliminated_players: Players removed from game
        all_imposters: Original list of imposters
        remaining_players: Still in game
        num_civilians: Number of non-imposter players

    Returns:
        WinCondition indicating if game is over and who won
    """

    # Check which imposters are eliminated
    eliminated_imposters = [p for p in eliminated_players if p in all_imposters]
    surviving_imposters = [p for p in all_imposters if p not in eliminated_players]

    # Win Condition 1: All imposters eliminated
    if len(surviving_imposters) == 0:
        return WinCondition(
            game_over=True,
            winner='civilians',
            reason='all_imposters_eliminated',
            eliminated_imposters=eliminated_imposters,
            surviving_imposters=[]
        )

    # Win Condition 2: Imposters equal or outnumber civilians
    remaining_civilians = num_civilians - len([p for p in eliminated_players if p not in all_imposters])

    if len(surviving_imposters) >= remaining_civilians:
        return WinCondition(
            game_over=True,
            winner='imposters',
            reason='imposters_outnumber_civilians',
            eliminated_imposters=eliminated_imposters,
            surviving_imposters=surviving_imposters
        )

    # Game continues
    return WinCondition(
        game_over=False,
        winner=None,
        reason='game_in_progress',
        eliminated_imposters=eliminated_imposters,
        surviving_imposters=surviving_imposters
    )


def resolve_vote_tie(
    tied_players: List[str],
    method: str = "random"
) -> str:
    """
    Resolve a tie in voting.

    Methods:
    - random: Pick randomly (default)
    - first: Alphabetically first player
    - revote: Would require another round (not implemented here)

    Returns:
        Player ID to eliminate
    """
    import random

    if method == "random":
        return random.choice(tied_players)
    elif method == "first":
        return sorted(tied_players)[0]
    else:
        return tied_players[0]
