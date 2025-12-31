/**
 * TheaterStage - Main gameplay view with clue + thinking together
 * "Watch the AI take the stage" - one player spotlight at a time
 */

import React from 'react';
import type { ClueEvent, Player } from '../types/game';
import './TheaterStage.css';

interface TheaterStageProps {
  currentClue: ClueEvent | null;
  allClues: ClueEvent[];
  players: Player[];
  currentRound: number;
  totalRounds: number;
}

export const TheaterStage: React.FC<TheaterStageProps> = ({
  currentClue,
  allClues,
  players,
  currentRound,
  totalRounds
}) => {
  const currentPlayer = currentClue
    ? players.find(p => p.id === currentClue.player_id)
    : null;

  return (
    <div className="theater-stage">
      {/* Main spotlight - current player */}
      <div className="spotlight-area">
        {currentClue && currentPlayer ? (
          <div className={`player-performance ${currentClue.role}`}>
            {/* Player info header */}
            <div className="performance-header">
              <div className="player-badge">
                <div className="player-avatar-large">
                  {currentPlayer.id.slice(-1)}
                </div>
                <div className="player-details">
                  <div className="player-name">{currentPlayer.id}</div>
                  <div className="player-model">{currentPlayer.model}</div>
                  <div className="round-indicator">Round {currentClue.round}</div>
                </div>
              </div>

              {/* Role indicator (only show if imposter for visual interest) */}
              {currentClue.role === 'imposter' && (
                <div className="role-badge imposter">
                  <span className="badge-icon">🎭</span>
                  <span className="badge-text">Imposter</span>
                  {currentClue.word_hypothesis && (
                    <span className="guess-text">Guessing: {currentClue.word_hypothesis}</span>
                  )}
                </div>
              )}

              {/* Confidence meter */}
              <div className="confidence-display">
                <div className="confidence-label">{currentClue.confidence}% confident</div>
                <div className="confidence-bar">
                  <div
                    className="confidence-fill"
                    style={{ width: `${currentClue.confidence}%` }}
                  />
                </div>
              </div>
            </div>

            {/* The clue - LARGE and centered */}
            <div className="clue-spotlight">
              <div className="clue-label">Their Clue:</div>
              <div className="clue-word-massive">
                "{currentClue.clue}"
              </div>
            </div>

            {/* The thinking - readable, prominent */}
            <div className="thinking-display">
              <div className="thinking-label">💭 Inner Monologue:</div>
              <div className="thinking-text">
                {currentClue.thinking}
              </div>
            </div>
          </div>
        ) : (
          <div className="waiting-state">
            <div className="waiting-icon">⏳</div>
            <div className="waiting-text">Waiting for next player...</div>
          </div>
        )}
      </div>

      {/* Timeline sidebar - condensed history */}
      <div className="timeline-sidebar">
        <div className="timeline-header">
          <h3>📜 Game History</h3>
          <div className="round-progress">Round {currentRound} / {totalRounds}</div>
        </div>

        <div className="timeline-scroll">
          {allClues.map((clue, index) => {
            const player = players.find(p => p.id === clue.player_id);
            const isImposter = clue.role === 'imposter';

            return (
              <div
                key={index}
                className={`timeline-item ${isImposter ? 'imposter' : 'normal'} ${currentClue?.player_id === clue.player_id ? 'current' : ''}`}
              >
                <div className="timeline-marker">
                  {isImposter ? '🎭' : '✓'}
                </div>
                <div className="timeline-content">
                  <div className="timeline-meta">
                    <span className="timeline-player">{clue.player_id}</span>
                    <span className="timeline-round">R{clue.round}</span>
                  </div>
                  <div className="timeline-clue">"{clue.clue}"</div>
                  {clue.word_hypothesis && (
                    <div className="timeline-guess">→ {clue.word_hypothesis}</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Player gallery */}
        <div className="player-gallery">
          <div className="gallery-label">Players</div>
          <div className="gallery-grid">
            {players.map(player => (
              <div
                key={player.id}
                className={`player-chip ${currentPlayer?.id === player.id ? 'active' : ''}`}
              >
                <div className="chip-avatar">{player.id.slice(-1)}</div>
                <div className="chip-label">{player.id}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
