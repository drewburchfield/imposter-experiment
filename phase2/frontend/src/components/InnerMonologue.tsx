/**
 * InnerMonologue - Displays AI player's inner thoughts in real-time.
 * Shows strategic reasoning, suspicions, and confidence levels.
 */

import React, { useEffect, useRef } from 'react';
import './InnerMonologue.css';

interface Thought {
  playerId: string;
  thinking: string;
  type: 'clue' | 'vote';
  confidence: number;
  timestamp: number;
}

interface InnerMonologueProps {
  thoughts: Thought[];
  currentPlayer?: string;
}

export const InnerMonologue: React.FC<InnerMonologueProps> = ({
  thoughts,
  currentPlayer
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest thought
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [thoughts]);

  const visibleThoughts = currentPlayer
    ? thoughts.filter(t => t.playerId === currentPlayer)
    : thoughts.slice(-10); // Last 10 thoughts if no filter

  return (
    <div className="inner-monologue">
      <div className="monologue-header">
        <h3>💭 Inner Thoughts</h3>
        {currentPlayer && <span className="filter-indicator">Showing: {currentPlayer}</span>}
      </div>
      <div className="monologue-content" ref={containerRef}>
        {visibleThoughts.length === 0 ? (
          <div className="empty-state">
            <p>Select a player or wait for game to start...</p>
          </div>
        ) : (
          visibleThoughts.map((thought, index) => (
            <div
              key={index}
              className={`thought-card ${thought.type}`}
            >
              <div className="thought-header">
                <span className="player-id">{thought.playerId}</span>
                <span className={`confidence confidence-${Math.floor(thought.confidence / 25)}`}>
                  {thought.confidence}% confident
                </span>
              </div>
              <div className="thought-content">
                {thought.thinking}
              </div>
              <div className="thought-timestamp">
                {new Date(thought.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
