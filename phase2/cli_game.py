#!/usr/bin/env python3
"""
CLI Interface for Phase 2: AI Imposter Game

Run AI-powered imposter games from the command line.
This is the MVP - proves the concept before building the visual UI.

Usage:
    python cli_game.py --word beach --category nature --players 6 --imposters 2 --rounds 3
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import from src package
import sys
import importlib.util

# Import modules directly
from src.game_engine.engine import GameEngine, GameConfig
from src.ai.openrouter import OpenRouterClient, AVAILABLE_MODELS
from src.utils.cli_display import print_game_setup, print_results as display_final_results

# Setup logging (minimal for visual mode)
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings/errors
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


async def run_cli_game(
    word: str,
    category: str,
    num_players: int = 6,
    num_imposters: int = 2,
    num_rounds: int = 3,
    models: Optional[str] = None
):
    """
    Run a complete game and print results to console.

    Args:
        word: The secret word
        category: Category of the word
        num_players: Total number of players
        num_imposters: Number of imposters
        num_rounds: Number of clue rounds
        models: Comma-separated model keys (e.g., "llama,llama,gemini,haiku")
    """

    # Parse model distribution
    if models:
        model_list = models.split(',')
        if len(model_list) != num_players:
            print(f"Error: Model count ({len(model_list)}) must match players ({num_players})")
            return

        # Count models
        model_dist = {}
        for m in model_list:
            model_dist[m] = model_dist.get(m, 0) + 1

        config = GameConfig(
            word=word,
            category=category,
            num_players=num_players,
            num_imposters=num_imposters,
            num_rounds=num_rounds,
            model_strategy='mixed',
            model_distribution=model_dist
        )
        models_used = model_dist
    else:
        # Default: all use Llama
        config = GameConfig(
            word=word,
            category=category,
            num_players=num_players,
            num_imposters=num_imposters,
            num_rounds=num_rounds,
            model_strategy='single',
            default_model='llama'
        )
        models_used = {'llama': num_players}

    # Visual game setup display
    print_game_setup(config, models_used)

    # Initialize OpenRouter client
    client = OpenRouterClient()

    # Create and run game
    engine = GameEngine(config, client)

    try:
        result = await engine.run_game()

        # Display final results with visual formatting
        display_final_results(result, pause_time=2.0)

    except KeyboardInterrupt:
        print("\n\n⏸️  Game interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Game error: {e}", exc_info=True)
        sys.exit(1)


def print_results(result):
    """Print formatted game results"""

    print(f"\n{'='*60}")
    print("🏆 GAME RESULTS")
    print(f"{'='*60}\n")

    print(f"Secret Word: {result.word} ({result.category})")
    print(f"Total Rounds: {result.total_rounds}\n")

    print(f"🎭 Actual Imposters:")
    for imp in result.actual_imposters:
        print(f"   • {imp}")

    print(f"\n🗳️  Players Voted Out:")
    for elim in result.eliminated_players:
        print(f"   • {elim}")

    correctly_identified = set(result.eliminated_players) & set(result.actual_imposters)
    print(f"\n✓ Correctly Identified: {list(correctly_identified)}")

    print(f"\n📊 Detection Accuracy: {result.detection_accuracy * 100:.1f}%")

    if result.detection_accuracy == 1.0:
        print("   🎉 PERFECT DETECTION! All imposters caught!")
    elif result.detection_accuracy >= 0.67:
        print("   ✓ Good detective work! Majority of imposters caught.")
    elif result.detection_accuracy > 0:
        print("   ⚠️  Some imposters caught, but others escaped.")
    else:
        print("   ❌ Imposters completely fooled the group!")

    # Show imposter performance
    print(f"\n🎭 Imposter Performance:")
    for imp_id in result.actual_imposters:
        imp_clues = [c for c in result.all_clues if c.player_id == imp_id]
        if imp_clues:
            print(f"\n   {imp_id}:")
            for clue_rec in imp_clues:
                print(f"   R{clue_rec.round}: \"{clue_rec.clue}\" (guessed: {clue_rec.word_hypothesis})")

    print("\n" + "="*60 + "\n")


def main():
    """Main entry point for CLI"""

    # Load environment variables
    load_dotenv(Path(__file__).parent / ".env")

    parser = argparse.ArgumentParser(
        description="Run AI-powered imposter game",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--word", required=True, help="Secret word")
    parser.add_argument("--category", required=True, help="Word category")
    parser.add_argument("--players", type=int, default=6, help="Number of players")
    parser.add_argument("--imposters", type=int, default=2, help="Number of imposters")
    parser.add_argument("--rounds", type=int, default=3, help="Number of clue rounds")
    parser.add_argument(
        "--models",
        help="Comma-separated model keys (e.g., llama,llama,gemini,haiku). "
             "Must match player count. Available: llama, gemini, haiku, gpt4-mini, mistral"
    )

    args = parser.parse_args()

    # Validate
    if args.imposters >= args.players:
        print("Error: Imposters must be less than total players")
        sys.exit(1)

    if args.imposters < 1:
        print("Error: Must have at least 1 imposter")
        sys.exit(1)

    # Run game
    asyncio.run(run_cli_game(
        word=args.word,
        category=args.category,
        num_players=args.players,
        num_imposters=args.imposters,
        num_rounds=args.rounds,
        models=args.models
    ))


if __name__ == "__main__":
    main()
