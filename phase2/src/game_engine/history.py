"""
GameHistory - Complete audit trail of game events for analysis and replay.
Stores all actions, thoughts, and outcomes in SQLite.
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


def init_database(db_path: str = "./data/games.db"):
    """Initialize SQLite database with schema"""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Games table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id TEXT PRIMARY KEY,
            word TEXT NOT NULL,
            category TEXT NOT NULL,
            num_players INTEGER NOT NULL,
            num_imposters INTEGER NOT NULL,
            model_config TEXT NOT NULL,
            result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Actions table (clues, votes, discussion)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            round INTEGER,
            player_id TEXT NOT NULL,
            player_model TEXT NOT NULL,
            role TEXT NOT NULL,
            action_type TEXT NOT NULL,
            data TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id)
        )
    """)

    # Analytics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            game_id TEXT PRIMARY KEY,
            deception_rate REAL,
            detection_accuracy REAL,
            avg_clue_quality REAL,
            voting_consensus REAL,
            metrics TEXT,
            FOREIGN KEY (game_id) REFERENCES games(id)
        )
    """)

    conn.commit()
    conn.close()


class GameHistory:
    """
    Manages complete game history and persistence.
    Tracks all events for replay, analysis, and educational purposes.
    """

    def __init__(self, game_id: Optional[str] = None, db_path: str = "./data/games.db"):
        self.game_id = game_id or str(uuid.uuid4())
        self.db_path = db_path

        # In-memory event log
        self.events: List[Dict] = []

        # Initialize DB
        init_database(db_path)

    def add_event(
        self,
        event_type: str,
        data: Dict,
        player_id: Optional[str] = None,
        round_num: Optional[int] = None
    ):
        """
        Add an event to the history.

        Args:
            event_type: Type of event (game_start, clue, vote, game_end, etc.)
            data: Event-specific data
            player_id: Player who performed the action (if applicable)
            round_num: Round number (if applicable)
        """
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "game_id": self.game_id,
            "player_id": player_id,
            "round": round_num,
            "data": data
        }

        self.events.append(event)

    def save_game_start(self, config: Dict, players: List[Dict]):
        """Record game initialization"""
        self.add_event("game_start", {
            "config": config,
            "players": players
        })

        # Insert into games table
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO games (id, word, category, num_players, num_imposters, model_config)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self.game_id,
            config.get("word"),
            config.get("category"),
            config.get("num_players"),
            config.get("num_imposters"),
            json.dumps(config)
        ))

        conn.commit()
        conn.close()

    def save_clue(
        self,
        round_num: int,
        player_id: str,
        player_model: str,
        role: str,
        clue: str,
        thinking: str,
        confidence: int,
        word_hypothesis: Optional[str] = None
    ):
        """Record a clue action"""
        data = {
            "clue": clue,
            "thinking": thinking,
            "confidence": confidence,
            "word_hypothesis": word_hypothesis
        }

        self.add_event("clue", data, player_id, round_num)

        # Insert into actions table
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO actions (game_id, round, player_id, player_model, role, action_type, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.game_id,
            round_num,
            player_id,
            player_model,
            role,
            "clue",
            json.dumps(data)
        ))

        conn.commit()
        conn.close()

    def save_vote(
        self,
        player_id: str,
        player_model: str,
        role: str,
        votes: List[str],
        thinking: str,
        reasoning: Dict[str, str],
        confidence: int
    ):
        """Record a vote action"""
        data = {
            "votes": votes,
            "thinking": thinking,
            "reasoning": reasoning,
            "confidence": confidence
        }

        self.add_event("vote", data, player_id, None)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO actions (game_id, round, player_id, player_model, role, action_type, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.game_id,
            None,
            player_id,
            player_model,
            role,
            "vote",
            json.dumps(data)
        ))

        conn.commit()
        conn.close()

    def save_game_result(self, result: Dict):
        """Record final game results"""
        self.add_event("game_end", result)

        # Update games table with result
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE games
            SET result = ?
            WHERE id = ?
        """, (json.dumps(result), self.game_id))

        conn.commit()
        conn.close()

    def get_events_for_sse(self) -> List[Dict]:
        """
        Get all events formatted for SSE streaming.
        Used by FastAPI to stream game to frontend.
        """
        return self.events

    def to_json(self) -> str:
        """Export full history as JSON"""
        return json.dumps({
            "game_id": self.game_id,
            "events": self.events
        }, indent=2)

    @staticmethod
    def load_game(game_id: str, db_path: str = "./data/games.db") -> Optional[Dict]:
        """Load a complete game from database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get game info
        cursor.execute("SELECT * FROM games WHERE id = ?", (game_id,))
        game_row = cursor.fetchone()

        if not game_row:
            return None

        # Get all actions
        cursor.execute("""
            SELECT * FROM actions WHERE game_id = ? ORDER BY id
        """, (game_id,))
        action_rows = cursor.fetchall()

        conn.close()

        return {
            "game": dict(zip(
                ["id", "word", "category", "num_players", "num_imposters",
                 "model_config", "result", "created_at"],
                game_row
            )),
            "actions": [
                dict(zip(
                    ["id", "game_id", "round", "player_id", "player_model",
                     "role", "action_type", "data", "timestamp"],
                    row
                ))
                for row in action_rows
            ]
        }
