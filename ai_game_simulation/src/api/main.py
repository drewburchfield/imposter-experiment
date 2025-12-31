"""
FastAPI backend for AI Imposter Game Simulation
Provides REST API and Server-Sent Events (SSE) streaming for real-time game observation.
"""

import asyncio
import uuid
import os
import logging
import sqlite3
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

@app.get("/health")
async def health_check():
    """Health check endpoint for fly.io"""
    return {"status": "healthy"}


@app.get("/api/status")
async def api_status():
    """API status info"""
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
    # Note: If model_distribution not provided, GameConfig uses its own tested defaults
    config = GameConfig(
        word=request.word,
        category=request.category,
        num_players=request.num_players,
        num_imposters=request.num_imposters,
        num_rounds=request.num_rounds,
        model_strategy=request.model_strategy,
        model_distribution=request.model_distribution,  # Let GameConfig handle None case
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

    Streams events IMMEDIATELY as they happen (no batching):
    - round_start
    - clue (with player thoughts) - streamed as each LLM responds
    - round_end
    - voting_start
    - vote (with analysis) - streamed as each LLM responds
    - game_complete (with results)
    """
    engine = game_sessions.get(game_id)
    history = game_histories.get(game_id)

    if not engine or not history:
        raise HTTPException(status_code=404, detail="Game not found")

    # Use async queue for real-time streaming
    event_queue: asyncio.Queue = asyncio.Queue()

    async def emit_event(event):
        """Callback to immediately queue events for streaming"""
        await event_queue.put(event)

    async def run_game():
        """Run the game engine and emit events"""
        try:
            # Initialize game
            await engine.initialize_game()

            # Set up event streaming
            engine.set_event_callback(emit_event)

            # Emit game start
            await event_queue.put({
                'type': 'game_start',
                'players': [{'id': p.player_id, 'model': p.model_name} for p in engine.players]
            })

            # Run rounds
            for round_num in range(1, engine.config.num_rounds + 1):
                engine.current_round = round_num

                # Round start
                await event_queue.put({
                    'type': 'round_start',
                    'round': round_num,
                    'total_rounds': engine.config.num_rounds
                })

                # Execute clue round - events emitted via callback as they happen
                await engine._execute_clue_round()

                # Round end
                await event_queue.put({'type': 'round_end', 'round': round_num})

            # Voting
            await event_queue.put({'type': 'voting_start'})

            # Execute voting - events emitted via callback as they happen
            await engine._execute_voting()

            # Calculate results
            result = engine._calculate_results()

            # Game complete
            await event_queue.put({
                'type': 'game_complete',
                'result': {
                    'word': result.word,
                    'category': result.category,
                    'actual_imposters': result.actual_imposters,
                    'eliminated_players': result.eliminated_players,
                    'detection_accuracy': result.detection_accuracy,
                    'total_rounds': result.total_rounds
                }
            })

            # Save history
            history.save_game_result({
                'word': result.word,
                'category': result.category,
                'actual_imposters': result.actual_imposters,
                'eliminated_players': result.eliminated_players,
                'detection_accuracy': result.detection_accuracy,
                'total_rounds': result.total_rounds
            })

        except Exception as e:
            logger.exception("Error in game execution")
            await event_queue.put({'type': 'error', 'message': str(e)})
        finally:
            # Signal end of stream
            await event_queue.put(None)

    async def event_generator():
        """Generate SSE events as they arrive from the queue"""
        # Start game in background task
        game_task = asyncio.create_task(run_game())

        try:
            while True:
                try:
                    # Wait for event with timeout for keepalive
                    event = await asyncio.wait_for(event_queue.get(), timeout=15.0)

                    # None signals end of stream
                    if event is None:
                        break

                    # Stream event immediately
                    yield f"data: {json.dumps(event)}\n\n"

                except asyncio.TimeoutError:
                    # Send keepalive comment to prevent proxy timeout
                    yield ": keepalive\n\n"
                    continue

        except asyncio.CancelledError:
            game_task.cancel()
            raise
        except Exception as e:
            logger.exception("Error in event generator")
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


# ============================================
# STATIC FILE SERVING
# ============================================

# Serve static frontend files in production
# The frontend is built to /app/frontend/dist in the Docker container
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"

if frontend_dist.exists():
    # Mount static assets (JS, CSS, etc.)
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    # Serve index.html for root and all unmatched routes (SPA routing)
    @app.get("/")
    async def serve_spa():
        """Serve the React SPA"""
        index_file = frontend_dist / "index.html"
        return HTMLResponse(content=index_file.read_text())

    @app.get("/{full_path:path}")
    async def serve_spa_fallback(full_path: str):
        """Fallback for client-side routing"""
        # Don't intercept API routes
        if full_path.startswith("api/") or full_path == "health":
            raise HTTPException(status_code=404)

        # Try to serve static file first
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return HTMLResponse(content=file_path.read_text())

        # Fallback to index.html for client-side routing
        index_file = frontend_dist / "index.html"
        return HTMLResponse(content=index_file.read_text())
else:
    # Development mode - no frontend build
    @app.get("/")
    async def root():
        """Development mode placeholder"""
        return {
            "app": "Imposter Mystery AI Game",
            "version": "2.0.0",
            "status": "running",
            "mode": "development",
            "note": "Frontend not built. Run 'npm run build' in frontend/ directory."
        }
