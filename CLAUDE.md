# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**The Imposter Experiment** is an educational tool for teaching probability and statistics through social deduction games. It combines two complementary features:

- **Statistical Modeling Page** (`index.html`): Interactive probability simulator demonstrating Law of Large Numbers through the "Jen scenario" (selecting imposter 2 out of 3 times)
- **Interactive Simulation** (`ai_game_simulation/`): AI agents playing the actual imposter game with real-time observation of their reasoning and decision-making

These were built sequentially but are conceptually one unified capability. Future development will merge them with shared navigation.

## Architecture

### Statistical Modeling Page
- **Single-file web app**: `index.html` - No build process, open directly in browser
- **Simulation engine**: Fisher-Yates shuffle for player selection across 3 rounds
- **Visualization**: Chart.js for distribution histograms
- **Key insight**: Demonstrates convergence to theoretical probability (1.61%) as sample size increases

### Interactive Simulation (AI Game Engine)

**Three-tier architecture:**

1. **Backend** (`ai_game_simulation/src/`)
   - `game_engine/` - Core orchestration (state machine, turn coordination)
   - `ai/` - OpenRouter API integration for multiple LLM models
   - `api/` - FastAPI server with SSE streaming for real-time events
   - `utils/` - CLI display and logging utilities

2. **Frontend** (`ai_game_simulation/frontend/`)
   - React + TypeScript + Vite
   - Real-time game observation via SSE
   - Components: PlayerCircle, InnerMonologue, ClueDisplay, GameControls

3. **Data Flow**
   - GameEngine emits events (game_start, round_start, clue, vote, game_complete)
   - Events streamed via SSE to frontend
   - Frontend derives game state from event stream (no direct state management)

**Key architectural decisions:**
- **Event-driven**: All game state changes are events, frontend derives UI from event stream
- **AI independence**: Each player is independent LLM agent with own conversation context
- **Model flexibility**: Supports mixed models per game (Llama, Claude Haiku, Gemini, GPT-4-mini, Mistral)
- **Structured output**: Uses Pydantic schemas for reliable JSON responses from LLMs

## Development Commands

### Interactive Simulation - Backend

```bash
# Setup
cd ai_game_simulation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure (required)
cp .env.example .env
# Add OPENROUTER_API_KEY to .env

# Run CLI game (test game engine without UI)
python cli_game.py --word beach --category nature --players 6 --imposters 2 --rounds 3

# Run CLI with mixed models
python cli_game.py --word beach --category nature --players 6 --imposters 2 --models llama,llama,haiku,haiku,gemini,gpt4-mini

# Start API server (for frontend)
cd src/api
uvicorn main:app --reload --port 8000
```

### Interactive Simulation - Frontend

```bash
cd ai_game_simulation/frontend

# Install dependencies
npm install

# Development server (with HMR)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

### Statistical Modeling Page

```bash
# No build required - open directly
open index.html

# Or serve with any static server
python -m http.server 8000
# Then visit http://localhost:8000
```

## Critical Implementation Details

### Game Engine State Machine (`ai_game_simulation/src/game_engine/engine.py`)

Phases: SETUP → CLUE_ROUND → VOTING → REVEAL → COMPLETE

- **CLUE_ROUND**: All players generate clues simultaneously (imposters don't know secret word)
- **VOTING**: Players vote based on accumulated clue history
- **Context propagation**: Each player maintains `PlayerKnowledge` with all previous clues

### AI Client (`ai_game_simulation/src/ai/`)

Two implementations (SDK preferred over legacy):
- `openrouter_sdk.py` - Uses official OpenAI SDK with OpenRouter base URL
- `openrouter.py` - Legacy aiohttp implementation

**Model configuration:**
```python
AVAILABLE_MODELS = {
    'llama': 'meta-llama/llama-3.1-8b-instruct',      # Fast, cheap, good quality
    'haiku': 'anthropic/claude-3.5-haiku',            # Premium, best reasoning
    'gemini': 'google/gemini-flash-1.5',              # Fast, creative
    'gpt4-mini': 'openai/gpt-4o-mini',                # OpenAI option
    'mistral': 'mistralai/mistral-7b-instruct'        # Alternative budget
}
```

### Pydantic Schemas (`ai_game_simulation/src/ai/schemas.py`)

**Structured JSON enforcement:**
- `ClueResponse`: Player's clue with thinking and confidence
- `VoteResponse`: Suspicion rankings with reasoning
- `ImpostorAnalysis`: Imposter's word hypothesis generation

All LLM calls use `response_format` with Pydantic models to ensure valid JSON.

### Event Streaming (`ai_game_simulation/src/api/main.py`)

**SSE event types:**
- `game_start`: Initial player setup (IDs, roles, models)
- `round_start`: Round number announcement
- `clue`: Player clue with thinking (visible to observers, not other players)
- `vote`: Player vote with reasoning
- `game_complete`: Final results with detection accuracy

Frontend uses `useGameStream` hook to consume SSE and build event list.

### Frontend State Derivation (`ai_game_simulation/frontend/src/App.tsx`)

```typescript
// State is computed from events, not managed directly
const gameState = useMemo(() => {
  const players = [];
  const clues = [];

  events.forEach(event => {
    if (event.type === 'game_start') players.push(...event.players);
    if (event.type === 'clue') clues.push(event);
    // etc.
  });

  return { players, clues, currentRound, result };
}, [events]);
```

This approach makes time-travel debugging possible and ensures UI consistency.

## Environment Variables

### Interactive Simulation Backend (`.env`)
```
OPENROUTER_API_KEY=sk-or-v1-...     # Required - from openrouter.ai
DATABASE_PATH=./data/games.db        # Optional - defaults shown
DEFAULT_MODEL=meta-llama/llama-3.1-8b-instruct
LOG_LEVEL=INFO
```

## Testing Strategy

**Statistical Modeling Page:** Manual testing via browser (no automated tests)

**Interactive Simulation:**
- **CLI testing**: Use `cli_game.py` to validate game logic without frontend
- **API testing**: Start server and monitor `/api/game/create` and `/api/game/{game_id}/stream`
- **Model testing**: Run games with different model distributions to compare performance

No formal test suite exists currently - validation is primarily manual through CLI observation.

## Common Workflows

### Testing a new AI model

1. Add model to `AVAILABLE_MODELS` in `ai_game_simulation/src/ai/openrouter.py`
2. Test with CLI: `python cli_game.py --word test --category misc --players 4 --imposters 1 --models llama,newmodel,llama,llama`
3. Observe clue quality and vote reasoning in CLI output

### Debugging game logic

1. Run CLI with `visual_mode=True` (default) to see round-by-round progression
2. Check `ai_game_simulation/data/games.db` for historical game records
3. Add logging in `game_engine/engine.py` at state transitions

### Frontend development

1. Start backend: `cd ai_game_simulation/src/api && uvicorn main:app --reload`
2. Start frontend: `cd ai_game_simulation/frontend && npm run dev`
3. Create game via GameControls component
4. Stream automatically connects to `http://localhost:8000/api/game/{game_id}/stream`

## Deployment

**Statistical Modeling Page:** Static hosting (already configured for fly.io via `Dockerfile` + nginx)

**Interactive Simulation:**
- Backend: FastAPI serves both API and static frontend
- Frontend: Built into `dist/`, mounted by FastAPI as static files
- Database: SQLite file persisted in container volume

Current deployment target: `imposter-experiment.fly.dev`
