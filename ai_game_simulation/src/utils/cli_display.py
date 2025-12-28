"""
Visual CLI display for observing the AI imposter game.
Makes the game easy to follow with formatting, colors, and pauses.
"""

import time
from typing import List, Optional
from ..ai.schemas import PlayerRole


# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Roles
    IMPOSTER = '\033[91m'  # Red
    NON_IMPOSTER = '\033[92m'  # Green

    # Actions
    THINKING = '\033[36m'  # Cyan
    SPEAKING = '\033[93m'  # Yellow
    VOTING = '\033[95m'  # Magenta

    # UI Elements
    HEADER = '\033[96m'  # Light cyan
    SUCCESS = '\033[92m'  # Green
    WARNING = '\033[93m'  # Yellow
    ERROR = '\033[91m'  # Red


def clear_screen():
    """Clear terminal screen safely using ANSI escape codes"""
    print('\033[2J\033[H', end='')  # ANSI: clear screen + move cursor to home


def pause(seconds: float = 2.0, message: Optional[str] = None):
    """Pause for dramatic effect"""
    if message:
        print(f"\n{Colors.DIM}{message}{Colors.RESET}")
    time.sleep(seconds)


def print_box(content: str, title: Optional[str] = None, color: str = Colors.RESET):
    """Print content in a box"""
    lines = content.split('\n')
    max_width = max(len(line) for line in lines) if lines else 40
    box_width = min(max_width + 4, 80)

    print(f"\n{color}╔{'═' * (box_width - 2)}╗{Colors.RESET}")

    if title:
        title_padded = f" {title} ".center(box_width - 2, '═')
        print(f"{color}╠{title_padded}╣{Colors.RESET}")

    for line in lines:
        padded = line.ljust(box_width - 4)
        print(f"{color}║{Colors.RESET} {padded} {color}║{Colors.RESET}")

    print(f"{color}╚{'═' * (box_width - 2)}╝{Colors.RESET}\n")


def print_player_circle(players: List, current_speaker: Optional[str] = None, revealed: bool = False):
    """
    Display players in a circle-ish formation using ASCII.

    Args:
        players: List of AIPlayer objects
        current_speaker: ID of player currently speaking (highlight them)
        revealed: Whether to show roles (after game ends)
    """
    print(f"\n{Colors.HEADER}{'='*70}{Colors.RESET}")
    print(f"{Colors.HEADER}👥 PLAYERS{Colors.RESET}")
    print(f"{Colors.HEADER}{'='*70}{Colors.RESET}\n")

    # Display in rows of 3-4 for readability
    rows = []
    row_size = 3
    for i in range(0, len(players), row_size):
        rows.append(players[i:i + row_size])

    for row in rows:
        # Build player display
        player_displays = []
        for player in row:
            # Determine symbol and color
            if revealed:
                symbol = "🎭" if player.role == PlayerRole.IMPOSTER else "✓"
                color = Colors.IMPOSTER if player.role == PlayerRole.IMPOSTER else Colors.NON_IMPOSTER
            else:
                symbol = "●"
                color = Colors.RESET

            # Highlight current speaker
            if player.player_id == current_speaker:
                display = f"{Colors.BOLD}{Colors.SPEAKING}▶ {symbol} {player.player_id} ◀{Colors.RESET}"
            else:
                display = f"  {color}{symbol} {player.player_id}{Colors.RESET}  "

            # Add model info
            display += f" {Colors.DIM}({player.model_name}){Colors.RESET}"

            player_displays.append(display)

        # Print row
        print("  ".join(player_displays))

    print(f"\n{Colors.HEADER}{'='*70}{Colors.RESET}\n")


