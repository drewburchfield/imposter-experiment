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

// Legacy batch voting (deprecated)
export interface LegacyVoteEvent {
  type: 'vote';
  player_id: string;
  votes: string[];
  thinking: string;
  reasoning: Record<string, string>;
  confidence: number;
}

// New sequential voting - one player at a time
export interface VoteEvent {
  type: 'vote';
  voting_round: number;
  player_id: string;
  vote: string;  // Single player they're voting for
  thinking: string;
  reasoning: string;
  confidence: number;
  votes_so_far: Record<string, number>;  // Running tally
  total_votes_cast: number;  // How many players have voted so far
  total_active_players: number;  // Total players who will vote
}

export interface VotingRoundStartEvent {
  type: 'voting_round_start';
  voting_round: number;
  total_voting_rounds: number;
  eliminated_so_far: string[];
}

export interface EliminationEvent {
  type: 'elimination';
  voting_round: number;
  eliminated_player: string;
  was_imposter: boolean;
  vote_counts: Record<string, number>;
  remaining_imposters: number;
}

export interface ValidationErrorEvent {
  type: 'validation_error';
  player_id: string;
  clue: string;
  reason: string;
  message: string;
}

export interface InstantRevealEvent {
  type: 'instant_reveal';
  player_id: string;
  role: string;
  reason: string;
}

export interface GameResult {
  word: string;
  category: string;
  actual_imposters: string[];
  eliminated_players: string[];
  detection_accuracy: number;
  total_rounds: number;
}

export interface PlayerThinkingEvent {
  type: 'player_thinking';
  player_id: string;
  player_model: string;
  action: 'clue' | 'vote';
  player_index: number;
  total_players: number;
  voting_round?: number;
}

export type GameEvent =
  | { type: 'game_start'; players: Player[] }
  | { type: 'round_start'; round: number; total_rounds: number }
  | PlayerThinkingEvent
  | ClueEvent
  | { type: 'round_end'; round: number }
  | { type: 'voting_start' }
  | VotingRoundStartEvent
  | VoteEvent
  | EliminationEvent
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
