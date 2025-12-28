/**
 * GameControls - Playback controls for game observation.
 * Play/pause, speed adjustment, and game info display.
 */

import React from 'react';
import './GameControls.css';

interface GameControlsProps {
  isPlaying: boolean;
  speed: number;
  currentRound: number;
  totalRounds: number;
  onTogglePlay: () => void;
  onSpeedChange: (speed: number) => void;
}

export const GameControls: React.FC<GameControlsProps> = ({
  isPlaying,
  speed,
  currentRound,
  totalRounds,
  onTogglePlay,
  onSpeedChange
}) => {
  const speedOptions = [0.25, 0.5, 1, 2, 4];

  return (
    <div className="game-controls">
      <div className="control-section">
        <button
          className="play-pause-btn"
          onClick={onTogglePlay}
        >
          {isPlaying ? '⏸ Pause' : '▶ Play'}
        </button>

        <div className="round-indicator">
          Round {currentRound} / {totalRounds}
        </div>
      </div>

      <div className="control-section">
        <label>Speed:</label>
        <div className="speed-buttons">
          {speedOptions.map(s => (
            <button
              key={s}
              className={`speed-btn ${speed === s ? 'active' : ''}`}
              onClick={() => onSpeedChange(s)}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
