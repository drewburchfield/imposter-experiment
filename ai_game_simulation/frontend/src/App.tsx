/**
 * Main App - Imposter Mystery AI Game Observer
 * Real-time observation of AI agents playing social deduction game.
 */

import { useState, useMemo, useEffect, useCallback } from 'react';
import { GameControls } from './components/GameControls';
import { TheaterStage } from './components/TheaterStage';
import { ImposterReveal } from './components/ImposterReveal';
import { useGameStream } from './hooks/useGameStream';
import { API_BASE_URL } from './config/api';
import type { Player, ClueEvent, VoteEvent, EliminationEvent } from './types/game';
import './App.css';

function App() {
  const [gameId, setGameId] = useState<string | null>(null);
  const [gameStarted, setGameStarted] = useState(false);
  const [showResultsModal, setShowResultsModal] = useState(false);

  // Game configuration
  const [config, setConfig] = useState({
    word: 'beach',
    category: 'nature',
    num_players: 6,
    num_imposters: 2,
    num_rounds: 2
  });

  const {
    events,
    isPlaying,
    speed,
    setSpeed,
    togglePlay,
    selectedEventIndex,
    isViewingHistory,
    selectEvent,
    goToLive,
    stepPrev,
    stepNext
  } = useGameStream(gameId);

  // Derive game state from events
  // Handle game start separately to avoid setState in useMemo
  useEffect(() => {
    const hasGameStart = events.some(e => e.type === 'game_start');
    if (hasGameStart && !gameStarted) {
      setGameStarted(true);
    }
  }, [events, gameStarted]);

  const gameState: {
    players: Player[];
    clues: ClueEvent[];
    votes: VoteEvent[];
    eliminations: EliminationEvent[];
    currentRound: number;
    currentVotingRound: number;
    totalVotingRounds: number;
    currentSpeaker: string | undefined;
    isVotingPhase: boolean;
    result: { detection_accuracy: number; actual_imposters: string[]; eliminated_players: string[] } | null;
  } = useMemo(() => {
    const players: Player[] = [];
    const clues: ClueEvent[] = [];
    const votes: VoteEvent[] = [];
    const eliminations: EliminationEvent[] = [];
    let currentRound = 0;
    let currentVotingRound = 0;
    let totalVotingRounds = 0;
    let currentSpeaker: string | undefined;
    let isVotingPhase = false;
    let result: { detection_accuracy: number; actual_imposters: string[]; eliminated_players: string[] } | null = null;

    events.forEach(event => {
      switch (event.type) {
        case 'game_start':
          players.push(...event.players);
          break;

        case 'round_start':
          currentRound = event.round;
          break;

        case 'clue':
          clues.push(event as ClueEvent);
          currentSpeaker = event.player_id;
          break;

        case 'voting_start':
          isVotingPhase = true;
          break;

        case 'voting_round_start':
          currentVotingRound = event.voting_round;
          totalVotingRounds = event.total_voting_rounds;
          break;

        case 'vote':
          votes.push(event as VoteEvent);
          currentSpeaker = event.player_id;
          break;

        case 'elimination':
          eliminations.push(event as EliminationEvent);
          break;

        case 'game_complete':
          result = event.result;
          break;
      }
    });

    return { players, clues, votes, eliminations, currentRound, currentVotingRound, totalVotingRounds, currentSpeaker, isVotingPhase, result };
  }, [events]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't capture when typing in inputs
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.code) {
        case 'Space':
          e.preventDefault();
          togglePlay();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          stepPrev();
          break;
        case 'ArrowRight':
          e.preventDefault();
          stepNext();
          break;
        case 'Escape':
          e.preventDefault();
          if (showResultsModal) {
            setShowResultsModal(false);
          } else if (isViewingHistory) {
            goToLive();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [togglePlay, stepPrev, stepNext, goToLive, isViewingHistory, showResultsModal]);

  const startGame = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/game/create`, {
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

  // Reset everything for a new game
  const startNewGame = useCallback(() => {
    setGameId(null);
    setGameStarted(false);
    setShowResultsModal(false);
  }, []);

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
                onChange={(e) => setConfig({...config, num_players: parseInt(e.target.value) || 6})}
                min="4"
                max="18"
              />
            </div>
            <div className="form-group">
              <label>Imposters:</label>
              <input
                type="number"
                value={config.num_imposters}
                onChange={(e) => setConfig({...config, num_imposters: parseInt(e.target.value) || 2})}
                min="1"
                max="5"
              />
            </div>
            <div className="form-group">
              <label>Rounds:</label>
              <input
                type="number"
                value={config.num_rounds}
                onChange={(e) => setConfig({...config, num_rounds: parseInt(e.target.value) || 2})}
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
            gameComplete={!!gameState.result}
            onShowResults={() => setShowResultsModal(true)}
            onNewGame={startNewGame}
          />

          <TheaterStage
            currentClue={gameState.clues[gameState.clues.length - 1] || null}
            allClues={gameState.clues}
            allVotes={gameState.votes}
            currentVote={gameState.votes[gameState.votes.length - 1] || null}
            allEliminations={gameState.eliminations}
            isVotingPhase={gameState.isVotingPhase}
            currentVotingRound={gameState.currentVotingRound}
            totalVotingRounds={gameState.totalVotingRounds}
            players={gameState.players}
            currentRound={gameState.currentRound}
            totalRounds={config.num_rounds}
            word={config.word}
            category={config.category}
            selectedEventIndex={selectedEventIndex}
            isViewingHistory={isViewingHistory}
            onSelectEvent={selectEvent}
            onGoToLive={goToLive}
            gameComplete={!!gameState.result}
          />

          {/* Results Modal */}
          {showResultsModal && gameState.result && (
            <div className="results-modal-overlay" onClick={() => setShowResultsModal(false)}>
              <div className="results-modal" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close-btn" onClick={() => setShowResultsModal(false)}>
                  ✕
                </button>
                <ImposterReveal
                  imposters={gameState.result.actual_imposters}
                  eliminated={gameState.result.eliminated_players}
                  players={gameState.players}
                  detectionAccuracy={gameState.result.detection_accuracy}
                  word={config.word}
                />
                <div className="modal-actions">
                  <button className="modal-new-game-btn" onClick={startNewGame}>
                    🎭 New Game
                  </button>
                  <button className="modal-dismiss-btn" onClick={() => setShowResultsModal(false)}>
                    Review Game History
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;
