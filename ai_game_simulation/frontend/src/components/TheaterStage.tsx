/**
 * TheaterStage - Main gameplay view with clue + thinking together
 * "Watch the AI take the stage" - one player spotlight at a time
 */

import React, { useRef } from 'react';
import type { ClueEvent, VoteEvent, EliminationEvent, Player } from '../types/game';
import './TheaterStage.css';

interface TheaterStageProps {
  currentClue: ClueEvent | null;
  allClues: ClueEvent[];
  // Voting phase - sequential voting with eliminations
  currentVote: VoteEvent | null;
  allVotes: VoteEvent[];
  allEliminations: EliminationEvent[];
  isVotingPhase: boolean;
  currentVotingRound: number;
  totalVotingRounds: number;
  // Current player generating content
  thinkingPlayer: { playerId: string; model: string; action: 'clue' | 'vote'; index: number; total: number } | null;
  // Core game state
  players: Player[];
  currentRound: number;
  totalRounds: number;
  // Game context for loading states
  word: string;
  category: string;
  // History navigation - clues
  selectedClueIndex: number | null;
  // History navigation - votes (now inspectable like clues)
  selectedVoteIndex: number | null;
  isViewingHistory: boolean;
  onSelectClue: (index: number) => void;
  onSelectVote: (index: number) => void;
  onGoToLive: () => void;
  // Game completion
  gameComplete?: boolean;
  // Buffer status
  isBuffering?: boolean;
}

