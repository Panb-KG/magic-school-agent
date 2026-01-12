import { useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import type { WebSocketMessage } from '@/types';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8765';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  channels?: string[];
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: Error) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const {
    autoConnect = true,
    channels = [],
    onMessage,
    onError,
    onConnect,
    onDisconnect,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<Socket | null>(null);

  // 连接 WebSocket
  const connect = useCallback(() => {
    if (socketRef.current?.connected) {
      return;
    }

    const socket = io(WS_URL, {
      transports: ['websocket'],
      autoConnect: false,
    });

    socket.on('connect', () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      onConnect?.();

      // 订阅频道
      if (channels.length > 0) {
        socket.emit('subscribe', { channels });
      }
    });

    socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      onDisconnect?.();
    });

    socket.on('message', (data: WebSocketMessage) => {
      console.log('WebSocket message received:', data);
      onMessage?.(data);
    });

    socket.on('error', (error: Error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
      onError?.(error);
    });

    socketRef.current = socket;
    socket.connect();
  }, [channels, onMessage, onError, onConnect, onDisconnect]);

  // 断开连接
  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
      setIsConnected(false);
    }
  }, []);

  // 订阅频道
  const subscribe = useCallback((newChannels: string[]) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('subscribe', { channels: newChannels });
    }
  }, []);

  // 取消订阅频道
  const unsubscribe = useCallback((channelsToUnsubscribe: string[]) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('unsubscribe', { channels: channelsToUnsubscribe });
    }
  }, []);

  // 发送消息
  const send = useCallback((event: string, data: any) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit(event, data);
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  // 自动连接
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    isConnected,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    send,
    socket: socketRef.current,
  };
};
