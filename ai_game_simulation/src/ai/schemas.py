"""
Pydantic schemas for structured AI responses.
All AI players return JSON matching these schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class PlayerRole(str, Enum):
    """Player role in the game"""
    IMPOSTER = "imposter"
    NON_IMPOSTER = "non_imposter"


class ClueResponse(BaseModel):
    """
    Response schema for clue generation.
    AI must provide strategic thinking + actual clue.
    """
    thinking: str = Field(
        description="Inner monologue - strategic reasoning about what clue to give and why",
        min_length=10,
        max_length=2000  # Increased for detailed strategic analysis
    )
    clue: str = Field(
        description="The actual one-word clue (can include hyphens)",
        min_length=1,
        max_length=50
    )
    confidence: int = Field(
        description="Confidence level in this clue (0-100)",
        ge=0,
        le=100
    )
    word_hypothesis: Optional[str] = Field(
        default=None,
        description="For imposters only: current guess at what the secret word might be"
    )


class VoteResponse(BaseModel):
    """
    Response schema for voting phase.
    AI analyzes all clues and votes for suspected imposters.
    """
    thinking: str = Field(
        description="Analysis of clues and reasoning for votes",
        min_length=20,
        max_length=2000  # Increased for detailed analysis
    )
    votes: List[str] = Field(
        description="List of player IDs to vote out (can be empty if uncertain)",
        min_items=0  # Allow empty votes if AI is uncertain
    )
    confidence: int = Field(
        description="Overall confidence in these votes (0-100)",
        ge=0,
        le=100
    )
    reasoning_per_player: Dict[str, str] = Field(
        description="Brief explanation for each suspected player (must provide for all voted players)"
    )


class DiscussionResponse(BaseModel):
    """
    Response schema for optional discussion phase.
    Players share suspicions or observations.
    """
    thinking: str = Field(
        description="Internal reasoning before speaking"
    )
    message: str = Field(
        description="Public statement to other players",
        max_length=200
    )
    confidence: int = Field(
        description="Confidence in this statement",
        ge=0,
        le=100
    )
