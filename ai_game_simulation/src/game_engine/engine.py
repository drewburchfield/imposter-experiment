"""
GameEngine - Orchestrates the imposter game with AI players.
Manages state transitions, turn coordination, and results calculation.
"""

import random
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict

from .player import AIPlayer, GameContext, PlayerKnowledge
from ..ai.schemas import PlayerRole, ClueResponse, VoteResponse, SingleVoteResponse
from .validation import validate_clue, check_win_condition, resolve_vote_tie, ValidationResult

logger = logging.getLogger(__name__)

# Default model distribution (used when None provided)
DEFAULT_MODEL_DISTRIBUTION = {
    'gemini-3': 2,      # Fastest (1.98s) - Google
    'gemini-2.5': 2,    # Fast + max creativity - Google
    'gpt4o-mini': 2,    # Premium quality - OpenAI
    'haiku': 1,         # Best reasoning - Anthropic
    'qwen-coder': 1,    # Open source - Qwen
}

# Import OpenRouter client (SDK preferred)
try:
    from ..ai.openrouter_sdk import OpenRouterSDKClient as OpenRouterClient, get_model_id
    logger.info("Using OpenRouter SDK client")
except ImportError:
    from ..ai.openrouter import OpenRouterClient, get_model_id
    logger.info("Using legacy OpenRouter client")

# Optional CLI display (only import if available)
try:
    from ..utils.cli_display import (
        print_player_circle,
        print_round_header,
        print_clue,
        print_voting_header,
        print_vote,
        pause,
        Colors
    )
    CLI_DISPLAY_AVAILABLE = True
except ImportError:
    CLI_DISPLAY_AVAILABLE = False


class GamePhase(Enum):
    """Game state machine phases"""
    SETUP = auto()
    CLUE_ROUND = auto()
    DISCUSSION = auto()
    VOTING = auto()
    REVEAL = auto()
    COMPLETE = auto()


@dataclass
class GameConfig:
    """Configuration for a game instance"""
    # Game setup
    word: str
    category: str
    num_players: int = 8
    num_imposters: int = 2
    num_rounds: int = 3

    # Model configuration - Uses only tested, high-performing models
    model_strategy: str = "mixed"
    default_model: str = "gemini-3"  # Fastest verified model

    # Default model distribution: Optimized for speed, diversity, and reliability
    # All models tested and verified (see test_models.py results)
    model_distribution: Dict[str, int] = field(default_factory=lambda: {
        'gemini-3': 2,      # Fastest (1.98s) - Google
        'gemini-2.5': 2,    # Fast + max creativity - Google
        'gpt4o-mini': 2,    # Premium quality - OpenAI
        'haiku': 1,         # Best reasoning - Anthropic
        'qwen-coder': 1,    # Open source - Qwen
    })

    # Optional features
    enable_discussion: bool = False
    discussion_turns: int = 1

    # AI parameters
    temperature: float = 0.7


@dataclass
class ClueRecord:
    """Record of a single clue"""
    round: int
    player_id: str
    player_model: str
    role: PlayerRole
    clue: str
    thinking: str
    confidence: int
    word_hypothesis: Optional[str] = None


@dataclass
class VoteRecord:
    """Record of a vote (legacy - for batch voting)"""
    player_id: str
    voted_for: List[str]
    reasoning: Dict[str, str]
    thinking: str
    confidence: int


@dataclass
class SingleVoteRecord:
    """Record of a single vote in sequential voting"""
    voting_round: int
    player_id: str
    voted_for: str
    reasoning: str
    thinking: str
    confidence: int


@dataclass
class GameResult:
    """Final game results"""
    word: str
    category: str
    actual_imposters: List[str]
    eliminated_players: List[str]
    detection_accuracy: float  # 0.0 to 1.0
    total_rounds: int
    all_clues: List[ClueRecord]
    all_votes: List[VoteRecord]


