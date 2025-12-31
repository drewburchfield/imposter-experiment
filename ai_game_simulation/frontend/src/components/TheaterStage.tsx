/**
 * TheaterStage - Main gameplay view with clue + thinking together
 * "Watch the AI take the stage" - one player spotlight at a time
 */

import React, { useRef } from 'react';
import type { ClueEvent, Player } from '../types/game';
import './TheaterStage.css';

interface TheaterStageProps {
  currentClue: ClueEvent | null;
  allClues: ClueEvent[];
  players: Player[];
  currentRound: number;
  totalRounds: number;
  // Game context for loading states
  word: string;
  category: string;
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
  word,
  category,
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

  // Ref for timeline scroll container
  const timelineScrollRef = useRef<HTMLDivElement>(null);

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
            {/* Contextual loading based on game phase */}
            {currentRound === 0 ? (
              // Game initializing - no round_start yet
              <>
                <div className="waiting-icon pulse">🎭</div>
                <div className="waiting-title">Game Starting...</div>
                <div className="waiting-context">
                  <div className="context-item">
                    <span className="context-label">Category:</span>
                    <span className="context-value">{category}</span>
                  </div>
                  <div className="context-item">
                    <span className="context-label">Secret Word:</span>
                    <span className="context-value secret">{word}</span>
                  </div>
                  <div className="context-item">
                    <span className="context-label">Players:</span>
                    <span className="context-value">{players.length > 0 ? players.length : '...'}</span>
                  </div>
                </div>
                <div className="waiting-subtitle">Assigning roles to AI agents...</div>
              </>
            ) : allClues.filter(c => c.round === currentRound).length === 0 ? (
              // Round started but no clues yet in this round
              <>
                <div className="waiting-icon pulse">💭</div>
                <div className="waiting-title">Round {currentRound} Starting</div>
                <div className="waiting-context">
                  <div className="context-item">
                    <span className="context-label">Category:</span>
                    <span className="context-value">{category}</span>
                  </div>
                  <div className="context-item">
                    <span className="context-label">Secret Word:</span>
                    <span className="context-value secret">{word}</span>
                  </div>
                </div>
                <div className="waiting-subtitle">AI agents are thinking of clues...</div>
                <div className="thinking-dots">
                  <span>.</span><span>.</span><span>.</span>
                </div>
              </>
            ) : (
              // Between players in a round
              <>
                <div className="waiting-icon">⏳</div>
                <div className="waiting-title">Waiting for next player...</div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Timeline sidebar - condensed history */}
      <div className="timeline-sidebar">
        <div className="timeline-header">
          <h3>📜 Game History</h3>
          <div className="round-progress">Round {currentRound} / {totalRounds}</div>
        </div>

        <div className="timeline-scroll" ref={timelineScrollRef}>
          {/* Group clues by round, then display rounds in descending order (newest first) */}
          {(() => {
            // Group clues by round, keeping track of original indices
            const cluesByRound: { [round: number]: { clue: typeof allClues[0]; originalIndex: number }[] } = {};
            allClues.forEach((clue, index) => {
              if (!cluesByRound[clue.round]) {
                cluesByRound[clue.round] = [];
              }
              cluesByRound[clue.round].push({ clue, originalIndex: index });
            });

            // Get rounds sorted descending (newest first)
            const rounds = Object.keys(cluesByRound).map(Number).sort((a, b) => b - a);

            return rounds.map(round => (
              <div key={round} className="timeline-round-block">
                {/* Round header */}
                <div className={`timeline-round-header ${round === currentRound ? 'current-round' : ''}`}>
                  <span className="round-line" />
                  <span className="round-label">Round {round}</span>
                  <span className="round-line" />
                </div>

                {/* Clues within this round (chronological order) */}
                {cluesByRound[round].map(({ clue, originalIndex }) => {
                  const isImposter = clue.role === 'imposter';
                  const isSelected = selectedEventIndex === originalIndex;
                  const isLatest = originalIndex === allClues.length - 1 && !isViewingHistory;

                  return (
                    <div
                      key={originalIndex}
                      className={`timeline-item ${isImposter ? 'imposter' : 'normal'} ${isSelected ? 'selected' : ''} ${isLatest ? 'current' : ''}`}
                      onClick={() => onSelectEvent(originalIndex)}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => e.key === 'Enter' && onSelectEvent(originalIndex)}
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
                  );
                })}
              </div>
            ));
          })()}
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
