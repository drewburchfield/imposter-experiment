/**
 * ClueDisplay - Shows clues given by players with metadata.
 */

import React from 'react';
import { ClueEvent } from '../types/game';
import './ClueDisplay.css';

interface ClueDisplayProps {
  clues: ClueEvent[];
}

export const ClueDisplay: React.FC<ClueDisplayProps> = ({ clues }) => {
  return (
    <div className="clue-display">
      <h3>🗣️ Clues Given</h3>
      <div className="clue-list">
        {clues.map((clue, index) => (
          <div key={index} className={`clue-item ${clue.role}`}>
            <div className="clue-header">
              <span className="clue-player">{clue.player_id}</span>
              <span className="clue-round">Round {clue.round}</span>
            </div>
            <div className="clue-text">"{clue.clue}"</div>
            {clue.word_hypothesis && (
              <div className="word-guess">
                Guessing: {clue.word_hypothesis}
              </div>
            )}
            <details className="clue-thinking">
              <summary>View thinking</summary>
              <p>{clue.thinking}</p>
            </details>
          </div>
        ))}
      </div>
    </div>
  );
};
