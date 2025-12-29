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
from ..ai.schemas import PlayerRole, ClueResponse, VoteResponse
from .validation import validate_clue, check_win_condition, resolve_vote_tie, ValidationResult

logger = logging.getLogger(__name__)

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
    """Record of a vote"""
    player_id: str
    voted_for: List[str]
    reasoning: Dict[str, str]
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
        self.all_votes: List[VoteRecord] = []
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

            for model_key, count in self.config.model_distribution.items():
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
        """Execute one round where all players give clues"""

        # Visual display (CLI only)
        if self.visual_mode and CLI_DISPLAY_AVAILABLE:
            print_round_header(self.current_round, self.config.num_rounds)

        # Build context for all players
        context = GameContext(
            current_round=self.current_round,
            clues_so_far=self._get_clue_dicts()
        )

        if self.visual_mode and CLI_DISPLAY_AVAILABLE:
            print_player_circle(self.players, current_speaker=None)
            pause(1.5, "All players are thinking...")

        # Prepare API requests for all players
        requests = []
        for player in self.players:
            messages = player.build_clue_messages(context)
            requests.append({
                "messages": messages,
                "model": get_model_id(player.model_name),
                "temperature": self.config.temperature
            })

        # Call all AIs in parallel
        if self.visual_mode and CLI_DISPLAY_AVAILABLE:
            print(f"\n{Colors.DIM}🤖 Calling {len(requests)} AIs concurrently...{Colors.RESET}")

        responses = await self.openrouter.batch_call(
            requests,
            response_format=ClueResponse
        )

        if self.visual_mode and CLI_DISPLAY_AVAILABLE:
            print(f"{Colors.SUCCESS}✓ All AI responses received{Colors.RESET}\n")
            pause(1.0)

        # Process and display clues
        for player, response in zip(self.players, responses):
            if isinstance(response, Exception):
                logger.error(f"{player.player_id} API call failed: {response}")
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
        """All players vote for suspected imposters"""

        if self.visual_mode and CLI_DISPLAY_AVAILABLE:
            print_voting_header()

        # Prepare voting requests
        requests = []
        for player in self.players:
            messages = player.build_voting_messages(
                all_clues=self._get_clue_dicts(),
                word=self.config.word
            )
            requests.append({
                "messages": messages,
                "model": get_model_id(player.model_name),
                "temperature": 0.5
            })

        if self.visual_mode and CLI_DISPLAY_AVAILABLE:
            print(f"\n{Colors.DIM}🤖 All players analyzing {len(self.all_clues)} clues...{Colors.RESET}")

        responses = await self.openrouter.batch_call(
            requests,
            response_format=VoteResponse
        )

        if self.visual_mode and CLI_DISPLAY_AVAILABLE:
            print(f"{Colors.SUCCESS}✓ Votes received{Colors.RESET}\n")
            pause(1.0)

        # Process votes
        for player, response in zip(self.players, responses):
            if isinstance(response, Exception):
                logger.error(f"{player.player_id} voting failed: {response}")
                response = VoteResponse(
                    thinking="[API_ERROR] Language model failed to generate valid voting response. Using empty vote as fallback to continue game.",
                    votes=[],
                    confidence=0,
                    reasoning_per_player={}
                )

            vote_record = VoteRecord(
                player_id=player.player_id,
                voted_for=response.votes,
                reasoning=response.reasoning_per_player,
                thinking=response.thinking,
                confidence=response.confidence
            )
            self.all_votes.append(vote_record)
            player.record_vote(response)

            # Emit event for streaming
            if self.event_callback:
                await self.event_callback({
                    'type': 'vote',
                    'player_id': player.player_id,
                    'votes': response.votes,
                    'thinking': response.thinking,
                    'reasoning': response.reasoning_per_player,
                    'confidence': response.confidence
                })

            # Visual display (CLI only)
            if self.visual_mode and CLI_DISPLAY_AVAILABLE:
                print_vote(
                    player_id=player.player_id,
                    votes=response.votes,
                    thinking=response.thinking,
                    reasoning=response.reasoning_per_player,
                    pause_time=3.0
                )

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
