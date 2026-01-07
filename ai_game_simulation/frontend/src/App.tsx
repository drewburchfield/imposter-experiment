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

  // Game configuration with explicit typing
  interface GameSetupConfig {
    word: string;
    category: string;
    num_players: number;
    num_imposters: number;
    num_rounds: number;      // Clue rounds
    voting_rounds: number;   // Voting rounds (max = num_imposters)
  }

  const [config, setConfig] = useState<GameSetupConfig>({
    word: 'beach',
    category: 'nature',
    num_players: 6,
    num_imposters: 2,
    num_rounds: 2,
    voting_rounds: 2
  });

  // Auto-adjust voting_rounds when num_imposters changes
  // Default: min(2, num_imposters), Max: num_imposters
  useEffect(() => {
    const maxVotingRounds = config.num_imposters;
    const defaultVotingRounds = Math.min(2, config.num_imposters);

    // Clamp if current voting_rounds exceeds new max
    if (config.voting_rounds > maxVotingRounds) {
      setConfig(prev => ({ ...prev, voting_rounds: maxVotingRounds }));
    }
    // Set default if voting_rounds is invalid
    else if (!config.voting_rounds || config.voting_rounds < 1) {
      setConfig(prev => ({ ...prev, voting_rounds: defaultVotingRounds }));
    }
  }, [config.num_imposters]);

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
    stepNext,
    connectionError
  } = useGameStream(gameId);

  // Separate vote selection (votes are inspectable like clues)
  const [selectedVoteIndex, setSelectedVoteIndex] = useState<number | null>(null);

  // When selecting a vote, clear clue selection and vice versa
  const selectVote = useCallback((index: number) => {
    setSelectedVoteIndex(index);
    // Clear clue selection - votes take precedence
    if (selectedEventIndex !== null) {
      goToLive(); // This clears clue selection
    }
  }, [selectedEventIndex, goToLive]);

  const selectClue = useCallback((index: number) => {
    setSelectedVoteIndex(null); // Clear vote selection
    selectEvent(index);
  }, [selectEvent]);

  // Clear vote selection when going to live
  const handleGoToLive = useCallback(() => {
    setSelectedVoteIndex(null);
    goToLive();
  }, [goToLive]);

  // Combined history viewing state
  const isViewingAnyHistory = isViewingHistory || selectedVoteIndex !== null;

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
    thinkingPlayer: { playerId: string; model: string; action: 'clue' | 'vote'; index: number; total: number } | null;
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
    let thinkingPlayer: { playerId: string; model: string; action: 'clue' | 'vote'; index: number; total: number } | null = null;
    let result: { detection_accuracy: number; actual_imposters: string[]; eliminated_players: string[] } | null = null;

    events.forEach(event => {
      switch (event.type) {
        case 'game_start':
          players.push(...event.players);
          break;

        case 'round_start':
          currentRound = event.round;
          thinkingPlayer = null; // Reset when new round starts
          break;

        case 'player_thinking':
          thinkingPlayer = {
            playerId: event.player_id,
            model: event.player_model,
            action: event.action,
            index: event.player_index,
            total: event.total_players
          };
          break;

        case 'clue':
          clues.push(event as ClueEvent);
          currentSpeaker = event.player_id;
          thinkingPlayer = null; // Clear thinking when clue arrives
          break;

        case 'voting_start':
          isVotingPhase = true;
          thinkingPlayer = null;
          break;

        case 'voting_round_start':
          currentVotingRound = event.voting_round;
          totalVotingRounds = event.total_voting_rounds;
          thinkingPlayer = null;
          break;

        case 'vote':
          votes.push(event as VoteEvent);
          currentSpeaker = event.player_id;
          thinkingPlayer = null; // Clear thinking when vote arrives
          break;

        case 'elimination':
          eliminations.push(event as EliminationEvent);
          break;

        case 'game_complete':
          result = event.result;
          thinkingPlayer = null;
          break;
      }
    });

    return { players, clues, votes, eliminations, currentRound, currentVotingRound, totalVotingRounds, currentSpeaker, isVotingPhase, thinkingPlayer, result };
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
          } else if (isViewingAnyHistory) {
            handleGoToLive();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [togglePlay, stepPrev, stepNext, handleGoToLive, isViewingAnyHistory, showResultsModal]);

  const startGame = async () => {
    try {
      // Map frontend config to API format
      const apiConfig = {
        word: config.word,
        category: config.category,
        num_players: config.num_players,
        num_imposters: config.num_imposters,
        num_rounds: config.num_rounds,
        num_voting_rounds: config.voting_rounds  // Frontend uses voting_rounds, API uses num_voting_rounds
      };

      const response = await fetch(`${API_BASE_URL}/api/game/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(apiConfig)
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
        <div className="app-header-title">
          <h1>🎭 The Imposter Mystery - AI Observer</h1>
          <p>Watch AI agents play social deduction with visible reasoning</p>
        </div>
        <div className="header-links">
          <a href="https://imposter.drewburchfield.com/" className="cta-button" title="Monte Carlo probability simulator">
            <svg height="22" width="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 3v18h18"/>
              <path d="M7 16l4-8 4 4 6-10"/>
            </svg>
            Monte Carlo Probability Simulator
          </a>
          <a href="https://github.com/drewburchfield/imposter-experiment" target="_blank" rel="noopener noreferrer" className="header-link" aria-label="View on GitHub">
            <svg height="20" width="20" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
            </svg>
          </a>
        </div>
      </header>

      {/* Error Banner */}
      {connectionError && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span className="error-message">{connectionError}</span>
          <button className="error-action" onClick={startNewGame}>
            Start New Game
          </button>
        </div>
      )}

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
              <label>Clue Rounds:</label>
              <input
                type="number"
                value={config.num_rounds}
                onChange={(e) => setConfig({...config, num_rounds: parseInt(e.target.value) || 2})}
                min="1"
                max="10"
              />
            </div>
            <div className="form-group">
              <label>Voting Rounds:</label>
              <input
                type="number"
                value={config.voting_rounds}
                onChange={(e) => {
                  const value = parseInt(e.target.value) || 1;
                  // Clamp to valid range: 1 to num_imposters
                  const clamped = Math.max(1, Math.min(value, config.num_imposters));
                  setConfig({...config, voting_rounds: clamped});
                }}
                min="1"
                max={config.num_imposters}
              />
              <span className="form-hint">(max: {config.num_imposters})</span>
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
            thinkingPlayer={gameState.thinkingPlayer}
            players={gameState.players}
            currentRound={gameState.currentRound}
            totalRounds={config.num_rounds}
            word={config.word}
            category={config.category}
            selectedClueIndex={selectedEventIndex}
            selectedVoteIndex={selectedVoteIndex}
            isViewingHistory={isViewingAnyHistory}
            onSelectClue={selectClue}
            onSelectVote={selectVote}
            onGoToLive={handleGoToLive}
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