def print_round_header(round_num: int, total_rounds: int):
    """Print round header"""
    clear_screen()
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔" + "═" * 68 + "╗")
    print(f"║  ROUND {round_num}/{total_rounds}".ljust(69) + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{Colors.RESET}\n")


def print_clue(player_id: str, role: PlayerRole, model: str, clue: str, thinking: str, word_hypothesis: Optional[str] = None, pause_time: float = 3.0):
    """
    Display a single clue with inner monologue.

    Args:
        player_id: Player giving clue
        role: Their role (for color coding)
        model: Model they're using
        clue: The actual clue
        thinking: Inner monologue
        word_hypothesis: For imposters - what they think the word is
        pause_time: How long to pause after displaying
    """
    role_emoji = "🎭" if role == PlayerRole.IMPOSTER else "✓"
    role_color = Colors.IMPOSTER if role == PlayerRole.IMPOSTER else Colors.NON_IMPOSTER

    # Player header
    print(f"\n{role_color}{Colors.BOLD}{role_emoji} {player_id}{Colors.RESET} {Colors.DIM}({model}){Colors.RESET}")

    # The clue (big and prominent)
    print(f"{Colors.SPEAKING}{Colors.BOLD}   Clue: \"{clue}\"{Colors.RESET}")

    # Inner monologue
    print(f"\n{Colors.THINKING}   💭 Inner Thoughts:{Colors.RESET}")
    # Wrap thinking text
    import textwrap
    wrapped = textwrap.fill(thinking, width=65, initial_indent="      ", subsequent_indent="      ")
    print(f"{Colors.DIM}{wrapped}{Colors.RESET}")

    # Imposter hypothesis
    if word_hypothesis:
        print(f"\n{Colors.WARNING}   🤔 Guessing word is: {word_hypothesis}{Colors.RESET}")

    print(f"\n{Colors.DIM}{'─' * 70}{Colors.RESET}")

    pause(pause_time, f"⏸  Pausing {pause_time}s...")


def print_voting_header():
    """Print voting phase header"""
    clear_screen()
    print(f"\n{Colors.VOTING}{Colors.BOLD}")
    print("╔" + "═" * 68 + "╗")
    print("║  🗳️  VOTING PHASE - Who are the imposters?".ljust(69) + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{Colors.RESET}\n")
    pause(2.0, "Everyone is analyzing the clues...")


def print_vote(player_id: str, votes: List[str], thinking: str, reasoning: dict, pause_time: float = 3.0):
    """Display a player's vote"""
    print(f"\n{Colors.BOLD}{player_id}{Colors.RESET} votes:")
    print(f"{Colors.VOTING}   → {', '.join(votes)}{Colors.RESET}")

    print(f"\n{Colors.THINKING}   💭 Analysis:{Colors.RESET}")
    import textwrap
    wrapped = textwrap.fill(thinking, width=65, initial_indent="      ", subsequent_indent="      ")
    print(f"{Colors.DIM}{wrapped}{Colors.RESET}")

    if reasoning:
        print(f"\n{Colors.DIM}   Reasoning:{Colors.RESET}")
        for suspect, reason in list(reasoning.items())[:3]:  # Show top 3
            print(f"{Colors.DIM}      • {suspect}: {reason}{Colors.RESET}")

    print(f"\n{Colors.DIM}{'─' * 70}{Colors.RESET}")
    pause(pause_time / 2)  # Votes go faster than clues


def print_results(result, pause_time: float = 1.0):
    """Print final game results with drama"""
    clear_screen()

    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔" + "═" * 68 + "╗")
    print("║  🏆 GAME RESULTS".ljust(69) + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{Colors.RESET}\n")

    pause(pause_time, "Calculating results...")

    # Secret word reveal
    print_box(
        f"The secret word was: {Colors.BOLD}{result.word.upper()}{Colors.RESET}\nCategory: {result.category}",
        title="SECRET WORD",
        color=Colors.HEADER
    )

    pause(pause_time)

    # Actual imposters
    print(f"\n{Colors.IMPOSTER}{Colors.BOLD}🎭 THE IMPOSTERS WERE:{Colors.RESET}")
    for imp in result.actual_imposters:
        print(f"   • {Colors.IMPOSTER}{imp}{Colors.RESET}")

    pause(pause_time * 1.5)

    # Who was voted out
    print(f"\n{Colors.BOLD}🗳️  PLAYERS VOTED OUT:{Colors.RESET}")
    for elim in result.eliminated_players:
        is_imposter = elim in result.actual_imposters
        color = Colors.SUCCESS if is_imposter else Colors.ERROR
        marker = "✓" if is_imposter else "✗"
        print(f"   {marker} {color}{elim}{Colors.RESET}")

    pause(pause_time * 2)

    # Detection accuracy
    correctly_identified = set(result.eliminated_players) & set(result.actual_imposters)

    accuracy_pct = result.detection_accuracy * 100
    if accuracy_pct == 100:
        color = Colors.SUCCESS
        verdict = "🎉 PERFECT DETECTION! All imposters caught!"
    elif accuracy_pct >= 67:
        color = Colors.SUCCESS
        verdict = "✓ Good detective work! Majority caught."
    elif accuracy_pct > 0:
        color = Colors.WARNING
        verdict = "⚠️  Some caught, but others escaped."
    else:
        color = Colors.ERROR
        verdict = "❌ Imposters completely fooled everyone!"

    print_box(
        f"Accuracy: {accuracy_pct:.1f}%\n{verdict}",
        title="DETECTION SCORE",
        color=color
    )

    # Imposter performance analysis
    if result.all_clues:
        print(f"\n{Colors.IMPOSTER}{Colors.BOLD}🎭 IMPOSTER PERFORMANCE:{Colors.RESET}\n")
        for imp_id in result.actual_imposters:
            imp_clues = [c for c in result.all_clues if c.player_id == imp_id]
            if imp_clues:
                print(f"   {Colors.IMPOSTER}{imp_id}:{Colors.RESET}")
                for clue_rec in imp_clues:
                    hyp = f" (guessed: {clue_rec.word_hypothesis})" if clue_rec.word_hypothesis else ""
                    print(f"      R{clue_rec.round}: \"{clue_rec.clue}\"{hyp}")
                print()


def print_game_setup(config, models_used):
    """Print initial game setup"""
    clear_screen()

    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔" + "═" * 68 + "╗")
    print("║  🎭 THE IMPOSTER MYSTERY - AI Edition".ljust(69) + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{Colors.RESET}\n")

    print_box(
        f"Secret Word: {Colors.BOLD}{config.word.upper()}{Colors.RESET}\n"
        f"Category: {config.category}\n"
        f"Players: {config.num_players} ({config.num_imposters} imposters)\n"
        f"Rounds: {config.num_rounds}",
        title="GAME SETUP",
        color=Colors.HEADER
    )

    # Model info
    print(f"\n{Colors.BOLD}📱 AI Models in this game:{Colors.RESET}")
    for model_key, count in models_used.items():
        print(f"   • {model_key}: {count} player(s)")

    pause(3.0, "Game starting in 3 seconds...")