class GameEngine:
    """
    Main game engine that orchestrates AI player turns.

    Responsibilities:
    - Initialize players with roles
    - Coordinate turn order
    - Manage game phases
    - Calculate results
    """

    def __init__(self, config: GameConfig, openrouter_client: OpenRouterClient, visual_mode: bool = False):
        self.config = config
        self.openrouter = openrouter_client
        self.phase = GamePhase.SETUP
        self.visual_mode = visual_mode  # Enable CLI visual display

        self.players: List[AIPlayer] = []
        self.current_round = 0

        # Game history
        self.all_clues: List[ClueRecord] = []
        self.all_votes: List[VoteRecord] = []  # Legacy batch votes
        self.sequential_votes: List[SingleVoteRecord] = []  # New sequential votes
        self.eliminated_players: List[str] = []

        # Event callback for streaming
        self.event_callback = None

        # Game state
        self.game_ended_early = False
        self.early_end_reason = None

        logger.info(f"GameEngine created: {config.num_players} players, "
                   f"{config.num_imposters} imposters, word='{config.word}'")

    async def initialize_game(self):
        """
        Setup phase: Create AI players and randomly assign roles.
        """
        self.phase = GamePhase.SETUP

        # Create player IDs
        player_ids = [f"Player_{i+1}" for i in range(self.config.num_players)]

        # Randomly select imposters
        imposter_ids = random.sample(player_ids, self.config.num_imposters)

        # Assign models based on strategy
        model_assignments = self._assign_models(player_ids, imposter_ids)

        # Create AI players
        for player_id in player_ids:
            is_imposter = player_id in imposter_ids
            role = PlayerRole.IMPOSTER if is_imposter else PlayerRole.NON_IMPOSTER
            word = None if is_imposter else self.config.word
            model = model_assignments[player_id]

            player = AIPlayer(
                player_id=player_id,
                role=role,
                secret_word=word,
                category=self.config.category,
                total_players=self.config.num_players,
                num_imposters=self.config.num_imposters,
                model_name=model
            )
            self.players.append(player)

        logger.info(f"Game initialized with {len(self.players)} players")
        logger.info(f"Imposters: {imposter_ids}")

    def _assign_models(
        self,
        player_ids: List[str],
        imposter_ids: List[str]
    ) -> Dict[str, str]:
        """Assign models to players based on strategy"""

        if self.config.model_strategy == "single":
            # All players use default model
            return {pid: self.config.default_model for pid in player_ids}

        elif self.config.model_strategy == "mixed":
            # Distribute models according to distribution
            assignments = {}
            model_pool = []

            # Handle None model_distribution by using module constant
            distribution = self.config.model_distribution or DEFAULT_MODEL_DISTRIBUTION

            for model_key, count in distribution.items():
                model_pool.extend([model_key] * count)

            # Pad or trim to match player count
            while len(model_pool) < len(player_ids):
                model_pool.append(self.config.default_model)
            model_pool = model_pool[:len(player_ids)]

            # Shuffle and assign
            random.shuffle(model_pool)
            for pid, model in zip(player_ids, model_pool):
                assignments[pid] = model

            return assignments

        elif self.config.model_strategy == "role-based":
            # Different models for imposters vs non-imposters
            # (Not implemented yet in config, but could be added)
            assignments = {}
            for pid in player_ids:
                if pid in imposter_ids:
                    assignments[pid] = "haiku"  # Better model for imposters
                else:
                    assignments[pid] = "llama"  # Cheap for non-imposters
            return assignments

        else:
            return {pid: self.config.default_model for pid in player_ids}

    def set_event_callback(self, callback):
        """Set callback for streaming events to API/UI"""
        self.event_callback = callback

    async def run_game(self) -> GameResult:
        """
        Main game loop with validation and win condition checking.

        Returns:
            GameResult with complete game history and winner
        """
        await self.initialize_game()

        # Run clue rounds
        for round_num in range(1, self.config.num_rounds + 1):
            self.current_round = round_num
            self.phase = GamePhase.CLUE_ROUND

            logger.info(f"\n{'='*60}")
            logger.info(f"ROUND {round_num}/{self.config.num_rounds}")
            logger.info(f"{'='*60}")

            await self._execute_clue_round()

            # Check if game ended early (word revealed, instant elimination, etc.)
            if self.game_ended_early:
                break

            # Check win condition after instant reveals
            win_check = self._check_win_condition()
            if win_check.game_over:
                logger.info(f"Game over: {win_check.reason}")
                break

            # Optional discussion phase
            if self.config.enable_discussion:
                self.phase = GamePhase.DISCUSSION
                await self._execute_discussion_phase()

        # Voting phase (if game hasn't ended early)
        if not self.game_ended_early:
            self.phase = GamePhase.VOTING
            logger.info(f"\n{'='*60}")
            logger.info("VOTING PHASE")
            logger.info(f"{'='*60}")

            await self._execute_voting()

        # Calculate results
        self.phase = GamePhase.REVEAL
        result = self._calculate_results()

        self.phase = GamePhase.COMPLETE
        return result

    async def _execute_clue_round(self):
        """Execute one round where players give clues SEQUENTIALLY (each sees previous clues)"""

        # Visual display (CLI only)
        if self.visual_mode and CLI_DISPLAY_AVAILABLE:
            print_round_header(self.current_round, self.config.num_rounds)
            print_player_circle(self.players, current_speaker=None)

        # Call players SEQUENTIALLY so each sees previous clues in this round
        for player in self.players:
            # Build context with ALL clues so far (including this round)
            context = GameContext(
                current_round=self.current_round,
                clues_so_far=self._get_clue_dicts()  # Updated after each player!
            )

            if self.visual_mode and CLI_DISPLAY_AVAILABLE:
                pause(0.5, f"{player.player_id} is thinking...")

            # Build messages for this specific player
            messages = player.build_clue_messages(context)

            # Call LLM for this player
            try:
                response = await self.openrouter.call(
                    messages=messages,
                    model=get_model_id(player.model_name),
                    response_format=ClueResponse,
                    temperature=self.config.temperature,
                    max_tokens=5000
                )
            except Exception as e:
                logger.error(f"{player.player_id} API call failed: {e}")
                response = ClueResponse(
                    thinking="[API_ERROR] Language model failed to generate clue response. Using fallback generic clue.",
                    clue="uncertain",
                    confidence=0
                )

            # VALIDATE CLUE (including duplicate check)
            previous_clue_words = [c.clue for c in self.all_clues]
            validation = validate_clue(
                clue=response.clue,
                secret_word=self.config.word,
                player_id=player.player_id,
                role=player.role,
                previous_clues=previous_clue_words
            )

            # Handle validation result
            if not validation.valid:
                # Emit validation failure event
                if self.event_callback:
                    await self.event_callback({
                        'type': 'validation_error',
                        'player_id': player.player_id,
                        'clue': response.clue,
                        'reason': validation.reason,
                        'message': validation.message
                    })

                # Instant reveal for imposters saying the word
                if validation.instant_reveal:
                    self.eliminated_players.append(player.player_id)

                    if self.event_callback:
                        await self.event_callback({
                            'type': 'instant_reveal',
                            'player_id': player.player_id,
                            'role': player.role.value,
                            'reason': 'said_secret_word'
                        })

                    logger.warning(validation.message)

                # Game over for non-imposters saying word
                if validation.game_over:
                    self.game_ended_early = True
                    self.early_end_reason = validation.message
                    return

                # Skip recording invalid clue
                continue

            # Record valid clue
            clue_record = ClueRecord(
                round=self.current_round,
                player_id=player.player_id,
                player_model=player.model_name,
                role=player.role,
                clue=response.clue,
                thinking=response.thinking,
                confidence=response.confidence,
                word_hypothesis=response.word_hypothesis
            )
            self.all_clues.append(clue_record)
            player.record_clue(response)

            # Emit event for streaming
            if self.event_callback:
                await self.event_callback({
                    'type': 'clue',
                    'round': self.current_round,
                    'player_id': player.player_id,
                    'player_model': player.model_name,
                    'role': player.role.value,
                    'clue': response.clue,
                    'thinking': response.thinking,
                    'confidence': response.confidence,
                    'word_hypothesis': response.word_hypothesis
                })

            # Visual display (CLI only)
            if self.visual_mode and CLI_DISPLAY_AVAILABLE:
                print_player_circle(self.players, current_speaker=player.player_id)
                print_clue(
                    player_id=player.player_id,
                    role=player.role,
                    model=player.model_name,
                    clue=response.clue,
                    thinking=response.thinking,
                    word_hypothesis=response.word_hypothesis,
                    pause_time=4.0
                )

    async def _execute_discussion_phase(self):
        """Optional discussion phase (not implemented in MVP)"""
        logger.info("Discussion phase skipped in MVP")
        pass

    async def _execute_voting(self):
        """
        Sequential voting: One elimination per voting round.
        Repeat for each imposter to be eliminated.
        """

        if self.visual_mode and CLI_DISPLAY_AVAILABLE:
            print_voting_header()

        total_voting_rounds = self.config.num_imposters

        for voting_round in range(1, total_voting_rounds + 1):
            # Emit voting round start
            if self.event_callback:
                await self.event_callback({
                    'type': 'voting_round_start',
                    'voting_round': voting_round,
                    'total_voting_rounds': total_voting_rounds,
                    'eliminated_so_far': self.eliminated_players.copy()
                })

            if self.visual_mode and CLI_DISPLAY_AVAILABLE:
                print(f"\n{'='*60}")
                print(f"VOTING ROUND {voting_round} of {total_voting_rounds}")
                print(f"{'='*60}")
                if self.eliminated_players:
                    print(f"Already eliminated: {', '.join(self.eliminated_players)}")

            # Get active players (not eliminated)
            active_players = [p for p in self.players if p.player_id not in self.eliminated_players]
            logger.info(f"Voting round {voting_round}: {len(active_players)} active players: {[p.player_id for p in active_players]}")

            # Collect votes for this round - SEQUENTIALLY so players can see prior votes
            votes_this_round: List[Dict] = []
            vote_counts: Dict[str, int] = defaultdict(int)

            for player in active_players:
                logger.info(f"Getting vote from {player.player_id}...")
                # Build messages with context of votes cast so far
                messages = player.build_single_vote_messages(
                    all_clues=self._get_clue_dicts(),
                    voting_round=voting_round,
                    total_voting_rounds=total_voting_rounds,
                    eliminated_players=self.eliminated_players,
                    previous_votes_this_round=votes_this_round,
                    word=self.config.word
                )

                if self.visual_mode and CLI_DISPLAY_AVAILABLE:
                    pause(0.5, f"{player.player_id} is deliberating...")

                # Call LLM for this player's vote
                try:
                    response = await self.openrouter.call(
                        messages=messages,
                        model=get_model_id(player.model_name),
                        response_format=SingleVoteResponse,
                        temperature=0.5,
                        max_tokens=2000
                    )
                except Exception as e:
                    logger.error(f"{player.player_id} voting failed: {e}")
                    # Fallback: vote for random non-eliminated player
                    candidates = [p.player_id for p in active_players if p.player_id != player.player_id]
                    fallback_vote = candidates[0] if candidates else "abstain"
                    response = SingleVoteResponse(
                        thinking="[API_ERROR] Vote failed, using fallback.",
                        vote=fallback_vote,
                        reasoning="API error - fallback vote",
                        confidence=0
                    )

                # Validate vote target exists and isn't eliminated
                vote_target = response.vote
                valid_targets = [p.player_id for p in active_players if p.player_id != player.player_id]
                if vote_target not in valid_targets:
                    # Invalid vote - pick first valid target
                    vote_target = valid_targets[0] if valid_targets else "abstain"

                # Record the vote
                vote_record = SingleVoteRecord(
                    voting_round=voting_round,
                    player_id=player.player_id,
                    voted_for=vote_target,
                    reasoning=response.reasoning,
                    thinking=response.thinking,
                    confidence=response.confidence
                )
                self.sequential_votes.append(vote_record)

                # Track for this round
                votes_this_round.append({
                    'player_id': player.player_id,
                    'vote': vote_target,
                    'reasoning': response.reasoning
                })
                vote_counts[vote_target] += 1

                # Emit event for streaming
                if self.event_callback:
                    await self.event_callback({
                        'type': 'vote',
                        'voting_round': voting_round,
                        'player_id': player.player_id,
                        'vote': vote_target,
                        'thinking': response.thinking,
                        'reasoning': response.reasoning,
                        'confidence': response.confidence,
                        'votes_so_far': dict(vote_counts),
                        'total_votes_cast': len(votes_this_round),
                        'total_active_players': len(active_players)
                    })

                if self.visual_mode and CLI_DISPLAY_AVAILABLE:
                    print(f"{player.player_id} votes for {vote_target}: {response.reasoning}")
                    pause(1.0)

            # Tally votes and determine elimination
            if vote_counts:
                max_votes = max(vote_counts.values())
                tied_players = [p for p, v in vote_counts.items() if v == max_votes]

                if len(tied_players) > 1:
                    # Tie - use tie-breaker
                    eliminated = resolve_vote_tie(tied_players)
                    logger.info(f"Vote tie between {tied_players}, eliminated: {eliminated}")
                else:
                    eliminated = tied_players[0]

                self.eliminated_players.append(eliminated)

                # Check if eliminated player was an imposter
                eliminated_player = next((p for p in self.players if p.player_id == eliminated), None)
                was_imposter = eliminated_player.role == PlayerRole.IMPOSTER if eliminated_player else False

                # Emit elimination event
                if self.event_callback:
                    await self.event_callback({
                        'type': 'elimination',
                        'voting_round': voting_round,
                        'eliminated_player': eliminated,
                        'was_imposter': was_imposter,
                        'vote_counts': dict(vote_counts),
                        'remaining_imposters': self._count_remaining_imposters()
                    })

                if self.visual_mode and CLI_DISPLAY_AVAILABLE:
                    role_reveal = "🎭 IMPOSTER!" if was_imposter else "✓ Innocent"
                    print(f"\n{'='*40}")
                    print(f"ELIMINATED: {eliminated} - {role_reveal}")
                    print(f"Votes: {dict(vote_counts)}")
                    print(f"{'='*40}")
                    pause(2.0)

                # Check win condition after elimination
                win_check = self._check_win_condition()
                if win_check.game_over:
                    logger.info(f"Game over: {win_check.reason}")
                    break

    def _count_remaining_imposters(self) -> int:
        """Count imposters not yet eliminated"""
        all_imposters = [p.player_id for p in self.players if p.role == PlayerRole.IMPOSTER]
        return len([i for i in all_imposters if i not in self.eliminated_players])

    def _check_win_condition(self):
        """Check if game should end based on eliminations"""
        all_imposters = [p.player_id for p in self.players if p.role == PlayerRole.IMPOSTER]
        remaining_players = [p.player_id for p in self.players if p.player_id not in self.eliminated_players]
        num_civilians = len([p for p in self.players if p.role == PlayerRole.NON_IMPOSTER])

        return check_win_condition(
            eliminated_players=self.eliminated_players,
            all_imposters=all_imposters,
            remaining_players=remaining_players,
            num_civilians=num_civilians
        )

    def _get_clue_dicts(self) -> List[Dict]:
        """Convert clue records to simple dicts for context"""
        return [
            {
                "round": c.round,
                "player_id": c.player_id,
                "clue": c.clue
            }
            for c in self.all_clues
        ]

    def _calculate_results(self) -> GameResult:
        """
        Determine game outcome based on votes.

        Returns:
            GameResult with accuracy metrics
        """
        logger.info(f"\n{'='*60}")
        logger.info("CALCULATING RESULTS")
        logger.info(f"{'='*60}")

        # Tally votes
        vote_counts = defaultdict(int)
        for vote_record in self.all_votes:
            for suspect in vote_record.voted_for:
                vote_counts[suspect] += 1

        # Top voted players with tie handling
        if vote_counts:
            max_votes = max(vote_counts.values())
            tied_players = [p for p, v in vote_counts.items() if v == max_votes]

            if len(tied_players) > 1:
                # Tie! Use tie-breaking
                eliminated_by_vote = [resolve_vote_tie(tied_players)]
                logger.info(f"Vote tie between {tied_players}, eliminated: {eliminated_by_vote}")
            else:
                eliminated_by_vote = [tied_players[0]]
        else:
            eliminated_by_vote = []

        # Combine with instant eliminations
        all_eliminated = list(set(self.eliminated_players + eliminated_by_vote))

        # Actual imposters
        actual_imposters = [
            p.player_id
            for p in self.players
            if p.role == PlayerRole.IMPOSTER
        ]

        # Calculate accuracy
        correctly_identified = set(all_eliminated) & set(actual_imposters)
        accuracy = len(correctly_identified) / len(actual_imposters) if actual_imposters else 0

        # Determine winner
        win_check = check_win_condition(
            eliminated_players=all_eliminated,
            all_imposters=actual_imposters,
            remaining_players=[p.player_id for p in self.players if p.player_id not in all_eliminated],
            num_civilians=len([p for p in self.players if p.role == PlayerRole.NON_IMPOSTER])
        )

        # Create result
        result = GameResult(
            word=self.config.word,
            category=self.config.category,
            actual_imposters=actual_imposters,
            eliminated_players=all_eliminated,
            detection_accuracy=accuracy,
            total_rounds=self.current_round,
            all_clues=self.all_clues,
            all_votes=self.all_votes
        )

        # Log results
        logger.info(f"\nSecret Word: {self.config.word}")
        logger.info(f"Actual Imposters: {actual_imposters}")
        logger.info(f"All Eliminated: {all_eliminated}")
        logger.info(f"Correctly Identified: {list(correctly_identified)}")
        logger.info(f"Detection Accuracy: {accuracy * 100:.1f}%")

        # Announce winner
        if win_check.winner == 'civilians':
            logger.info("🎉 CIVILIANS WIN! All imposters eliminated!")
        elif win_check.winner == 'imposters':
            logger.info("🎭 IMPOSTERS WIN! They survived or outnumbered civilians!")
        elif accuracy == 1.0:
            logger.info("🎉 PERFECT DETECTION! All imposters caught!")
        elif accuracy > 0.5:
            logger.info("✓ Good detective work!")
        else:
            logger.info("❌ Imposters escaped detection")

        return result
