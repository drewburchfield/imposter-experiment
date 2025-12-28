/**
 * PlayerCircle - Displays all players in a circular layout.
 * Highlights current speaker and shows player states.
 */

import React from 'react';
import { Player } from '../types/game';
import './PlayerCircle.css';

interface PlayerCircleProps {
  players: Player[];
  currentSpeaker?: string;
  revealedRoles?: boolean;
}

export const PlayerCircle: React.FC<PlayerCircleProps> = ({
  players,
  currentSpeaker,
  revealedRoles = false
}) => {
  const radius = 250; // pixels
  const centerX = 300;
  const centerY = 300;

  return (
    <div className="player-circle-container">
      <svg width="600" height="600" className="player-circle-svg">
        {players.map((player, index) => {
          const angle = (index / players.length) * 2 * Math.PI - Math.PI / 2;
          const x = centerX + radius * Math.cos(angle);
          const y = centerY + radius * Math.sin(angle);

          const isCurrentSpeaker = player.id === currentSpeaker;
          const isImposter = revealedRoles && player.role === 'imposter';

          return (
            <g key={player.id} className={`player ${isCurrentSpeaker ? 'speaking' : ''}`}>
              <circle
                cx={x}
                cy={y}
                r="30"
                className={`player-avatar ${isImposter ? 'imposter' : 'non-imposter'} ${isCurrentSpeaker ? 'speaking' : ''}`}
              />
              <text
                x={x}
                y={y + 50}
                textAnchor="middle"
                className="player-label"
              >
                {player.id}
              </text>
              <text
                x={x}
                y={y + 65}
                textAnchor="middle"
                className="player-model"
              >
                ({player.model})
              </text>
              {isCurrentSpeaker && (
                <circle
                  cx={x}
                  cy={y}
                  r="35"
                  className="speaker-glow"
                />
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
};
