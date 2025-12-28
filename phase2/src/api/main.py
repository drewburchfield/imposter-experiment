"""
FastAPI backend for Phase 2 - AI Imposter Game
Provides REST API and Server-Sent Events (SSE) streaming for real-time game observation.
"""

import asyncio
import uuid
import os
import logging
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json

logger = logging.getLogger(__name__)

from ..game_engine.engine import GameEngine, GameConfig, GameResult
from ..game_engine.history import GameHistory, init_database
from ..ai.openrouter_sdk import OpenRouterSDKClient as OpenRouterClient

# Initialize app
app = FastAPI(
    title="Imposter Mystery - AI Game API",
    description="Observable AI imposter game with independent LLM agents",
    version="2.0.0"
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game sessions (in-memory for MVP, use Redis for production)
game_sessions: Dict[str, GameEngine] = {}
game_histories: Dict[str, GameHistory] = {}

# Initialize database on startup
@app.on_event("startup")
async def startup():
    init_database()


# ============================================
# API MODELS
# ============================================

class CreateGameRequest(BaseModel):
    """Request to create a new game"""
    word: str
    category: str
    num_players: int = 8
    num_imposters: int = 2
    num_rounds: int = 3
    model_strategy: str = "mixed"
    model_distribution: Optional[Dict[str, int]] = None
    enable_discussion: bool = False


class GameSession(BaseModel):
    """Response with game session info"""
    game_id: str
    status: str
    stream_url: str


# ============================================
# ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "app": "Imposter Mystery AI Game",
        "version": "2.0.0",
        "status": "running"
    }


@app.post("/api/game/create", response_model=GameSession)
async def create_game(request: CreateGameRequest):
    """
    Create a new game instance.

    Returns game_id and SSE stream URL for real-time updates.
    """
    game_id = str(uuid.uuid4())

    # Create config
    config = GameConfig(
        word=request.word,
        category=request.category,
        num_players=request.num_players,
        num_imposters=request.num_imposters,
        num_rounds=request.num_rounds,
        model_strategy=request.model_strategy,
        model_distribution=request.model_distribution or {
            'llama': request.num_players // 2,
            'gemini': request.num_players // 4,
            'haiku': request.num_players // 4
        },
        enable_discussion=request.enable_discussion
    )

    # Create OpenRouter client
    openrouter = OpenRouterClient(
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    # Create game engine
    engine = GameEngine(config, openrouter)

    # Create history tracker
    history = GameHistory(game_id)

    # Store in sessions
    game_sessions[game_id] = engine
    game_histories[game_id] = history

    return GameSession(
        game_id=game_id,
        status="created",
        stream_url=f"/api/game/{game_id}/stream"
    )


@app.get("/api/game/{game_id}/stream")
async def stream_game(game_id: str):
    """
    Server-Sent Events stream of game progression.

    Streams events as they happen:
    - round_start
    - clue (with player thoughts)
    - round_end
    - voting_start
    - vote (with analysis)
    - game_complete (with results)
    """
    engine = game_sessions.get(game_id)
    history = game_histories.get(game_id)

    if not engine or not history:
        raise HTTPException(status_code=404, detail="Game not found")

    event_queue = []

    async def emit_event(event):
        """Callback to capture events from game engine"""
        event_queue.append(event)

    async def event_generator():
        """Generate SSE events as game progresses"""
        try:
            # Initialize game
            await engine.initialize_game()

            # Set up event streaming
            engine.set_event_callback(emit_event)

            # Emit game start
            yield f"data: {json.dumps({'type': 'game_start', 'players': [{'id': p.player_id, 'model': p.model_name} for p in engine.players]})}\n\n"
            await asyncio.sleep(0.1)

            # Run rounds
            for round_num in range(1, engine.config.num_rounds + 1):
                engine.current_round = round_num

                # Round start
                yield f"data: {json.dumps({'type': 'round_start', 'round': round_num, 'total_rounds': engine.config.num_rounds})}\n\n"
                await asyncio.sleep(0.5)

                # Execute clue round (will emit events via callback)
                queue_start = len(event_queue)
                await engine._execute_clue_round()

                # Stream queued clue events
                for event in event_queue[queue_start:]:
                    yield f"data: {json.dumps(event)}\n\n"
                    await asyncio.sleep(0.3)

                # Round end
                yield f"data: {json.dumps({'type': 'round_end', 'round': round_num})}\n\n"
                await asyncio.sleep(0.5)

            # Voting
            yield f"data: {json.dumps({'type': 'voting_start'})}\n\n"
            await asyncio.sleep(0.5)

            queue_start = len(event_queue)
            await engine._execute_voting()

            # Stream vote events
            for event in event_queue[queue_start:]:
                yield f"data: {json.dumps(event)}\n\n"
                await asyncio.sleep(0.3)

            # Calculate results
            result = engine._calculate_results()

            # Game complete
            result_data = {
                'type': 'game_complete',
                'result': {
                    'word': result.word,
                    'category': result.category,
                    'actual_imposters': result.actual_imposters,
                    'eliminated_players': result.eliminated_players,
                    'detection_accuracy': result.detection_accuracy,
                    'total_rounds': result.total_rounds
                }
            }

            yield f"data: {json.dumps(result_data)}\n\n"

            # Save history
            history.save_game_result(result_data['result'])

        except Exception as e:
            logger.exception("Error in game stream")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/game/{game_id}/history")
async def get_game_history(game_id: str):
    """Retrieve complete game history"""
    history = GameHistory.load_game(game_id)

    if not history:
        raise HTTPException(status_code=404, detail="Game not found")

    return history


@app.get("/api/games/list")
async def list_games(limit: int = 10):
    """List recent games"""
    conn = sqlite3.connect("./data/games.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, word, category, num_players, num_imposters, created_at, result
        FROM games
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))

    games = []
    for row in cursor.fetchall():
        games.append({
            "id": row[0],
            "word": row[1],
            "category": row[2],
            "num_players": row[3],
            "num_imposters": row[4],
            "created_at": row[5],
            "result": json.loads(row[6]) if row[6] else None
        })

    conn.close()

    return {"games": games}


# Import for SSE (need these in scope)
from ..ai.schemas import ClueResponse, VoteResponse
