import { useCallback, useEffect, useRef, useState } from "react";
import { AuctionWsEvent } from "../types";

export const useAuctionWs = (onEvent?: (event: AuctionWsEvent) => void) => {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isDestroyedRef = useRef<boolean>(false);

  const getWsUrl = useCallback((): string => {
    if (import.meta.env.VITE_WS_URL) {
      return import.meta.env.VITE_WS_URL as string;
    }
    const apiUrl = import.meta.env.VITE_API_URL as string | undefined;
    if (apiUrl) {
      const wsBase = apiUrl.replace(/^http(s?):/, "ws$1:");
      return `${wsBase.replace(/\/$/, "")}/ws/auction`;
    }
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.hostname || "localhost";
    return `${protocol}//${host}:8000/api/v1/ws/auction`;
  }, []);

  const connect = useCallback(() => {
    if (isDestroyedRef.current) {
      return;
    }

    try {
      const url = getWsUrl();
      const socket = new WebSocket(url);
      wsRef.current = socket;

      socket.onopen = () => {
        if (!isDestroyedRef.current) {
          setIsConnected(true);
        }
      };

      socket.onmessage = (messageEvent) => {
        try {
          const parsed = JSON.parse(messageEvent.data) as AuctionWsEvent;
          if (parsed && parsed.event && onEventRef.current) {
            onEventRef.current(parsed);
          }
        } catch {
          return;
        }
      };

      socket.onclose = () => {
        if (!isDestroyedRef.current) {
          setIsConnected(false);
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 2000);
        }
      };

      socket.onerror = () => {
        socket.close();
      };
    } catch {
      if (!isDestroyedRef.current) {
        setIsConnected(false);
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 2000);
      }
    }
  }, [getWsUrl]);

  useEffect(() => {
    isDestroyedRef.current = false;
    connect();

    return () => {
      isDestroyedRef.current = true;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { isConnected };
};
