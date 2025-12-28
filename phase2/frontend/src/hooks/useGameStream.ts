/**
 * Custom hook for SSE game streaming with playback control.
 * Manages event queue and speed-controlled playback.
 */

import { useState, useEffect, useRef } from 'react';
import type { GameEvent } from '../types/game';

interface UseGameStreamResult {
  events: GameEvent[];
  isPlaying: boolean;
  speed: number;
  setSpeed: (speed: number) => void;
  togglePlay: () => void;
  currentEventIndex: number;
}

export function useGameStream(gameId: string | null): UseGameStreamResult {
  const [eventQueue, setEventQueue] = useState<GameEvent[]>([]);
  const [displayedEvents, setDisplayedEvents] = useState<GameEvent[]>([]);
  const [isPlaying, setIsPlaying] = useState(true);
  const [speed, setSpeed] = useState(1.0);
  const [currentIndex, setCurrentIndex] = useState(0);

  const eventSourceRef = useRef<EventSource | null>(null);
  const playbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Connect to SSE stream
  useEffect(() => {
    if (!gameId) return;

    const eventSource = new EventSource(
      `http://localhost:9000/api/game/${gameId}/stream`
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
  useEffect(() => {
    if (!isPlaying || currentIndex >= eventQueue.length) {
      if (playbackTimerRef.current) {
        clearTimeout(playbackTimerRef.current);
      }
      return;
    }

    // Calculate delay based on event type and speed
    const nextEvent = eventQueue[currentIndex];
    let baseDelay = 1000; // 1 second default

    if (nextEvent.type === 'clue') {
      baseDelay = 4000; // 4 seconds for clues
    } else if (nextEvent.type === 'vote') {
      baseDelay = 3000; // 3 seconds for votes
    } else if (nextEvent.type === 'round_start') {
      baseDelay = 2000; // 2 seconds for transitions
    }

    const adjustedDelay = baseDelay / speed;

    playbackTimerRef.current = setTimeout(() => {
      setDisplayedEvents(prev => [...prev, nextEvent]);
      setCurrentIndex(prev => prev + 1);
    }, adjustedDelay);

    return () => {
      if (playbackTimerRef.current) {
        clearTimeout(playbackTimerRef.current);
      }
    };
  }, [isPlaying, currentIndex, eventQueue, speed]);

  const togglePlay = () => {
    setIsPlaying(prev => !prev);
  };

  return {
    events: displayedEvents,
    isPlaying,
    speed,
    setSpeed,
    togglePlay,
    currentEventIndex: currentIndex
  };
}
