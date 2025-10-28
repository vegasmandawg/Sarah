'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { WebSocketMessage } from '@/types'

interface UseWebSocketOptions {
  url: string
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export function useWebSocket({
  url,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5,
}: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false)
  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const urlRef = useRef(url)
  const reconnectAttemptsRef = useRef(0)
  const onMessageRef = useRef(onMessage)
  const shouldReconnectRef = useRef(true)

  useEffect(() => {
    onMessageRef.current = onMessage
  }, [onMessage])

  // Update url ref when it changes
  useEffect(() => {
    urlRef.current = url
  }, [url])

  useEffect(() => {
    shouldReconnectRef.current = true

    return () => {
      shouldReconnectRef.current = false
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
    }
  }, [])

  const connect = useCallback(() => {
    if (typeof window === 'undefined') {
      return
    }

    if (
      wsRef.current &&
      (wsRef.current.readyState === WebSocket.OPEN ||
        wsRef.current.readyState === WebSocket.CONNECTING)
    ) {
      return
    }

    try {
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8080'
      shouldReconnectRef.current = true
      const ws = new WebSocket(`${wsUrl}${urlRef.current}`)

      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        reconnectAttemptsRef.current = 0
        setReconnectAttempts(0)
        onConnect?.()
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WebSocketMessage
          onMessageRef.current?.(data)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        onError?.(error)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        onDisconnect?.()

        // Attempt to reconnect
        if (
          shouldReconnectRef.current &&
          reconnectAttemptsRef.current < maxReconnectAttempts
        ) {
          reconnectTimeoutRef.current = setTimeout(() => {
            const nextAttempt = reconnectAttemptsRef.current + 1
            reconnectAttemptsRef.current = nextAttempt
            setReconnectAttempts(nextAttempt)
            console.log(`Reconnecting... (attempt ${nextAttempt})`)
            connect()
          }, reconnectInterval)
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
    }
  }, [onConnect, onDisconnect, onError, reconnectInterval, maxReconnectAttempts])

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setIsConnected(false)
    reconnectAttemptsRef.current = 0
    setReconnectAttempts(0)
  }, [])

  const sendMessage = useCallback((data: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    } else {
      console.error('WebSocket is not connected')
    }
  }, [])

  // Connect on mount
  useEffect(() => {
    connect()

    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected,
    sendMessage,
    disconnect,
    reconnect: connect,
  }
}
