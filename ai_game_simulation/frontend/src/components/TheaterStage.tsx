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
  // History navigation
  selectedEventIndex: number | null;
  isViewingHistory: boolean;
  onSelectEvent: (index: number) => void;
  onGoToLive: () => void;
}

export const TheaterStage: React.FC<TheaterStageProps> = ({
  currentClue,
  allClues,
  players,
  currentRound,
  totalRounds,
  selectedEventIndex,
  isViewingHistory,
  onSelectEvent,
  onGoToLive
}) => {
  // Determine which clue to show in spotlight
  // If viewing history, show the selected clue; otherwise show the latest
  const displayedClue = isViewingHistory && selectedEventIndex !== null
    ? allClues[selectedEventIndex] || null
    : currentClue;

  const currentPlayer = displayedClue
    ? players.find(p => p.id === displayedClue.player_id)
    : null;

  return (
    <div className="theater-stage">
      {/* Main spotlight - current player */}
      <div className={`spotlight-area ${isViewingHistory ? 'viewing-history' : ''}`}>
        {/* History mode indicator */}
        {isViewingHistory && (
          <div className="history-indicator">
            <span className="history-badge">⏮ Viewing History</span>
            <span className="history-position">
              {selectedEventIndex !== null ? selectedEventIndex + 1 : 0} / {allClues.length}
            </span>
            <button className="return-to-live-btn" onClick={onGoToLive}>
              Return to Live →
            </button>
          </div>
        )}

        {displayedClue && currentPlayer ? (
          <div className={`player-performance ${displayedClue.role}`}>
            {/* Player info header */}
            <div className="performance-header">
              <div className="player-badge">
                <div className="player-avatar-large">
                  {currentPlayer.id.slice(-1)}
                </div>
                <div className="player-details">
                  <div className="player-name">{currentPlayer.id}</div>
                  <div className="player-model">{currentPlayer.model}</div>
                  <div className="round-indicator">Round {displayedClue.round}</div>
                </div>
              </div>

              {/* Role indicator (only show if imposter for visual interest) */}
              {displayedClue.role === 'imposter' && (
                <div className="role-badge imposter">
                  <span className="badge-icon">🎭</span>
                  <span className="badge-text">Imposter</span>
                  {displayedClue.word_hypothesis && (
                    <span className="guess-text">Guessing: {displayedClue.word_hypothesis}</span>
                  )}
                </div>
              )}

              {/* Confidence meter */}
              <div className="confidence-display">
                <div className="confidence-label">{displayedClue.confidence}% confident</div>
                <div className="confidence-bar">
                  <div
                    className="confidence-fill"
                    style={{ width: `${displayedClue.confidence}%` }}
                  />
                </div>
              </div>
            </div>

            {/* The clue - LARGE and centered */}
            <div className="clue-spotlight">
              <div className="clue-label">Their Clue:</div>
              <div className="clue-word-massive">
                "{displayedClue.clue}"
              </div>
            </div>

            {/* The thinking - readable, prominent */}
            <div className="thinking-display">
              <div className="thinking-label">💭 Inner Monologue:</div>
              <div className="thinking-text">
                {displayedClue.thinking}
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
            const isImposter = clue.role === 'imposter';
            const isSelected = selectedEventIndex === index;
            const isLatest = index === allClues.length - 1 && !isViewingHistory;
            const prevClue = index > 0 ? allClues[index - 1] : null;
            const isNewRound = !prevClue || prevClue.round !== clue.round;

            return (
              <React.Fragment key={index}>
                {/* Round divider */}
                {isNewRound && (
                  <div className="timeline-round-header">
                    <span className="round-line" />
                    <span className="round-label">Round {clue.round}</span>
                    <span className="round-line" />
                  </div>
                )}

                <div
                  className={`timeline-item ${isImposter ? 'imposter' : 'normal'} ${isSelected ? 'selected' : ''} ${isLatest ? 'current' : ''}`}
                  onClick={() => onSelectEvent(index)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => e.key === 'Enter' && onSelectEvent(index)}
                >
                  <div className="timeline-marker">
                    {isSelected ? '👁' : isImposter ? '🎭' : '✓'}
                  </div>
                  <div className="timeline-content">
                    <div className="timeline-meta">
                      <span className="timeline-player">{clue.player_id}</span>
                      <span className="timeline-round">R{clue.round}</span>
                    </div>
                    <div className="timeline-clue">"{clue.clue}"</div>
                    {clue.role === 'imposter' && clue.word_hypothesis && (
                      <div className="timeline-guess">→ {clue.word_hypothesis}</div>
                    )}
                  </div>
                </div>
              </React.Fragment>
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
