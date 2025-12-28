"""
AIPlayer class - represents a single AI agent playing the imposter game.
Each player maintains independent conversation state and makes decisions via LLM.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import logging

from ..ai.schemas import PlayerRole, ClueResponse, VoteResponse, DiscussionResponse
from ..ai.prompts import (
    NON_IMPOSTER_SYSTEM_PROMPT,
    IMPOSTER_SYSTEM_PROMPT,
    build_clue_prompt,
    build_voting_prompt,
    build_discussion_prompt
)

logger = logging.getLogger(__name__)


@dataclass
class PlayerKnowledge:
    """What this specific player knows about the game"""
    my_role: PlayerRole
    my_word: Optional[str]  # None for imposters
    category: str
    total_players: int
    num_imposters: int
    player_id: str


@dataclass
class GameContext:
    """
    Game state information available to a player.
    Different for each player (they only see what they've observed).
    """
    current_round: int
    clues_so_far: List[Dict]  # {round, player_id, clue}
    discussion_messages: List[Dict] = field(default_factory=list)


class AIPlayer:
    """
    Represents a single AI player with independent conversation state.

    Each player:
    - Maintains their own LLM conversation history
    - Only knows their role and what they've observed
    - Has no knowledge of other players' inner thoughts
    - Uses a specific LLM model (can be different per player)
    """

    def __init__(
        self,
        player_id: str,
        role: PlayerRole,
        secret_word: Optional[str],
        category: str,
        total_players: int,
        num_imposters: int,
        model_name: str = "llama"
    ):
        self.player_id = player_id
        self.role = role
        self.secret_word = secret_word  # None for imposters
        self.category = category
        self.model_name = model_name

        self.knowledge = PlayerKnowledge(
            my_role=role,
            my_word=secret_word,
            category=category,
            total_players=total_players,
            num_imposters=num_imposters,
            player_id=player_id
        )

        # Conversation state (preserved across turns)
        self.conversation_history: List[Dict[str, str]] = []

        # Tracking (for analysis)
        self.clues_given: List[ClueResponse] = []
        self.suspicions: Dict[str, float] = {}  # {player_id: suspicion_level}
        self.votes_cast: Optional[VoteResponse] = None

        logger.info(f"Created {player_id}: {role.value}, model={model_name}")

    def get_system_prompt(self) -> str:
        """Generate role-specific system prompt"""
        if self.role == PlayerRole.NON_IMPOSTER:
            return NON_IMPOSTER_SYSTEM_PROMPT.format(
                player_id=self.player_id,
                word=self.secret_word,
                category=self.category,
                total_players=self.knowledge.total_players,
                num_imposters=self.knowledge.num_imposters
            )
        else:
            return IMPOSTER_SYSTEM_PROMPT.format(
                player_id=self.player_id,
                category=self.category,
                total_players=self.knowledge.total_players,
                num_imposters=self.knowledge.num_imposters
            )

    def build_clue_messages(self, context: GameContext) -> List[Dict[str, str]]:
        """
        Build message array for clue generation API call.
        Includes system prompt + conversation history + current prompt.
        """
        messages = [
            {"role": "system", "content": self.get_system_prompt()}
        ]

        # Add conversation history (previous turns)
        messages.extend(self.conversation_history)

        # Add current clue request
        clue_prompt = build_clue_prompt(
            player_id=self.player_id,
            role=self.role,
            current_round=context.current_round,
            previous_clues=context.clues_so_far,
            word=self.secret_word,
            category=self.category
        )

        messages.append({"role": "user", "content": clue_prompt})

        return messages

    def build_voting_messages(
        self,
        all_clues: List[Dict],
        word: str
    ) -> List[Dict[str, str]]:
        """
        Build message array for voting phase.
        Reveals the secret word for analysis purposes.
        """
        messages = [
            {"role": "system", "content": self.get_system_prompt()}
        ]

        messages.extend(self.conversation_history)

        voting_prompt = build_voting_prompt(
            player_id=self.player_id,
            role=self.role,
            all_clues=all_clues,
            num_imposters=self.knowledge.num_imposters,
            word=word,
            category=self.category
        )

        messages.append({"role": "user", "content": voting_prompt})

        return messages

    def record_clue(self, clue_response: ClueResponse):
        """
        Record a clue this player gave.
        Updates conversation history for continuity.
        """
        self.clues_given.append(clue_response)

        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": clue_response.model_dump_json()
        })

    def record_vote(self, vote_response: VoteResponse):
        """Record this player's vote"""
        self.votes_cast = vote_response

        self.conversation_history.append({
            "role": "assistant",
            "content": vote_response.model_dump_json()
        })

    def __repr__(self) -> str:
        role_emoji = "🎭" if self.role == PlayerRole.IMPOSTER else "✓"
        return f"{role_emoji} {self.player_id} ({self.model_name})"
