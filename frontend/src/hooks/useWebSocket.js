/**
 * Custom React hook for WebSocket connections and real-time updates
 */
import { useEffect, useRef } from 'react';

// Global WebSocket instance - shared across all components
let globalWs = null;
let listeners = [];

function addListener(callback) {
  listeners.push(callback);
  return () => {
    listeners = listeners.filter(l => l !== callback);
  };
}

function notifyListeners(message) {
  listeners.forEach(callback => callback(message));
}

function connectGlobalWebSocket() {
  if (globalWs && (globalWs.readyState === WebSocket.OPEN || globalWs.readyState === WebSocket.CONNECTING)) {
    return; // Already connected or connecting
  }

  // Connect to backend API WebSocket endpoint (not through proxy)
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const backendHost = process.env.REACT_APP_API_URL ? 
    new URL(process.env.REACT_APP_API_URL).host : 
    'localhost:8000';
  const wsUrl = `${protocol}://${backendHost}/ws`;
  
  console.log(`🔌 Attempting WebSocket connection to: ${wsUrl}`);
  
  try {
    globalWs = new WebSocket(wsUrl);
    
    globalWs.onopen = () => {
      console.log('✅ WebSocket connected');
    };

    globalWs.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log('📨 WebSocket message received:', message);
        notifyListeners(message);
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    globalWs.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
    };

    globalWs.onclose = () => {
      console.log('⚠️ WebSocket disconnected, attempting to reconnect...');
      globalWs = null;
      // Attempt to reconnect after 3 seconds
      setTimeout(connectGlobalWebSocket, 3000);
    };
  } catch (e) {
    console.error('Failed to connect WebSocket:', e);
  }
}

export function useWebSocket(onMessage) {
  const callbackRef = useRef(onMessage);

  useEffect(() => {
    callbackRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    // Connect to WebSocket on first mount
    connectGlobalWebSocket();

    // Subscribe to messages
    const unsubscribe = addListener((message) => {
      if (callbackRef.current) {
        callbackRef.current(message);
      }
    });

    // Don't close the WebSocket on unmount - keep it alive for other components
    return unsubscribe;
  }, []);

  return globalWs;
}