export const TheaterStage: React.FC<TheaterStageProps> = ({
  currentClue,
  allClues,
  currentVote,
  allVotes,
  allEliminations,
  isVotingPhase,
  currentVotingRound,
  totalVotingRounds,
  thinkingPlayer,
  players,
  currentRound,
  totalRounds,
  word,
  category,
  selectedClueIndex,
  selectedVoteIndex,
  isViewingHistory,
  onSelectClue,
  onSelectVote,
  onGoToLive,
  gameComplete,
  isBuffering
}) => {
  // Determine which clue to show in spotlight
  // If viewing clue history, show the selected clue; otherwise show the latest
  const displayedClue = selectedClueIndex !== null
    ? allClues[selectedClueIndex] || null
    : currentClue;

  const cluePlayer = displayedClue
    ? players.find(p => p.id === displayedClue.player_id)
    : null;

  // Voting phase: determine which vote to display
  // If viewing vote history, show the selected vote; otherwise show the latest
  const displayedVote = selectedVoteIndex !== null
    ? allVotes[selectedVoteIndex] || null
    : currentVote;

  const votePlayer = displayedVote
    ? players.find(p => p.id === displayedVote.player_id)
    : null;

  // Are we viewing a selected vote from history?
  const isViewingVoteHistory = selectedVoteIndex !== null;

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
              {isViewingVoteHistory
                ? `Vote ${selectedVoteIndex !== null ? selectedVoteIndex + 1 : 0} / ${allVotes.length}`
                : `Clue ${selectedClueIndex !== null ? selectedClueIndex + 1 : 0} / ${allClues.length}`
              }
            </span>
            <button className="return-to-live-btn" onClick={onGoToLive}>
              Return to Live →
            </button>
          </div>
        )}

        {/* VOTING PHASE or viewing vote history: Show vote deliberation */}
        {(isVotingPhase || isViewingVoteHistory) && displayedVote && votePlayer ? (
          <div className="player-performance voting">
            {/* Player info header */}
            <div className="performance-header">
              <div className="player-badge">
                <div className="player-avatar-large voting">
                  {votePlayer.id.slice(-1)}
                </div>
                <div className="player-details">
                  <div className="player-name">{votePlayer.id}</div>
                  <div className="player-model">{votePlayer.model}</div>
                  <div className="round-indicator voting">
                    🗳️ Voting Round {displayedVote.voting_round} of {totalVotingRounds}
                  </div>
                </div>
              </div>

              {/* Confidence meter */}
              <div className="confidence-display">
                <div className="confidence-label">{displayedVote.confidence}% confident</div>
                <div className="confidence-bar">
                  <div
                    className="confidence-fill voting"
                    style={{ width: `${displayedVote.confidence}%` }}
                  />
                </div>
              </div>
            </div>

            {/* The single vote - who they're voting to eliminate */}
            <div className="vote-spotlight">
              <div className="vote-label">Voting to eliminate:</div>
              <div className="vote-target">
                <span className="target-name">{displayedVote.vote}</span>
              </div>
              <div className="vote-reasoning">{displayedVote.reasoning}</div>
            </div>

            {/* Running vote tally */}
            {displayedVote.votes_so_far && Object.keys(displayedVote.votes_so_far).length > 0 && (
              <div className="vote-tally">
                <div className="tally-label">
                  Current Vote Tally ({displayedVote.total_votes_cast || '?'} of {displayedVote.total_active_players || '?'} votes):
                </div>
                <div className="tally-list">
                  {Object.entries(displayedVote.votes_so_far)
                    .sort(([, a], [, b]) => b - a)
                    .map(([playerId, count]) => (
                      <div key={playerId} className="tally-item">
                        <span className="tally-player">{playerId}</span>
                        <span className="tally-count">{count} vote{count !== 1 ? 's' : ''}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* The thinking - deliberation process */}
            <div className="thinking-display voting">
              <div className="thinking-label">🗳️ Deliberation:</div>
              <div className="thinking-text">
                {displayedVote.thinking}
              </div>
            </div>
          </div>
        ) : isVotingPhase && !displayedVote ? (
          /* Voting started but no votes yet - show who is thinking */
          <div className="waiting-state">
            <div className="waiting-icon pulse">🗳️</div>
            <div className="waiting-title">Voting Phase</div>
            {thinkingPlayer && thinkingPlayer.action === 'vote' ? (
              <div className="thinking-player-spotlight">
                <div className="thinking-player-info">
                  <span className="thinking-player-name">{thinkingPlayer.playerId}</span>
                  <span className="thinking-player-model">({thinkingPlayer.model})</span>
                </div>
                <div className="thinking-progress">
                  is deliberating... ({thinkingPlayer.index} of {thinkingPlayer.total})
                </div>
                <div className="thinking-bar">
                  <div
                    className="thinking-bar-fill"
                    style={{ width: `${(thinkingPlayer.index / thinkingPlayer.total) * 100}%` }}
                  />
                </div>
              </div>
            ) : (
              <>
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
                <div className="waiting-subtitle">AI agents are analyzing clues and deciding who to eliminate...</div>
              </>
            )}
            <div className="thinking-dots">
              <span>.</span><span>.</span><span>.</span>
            </div>
          </div>
        ) : displayedClue && cluePlayer ? (
          <div className={`player-performance ${displayedClue.role}`}>
            {/* Player info header */}
            <div className="performance-header">
              <div className="player-badge">
                <div className="player-avatar-large">
                  {cluePlayer.id.slice(-1)}
                </div>
                <div className="player-details">
                  <div className="player-name">{cluePlayer.id}</div>
                  <div className="player-model">{cluePlayer.model}</div>
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
            {gameComplete ? (
              // Game is complete - show summary prompt
              <>
                <div className="waiting-icon celebration">🏆</div>
                <div className="waiting-title">Game Complete!</div>
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
                    <span className="context-label">Rounds Played:</span>
                    <span className="context-value">{totalRounds}</span>
                  </div>
                </div>
                <div className="waiting-subtitle">
                  Click "Show Results" to see who the imposters were!
                  <br />
                  Use the timeline to review game history.
                </div>
              </>
            ) : currentRound === 0 ? (
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
              // Round started but no clues yet - show who is thinking
              <>
                <div className="waiting-icon pulse">💭</div>
                <div className="waiting-title">Round {currentRound}</div>
                {thinkingPlayer && thinkingPlayer.action === 'clue' ? (
                  <div className="thinking-player-spotlight">
                    <div className="thinking-player-info">
                      <span className="thinking-player-name">{thinkingPlayer.playerId}</span>
                      <span className="thinking-player-model">({thinkingPlayer.model})</span>
                    </div>
                    <div className="thinking-progress">
                      is crafting a clue... ({thinkingPlayer.index} of {thinkingPlayer.total})
                    </div>
                    <div className="thinking-bar">
                      <div
                        className="thinking-bar-fill"
                        style={{ width: `${(thinkingPlayer.index / thinkingPlayer.total) * 100}%` }}
                      />
                    </div>
                  </div>
                ) : (
                  <>
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
                  </>
                )}
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
          {/* Voting section - grouped by voting round with eliminations */}
          {(allVotes.length > 0 || allEliminations.length > 0) && (() => {
            // Group votes by voting round, keeping track of original indices
            const votesByRound: { [round: number]: { vote: typeof allVotes[0]; originalIndex: number }[] } = {};
            allVotes.forEach((vote, index) => {
              if (!votesByRound[vote.voting_round]) {
                votesByRound[vote.voting_round] = [];
              }
              votesByRound[vote.voting_round].push({ vote, originalIndex: index });
            });

            // Get voting rounds sorted descending (newest first)
            const votingRounds = Object.keys(votesByRound).map(Number).sort((a, b) => b - a);

            return votingRounds.map(votingRound => {
              const elimination = allEliminations.find(e => e.voting_round === votingRound);

              return (
                <div key={`voting-round-${votingRound}`} className="timeline-round-block voting-block">
                  <div className="timeline-round-header current-round voting">
                    <span className="round-line" />
                    <span className="round-label">🗳️ Voting Round {votingRound}</span>
                    <span className="round-line" />
                  </div>

                  {/* Elimination reveal (if this round is complete) */}
                  {elimination && (
                    <div className={`timeline-item elimination ${elimination.was_imposter ? 'caught' : 'innocent'}`}>
                      <div className="timeline-marker">{elimination.was_imposter ? '🎭' : '❌'}</div>
                      <div className="timeline-content">
                        <div className="timeline-meta">
                          <span className="timeline-player">{elimination.eliminated_player}</span>
                          <span className={`elimination-badge ${elimination.was_imposter ? 'imposter' : 'innocent'}`}>
                            {elimination.was_imposter ? 'IMPOSTER!' : 'Innocent'}
                          </span>
                        </div>
                        <div className="timeline-clue">
                          Eliminated with {elimination.vote_counts[elimination.eliminated_player]} votes
                        </div>
                        {elimination.remaining_imposters > 0 && (
                          <div className="remaining-imposters">
                            {elimination.remaining_imposters} imposter{elimination.remaining_imposters !== 1 ? 's' : ''} remain
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Individual votes in this round - CLICKABLE */}
                  {votesByRound[votingRound].map(({ vote, originalIndex }) => {
                    const isSelected = selectedVoteIndex === originalIndex;
                    const isLatest = votingRound === currentVotingRound &&
                                     originalIndex === allVotes.length - 1 &&
                                     !isViewingHistory && !elimination;
                    return (
                      <div
                        key={`vote-${votingRound}-${originalIndex}`}
                        className={`timeline-item voting ${isLatest ? 'current' : ''} ${isSelected ? 'selected' : ''}`}
                        onClick={() => onSelectVote(originalIndex)}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => e.key === 'Enter' && onSelectVote(originalIndex)}
                      >
                        <div className="timeline-marker">{isSelected ? '👁' : '🗳️'}</div>
                        <div className="timeline-content">
                          <div className="timeline-meta">
                            <span className="timeline-player">{vote.player_id}</span>
                            <span className="timeline-round">→ {vote.vote}</span>
                          </div>
                          <div className="timeline-clue timeline-vote-reason">
                            {vote.reasoning}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              );
            });
          })()}

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

                {/* Clues within this round (chronological order) - CLICKABLE */}
                {cluesByRound[round].map(({ clue, originalIndex }) => {
                  const isImposter = clue.role === 'imposter';
                  const isSelected = selectedClueIndex === originalIndex;
                  const isLatest = originalIndex === allClues.length - 1 && !isViewingHistory;

                  return (
                    <div
                      key={originalIndex}
                      className={`timeline-item ${isImposter ? 'imposter' : 'normal'} ${isSelected ? 'selected' : ''} ${isLatest ? 'current' : ''}`}
                      onClick={() => onSelectClue(originalIndex)}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => e.key === 'Enter' && onSelectClue(originalIndex)}
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
                className={`player-chip ${(cluePlayer?.id === player.id || votePlayer?.id === player.id) ? 'active' : ''}`}
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
