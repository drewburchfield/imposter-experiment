/**
 * Custom hook for SSE game streaming with playback control.
 * Manages event queue, speed-controlled playback, and history navigation.
 *
 * Key feature: LLM calls run ahead of UI playback. Speed controls viewing time
 * between content events (clues/votes), independent of how fast LLM responds.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { API_BASE_URL } from '../config/api';
import type { GameEvent } from '../types/game';

interface UseGameStreamResult {
  events: GameEvent[];
  isPlaying: boolean;
  speed: number;
  setSpeed: (speed: number) => void;
  togglePlay: () => void;
  currentEventIndex: number;
  // History navigation
  selectedEventIndex: number | null;
  isViewingHistory: boolean;
  selectEvent: (index: number) => void;
  goToLive: () => void;
  stepPrev: () => void;
  stepNext: () => void;
  // Buffer status
  isBuffering: boolean;
}

// Check if event is a "content" event that should have speed-controlled pacing
function isContentEvent(event: GameEvent): boolean {
  return event.type === 'clue' || event.type === 'vote' || event.type === 'elimination';
}

export function useGameStream(gameId: string | null): UseGameStreamResult {
  const [eventQueue, setEventQueue] = useState<GameEvent[]>([]);
  const [displayedEvents, setDisplayedEvents] = useState<GameEvent[]>([]);
  const [isPlaying, setIsPlaying] = useState(true);
  const [speed, setSpeed] = useState(0.5);
  const [currentIndex, setCurrentIndex] = useState(0);

  // History navigation state
  const [selectedEventIndex, setSelectedEventIndex] = useState<number | null>(null);

  // Track when last content event was displayed (for pacing)
  const lastContentDisplayTimeRef = useRef<number>(0);

  const eventSourceRef = useRef<EventSource | null>(null);
  const playbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Derived state: are we viewing history vs live?
  const isViewingHistory = selectedEventIndex !== null;

  // Are we waiting for more events from the buffer?
  const isBuffering = isPlaying && currentIndex >= eventQueue.length && eventQueue.length > 0;

  // Connect to SSE stream
  useEffect(() => {
    if (!gameId) return;

    const eventSource = new EventSource(
      `${API_BASE_URL}/api/game/${gameId}/stream`
    );

    eventSource.onmessage = (event) => {
      const gameEvent: GameEvent = JSON.parse(event.data);
      setEventQueue(prev => [...prev, gameEvent]);
    };

    eventSource.onerror = () => {
      console.error('SSE connection error');
      eventSource.close();
    };

    eventSourceRef.current = eventSource;

    return () => {
      eventSource.close();
    };
  }, [gameId]);

  // Playback control - process queue at controlled speed
  // Key: content events are paced relative to LAST content event display time,
  // not relative to when they arrived. This lets LLM run ahead.
  useEffect(() => {
    if (!isPlaying || currentIndex >= eventQueue.length) {
      if (playbackTimerRef.current) {
        clearTimeout(playbackTimerRef.current);
      }
      return;
    }

    const nextEvent = eventQueue[currentIndex];
    const now = Date.now();

    // FIRST event displays immediately
    if (displayedEvents.length === 0) {
      if (isContentEvent(nextEvent)) {
        lastContentDisplayTimeRef.current = now;
      }
      setDisplayedEvents([nextEvent]);
      setCurrentIndex(1);
      return;
    }

    // Calculate delay based on event type
    let delay: number;

    if (nextEvent.type === 'clue') {
      // Clues: speed-adjusted viewing time, scheduled from last content event
      const baseDelay = 4000 / speed;
      const targetTime = lastContentDisplayTimeRef.current + baseDelay;
      delay = Math.max(0, targetTime - now);
    } else if (nextEvent.type === 'vote') {
      // Votes: speed-adjusted viewing time
      const baseDelay = 3500 / speed;
      const targetTime = lastContentDisplayTimeRef.current + baseDelay;
      delay = Math.max(0, targetTime - now);
    } else if (nextEvent.type === 'elimination') {
      // Eliminations: dramatic pause
      const baseDelay = 3000 / speed;
      const targetTime = lastContentDisplayTimeRef.current + baseDelay;
      delay = Math.max(0, targetTime - now);
    } else if (nextEvent.type === 'game_complete') {
      // Results: give users a moment to see the last content
      const baseDelay = 2000 / speed;
      const targetTime = lastContentDisplayTimeRef.current + baseDelay;
      delay = Math.max(0, targetTime - now);
    } else {
      // Transitions (round_start, round_end, voting_start, player_thinking):
      // Show immediately - these provide progress feedback
      delay = 50;
    }

    playbackTimerRef.current = setTimeout(() => {
      if (isContentEvent(nextEvent)) {
        lastContentDisplayTimeRef.current = Date.now();
      }
      setDisplayedEvents(prev => [...prev, nextEvent]);
      setCurrentIndex(prev => prev + 1);
    }, delay);

    return () => {
      if (playbackTimerRef.current) {
        clearTimeout(playbackTimerRef.current);
      }
    };
  }, [isPlaying, currentIndex, eventQueue, speed, displayedEvents.length]);

  const togglePlay = useCallback(() => {
    setIsPlaying(prev => !prev);
  }, []);

  // Select a specific event to view (auto-pauses)
  const selectEvent = useCallback((index: number) => {
    if (index >= 0 && index < displayedEvents.length) {
      setSelectedEventIndex(index);
      setIsPlaying(false); // Auto-pause when browsing history
    }
  }, [displayedEvents.length]);

  // Return to live mode (clears selection, optionally resumes)
  const goToLive = useCallback(() => {
    setSelectedEventIndex(null);
    setIsPlaying(true); // Resume playback
  }, []);

  // Step to previous event
  const stepPrev = useCallback(() => {
    const currentViewIndex = selectedEventIndex ?? displayedEvents.length - 1;
    if (currentViewIndex > 0) {
      setSelectedEventIndex(currentViewIndex - 1);
      setIsPlaying(false);
    }
  }, [selectedEventIndex, displayedEvents.length]);

  // Step to next event
  const stepNext = useCallback(() => {
    const currentViewIndex = selectedEventIndex ?? displayedEvents.length - 1;
    if (currentViewIndex < displayedEvents.length - 1) {
      setSelectedEventIndex(currentViewIndex + 1);
      setIsPlaying(false);
    } else {
      // At the end, go to live
      setSelectedEventIndex(null);
    }
  }, [selectedEventIndex, displayedEvents.length]);

  return {
    events: displayedEvents,
    isPlaying,
    speed,
    setSpeed,
    togglePlay,
    currentEventIndex: currentIndex,
    // History navigation
    selectedEventIndex,
    isViewingHistory,
    selectEvent,
    goToLive,
    stepPrev,
    stepNext,
    // Buffer status
    isBuffering
  };
}
