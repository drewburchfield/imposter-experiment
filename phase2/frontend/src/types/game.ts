/**
 * TypeScript types for the imposter game.
 * Matches backend Pydantic models.
 */

export type PlayerRole = 'imposter' | 'non_imposter';

export interface Player {
  id: string;
  model: string;
  role?: PlayerRole; // Unknown until reveal
}

export interface ClueEvent {
  type: 'clue';
  round: number;
  player_id: string;
  player_model: string;
  role: string;
  clue: string;
  thinking: string;
  confidence: number;
  word_hypothesis?: string;
}

export interface VoteEvent {
  type: 'vote';
  player_id: string;
  votes: string[];
  thinking: string;
  reasoning: Record<string, string>;
  confidence: number;
}

export interface GameResult {
  word: string;
  category: string;
  actual_imposters: string[];
  eliminated_players: string[];
  detection_accuracy: number;
  total_rounds: number;
}

export type GameEvent =
  | { type: 'game_start'; players: Player[] }
  | { type: 'round_start'; round: number; total_rounds: number }
  | ClueEvent
  | { type: 'round_end'; round: number }
  | { type: 'voting_start' }
  | VoteEvent
  | { type: 'game_complete'; result: GameResult }
  | { type: 'error'; message: string };

export interface GameConfig {
  word: string;
  category: string;
  num_players: number;
  num_imposters: number;
  num_rounds: number;
  model_strategy?: string;
  model_distribution?: Record<string, number>;
}
