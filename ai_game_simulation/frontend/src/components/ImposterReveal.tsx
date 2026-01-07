/**
 * ImposterReveal - Dramatic post-game imposter revelation
 * Tech Noir aesthetic with neon accents and cinematic animations
 */

import React from 'react';
import './ImposterReveal.css';

interface ImposterRevealProps {
  imposters: string[];
  eliminated: string[];
  players: Array<{ id: string; model: string }>;
  detectionAccuracy: number;
  word: string;
}

export const ImposterReveal: React.FC<ImposterRevealProps> = ({
  imposters,
  eliminated,
  players,
  detectionAccuracy,
  word
}) => {
  return (
    <div className="imposter-reveal-overlay">
      {/* Dramatic title */}
      <div className="reveal-header">
        <h1 className="reveal-title">
          <span className="title-line">THE IMPOSTERS</span>
          <span className="title-line delay-1">WERE...</span>
        </h1>
        <div className="word-reveal delay-2">
          The word was: <span className="secret-word">{word}</span>
        </div>
      </div>

      {/* Imposter cards */}
      <div className="imposter-cards">
        {imposters.map((imposterId, index) => {
          const player = players.find(p => p.id === imposterId);
          const wasCaught = eliminated.includes(imposterId);

          return (
            <div
              key={imposterId}
              className={`imposter-card ${wasCaught ? 'caught' : 'escaped'}`}
              style={{ animationDelay: `${0.8 + index * 0.3}s` }}
            >
              {/* Neon border glow */}
              <div className="card-glow"></div>

              {/* Card content */}
              <div className="card-inner">
                {/* Mask icon */}
                <div className="mask-container">
                  <div className="mask-icon">🎭</div>
                  <div className="mask-glow"></div>
                </div>

                {/* Player info */}
                <div className="player-info">
                  <div className="player-name">{imposterId}</div>
                  <div className="player-model">{player?.model || 'Unknown'}</div>
                </div>

                {/* Status badge */}
                <div className={`status-badge ${wasCaught ? 'caught' : 'escaped'}`}>
                  {wasCaught ? (
                    <>
                      <span className="status-icon">✓</span>
                      <span className="status-text">CAUGHT</span>
                    </>
                  ) : (
                    <>
                      <span className="status-icon">→</span>
                      <span className="status-text">ESCAPED</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Detection score */}
      <div className="detection-score delay-3">
        <div className="score-label">Detection Rate</div>
        <div className="score-value">
          {(detectionAccuracy * 100).toFixed(0)}%
        </div>
        <div className="score-bar">
          <div
            className="score-fill"
            style={{ width: `${detectionAccuracy * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
};
