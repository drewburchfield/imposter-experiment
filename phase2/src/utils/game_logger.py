"""
Comprehensive game logging for analysis and debugging.
Logs every LLM interaction, game event, and validation.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class GameLogger:
    """
    Comprehensive logger for game sessions.
    Tracks all interactions for post-game analysis.
    """

    def __init__(self, game_id: str, log_dir: str = "./data/logs"):
        self.game_id = game_id
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.log_file = self.log_dir / f"{game_id}.jsonl"
        self.events: List[Dict] = []

    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log a game event with timestamp"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "game_id": self.game_id,
            "type": event_type,
            "data": data
        }

        self.events.append(event)

        # Append to JSONL file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

    def log_llm_request(self, player_id: str, model: str, messages: List[Dict], prompt_tokens: int = 0):
        """Log LLM API request"""
        self.log_event("llm_request", {
            "player_id": player_id,
            "model": model,
            "message_count": len(messages),
            "prompt_tokens": prompt_tokens,
            "last_message": messages[-1] if messages else None
        })

    def log_llm_response(self, player_id: str, model: str, response: Any, completion_tokens: int = 0, success: bool = True, error: str = None):
        """Log LLM API response"""
        self.log_event("llm_response", {
            "player_id": player_id,
            "model": model,
            "success": success,
            "completion_tokens": completion_tokens,
            "error": error,
            "response_preview": str(response)[:200] if response else None
        })

    def log_clue(self, round_num: int, player_id: str, clue: str, thinking: str, role: str, validation_passed: bool):
        """Log a clue with validation result"""
        self.log_event("clue", {
            "round": round_num,
            "player_id": player_id,
            "clue": clue,
            "thinking": thinking,
            "role": role,
            "validation_passed": validation_passed
        })

    def log_validation_failure(self, player_id: str, clue: str, reason: str, message: str):
        """Log validation failure"""
        self.log_event("validation_failure", {
            "player_id": player_id,
            "clue": clue,
            "reason": reason,
            "message": message
        })

    def log_vote(self, player_id: str, votes: List[str], thinking: str, reasoning: Dict):
        """Log voting"""
        self.log_event("vote", {
            "player_id": player_id,
            "votes": votes,
            "thinking": thinking,
            "reasoning": reasoning
        })

    def log_game_result(self, result: Dict):
        """Log final game result"""
        self.log_event("game_result", result)

    def get_summary(self) -> Dict:
        """Generate game summary for analysis"""
        clues = [e for e in self.events if e['type'] == 'clue']
        votes = [e for e in self.events if e['type'] == 'vote']
        validations = [e for e in self.events if e['type'] == 'validation_failure']
        llm_errors = [e for e in self.events if e['type'] == 'llm_response' and not e['data'].get('success')]

        return {
            "game_id": self.game_id,
            "total_clues": len(clues),
            "total_votes": len(votes),
            "validation_failures": len(validations),
            "llm_errors": len(llm_errors),
            "log_file": str(self.log_file)
        }

    def print_summary(self):
        """Print readable summary"""
        summary = self.get_summary()
        print("\n" + "="*60)
        print(f"GAME LOG SUMMARY: {self.game_id}")
        print("="*60)
        print(f"Total Clues: {summary['total_clues']}")
        print(f"Total Votes: {summary['total_votes']}")
        print(f"Validation Failures: {summary['validation_failures']}")
        print(f"LLM Errors: {summary['llm_errors']}")
        print(f"Full Log: {summary['log_file']}")
        print("="*60 + "\n")
