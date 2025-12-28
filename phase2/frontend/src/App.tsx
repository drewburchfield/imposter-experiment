/**
 * Main App - Imposter Mystery AI Game Observer
 * Real-time observation of AI agents playing social deduction game.
 */

import { useState, useMemo } from 'react';
import { PlayerCircle } from './components/PlayerCircle';
import { InnerMonologue } from './components/InnerMonologue';
import { GameControls } from './components/GameControls';
import { ClueDisplay } from './components/ClueDisplay';
import { useGameStream } from './hooks/useGameStream';
import type { Player, ClueEvent } from './types/game';
import './App.css';

function App() {
  const [gameId, setGameId] = useState<string | null>(null);
  const [gameStarted, setGameStarted] = useState(false);

  // Game configuration
  const [config, setConfig] = useState({
    word: 'beach',
    category: 'nature',
    num_players: 6,
    num_imposters: 2,
    num_rounds: 2
  });

  const { events, isPlaying, speed, setSpeed, togglePlay } = useGameStream(gameId);

  // Derive game state from events
  const gameState: {
    players: Player[];
    clues: ClueEvent[];
    currentRound: number;
    currentSpeaker: string | undefined;
    result: { detection_accuracy: number; actual_imposters: string[]; eliminated_players: string[] } | null;
  } = useMemo(() => {
    const players: Player[] = [];
    const clues: ClueEvent[] = [];
    let currentRound = 0;
    let currentSpeaker: string | undefined;
    let result: { detection_accuracy: number; actual_imposters: string[]; eliminated_players: string[] } | null = null;

    events.forEach(event => {
      switch (event.type) {
        case 'game_start':
          players.push(...event.players);
          setGameStarted(true);
          break;

        case 'round_start':
          currentRound = event.round;
          break;

        case 'clue':
          clues.push(event as ClueEvent);
          currentSpeaker = event.player_id;
          break;

        case 'game_complete':
          result = event.result;
          break;
      }
    });

    return { players, clues, currentRound, currentSpeaker, result };
  }, [events]);

  // Thoughts for inner monologue
  const thoughts = useMemo(() => {
    return events
      .filter(e => e.type === 'clue' || e.type === 'vote')
      .map((e, idx) => {
        if (e.type === 'clue') {
          return {
            playerId: e.player_id,
            thinking: e.thinking,
            type: 'clue' as const,
            confidence: e.confidence,
            timestamp: Date.now() - (events.length - idx) * 1000
          };
        } else if (e.type === 'vote') {
          return {
            playerId: e.player_id,
            thinking: e.thinking,
            type: 'vote' as const,
            confidence: e.confidence,
            timestamp: Date.now() - (events.length - idx) * 1000
          };
        }
        return null;
      })
      .filter((t): t is NonNullable<typeof t> => t !== null);
  }, [events]);

  const startGame = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/game/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });

      const data = await response.json();
      setGameId(data.game_id);
    } catch (error) {
      console.error('Failed to create game:', error);
      alert('Failed to create game. Is the backend running?');
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎭 The Imposter Mystery - AI Observer</h1>
        <p>Watch AI agents play social deduction with visible reasoning</p>
      </header>

      {!gameStarted ? (
        <div className="game-setup">
          <h2>Game Setup</h2>
          <div className="setup-form">
            <div className="form-group">
              <label>Secret Word:</label>
              <input
                type="text"
                value={config.word}
                onChange={(e) => setConfig({...config, word: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label>Category:</label>
              <input
                type="text"
                value={config.category}
                onChange={(e) => setConfig({...config, category: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label>Players:</label>
              <input
                type="number"
                value={config.num_players}
                onChange={(e) => setConfig({...config, num_players: parseInt(e.target.value)})}
                min="4"
                max="18"
              />
            </div>
            <div className="form-group">
              <label>Imposters:</label>
              <input
                type="number"
                value={config.num_imposters}
                onChange={(e) => setConfig({...config, num_imposters: parseInt(e.target.value)})}
                min="1"
                max="5"
              />
            </div>
            <div className="form-group">
              <label>Rounds:</label>
              <input
                type="number"
                value={config.num_rounds}
                onChange={(e) => setConfig({...config, num_rounds: parseInt(e.target.value)})}
                min="1"
                max="10"
              />
            </div>
            <button onClick={startGame} className="start-btn">
              Start AI Game
            </button>
          </div>
        </div>
      ) : (
        <>
          <GameControls
            isPlaying={isPlaying}
            speed={speed}
            currentRound={gameState.currentRound}
            totalRounds={config.num_rounds}
            onTogglePlay={togglePlay}
            onSpeedChange={setSpeed}
          />

          <div className="game-layout">
            <div className="left-panel">
              <ClueDisplay clues={gameState.clues} />
            </div>

            <div className="center-panel">
              <PlayerCircle
                players={gameState.players}
                currentSpeaker={gameState.currentSpeaker}
                revealedRoles={!!gameState.result}
              />
              {gameState.result && (
                <div className="result-card">
                  <h2>🏆 Results</h2>
                  <p>Detection Accuracy: {(gameState.result.detection_accuracy * 100).toFixed(1)}%</p>
                  <p>Imposters: {gameState.result.actual_imposters.join(', ')}</p>
                  <p>Eliminated: {gameState.result.eliminated_players.join(', ')}</p>
                </div>
              )}
            </div>

            <div className="right-panel">
              <InnerMonologue
                thoughts={thoughts}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
