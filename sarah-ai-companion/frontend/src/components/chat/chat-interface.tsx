'use client'

import { useState, useEffect, useRef } from 'react'
import { Character, Message, WebSocketMessage } from '@/types'
import { MessageList } from './message-list'
import { MessageInput } from './message-input'
import { useWebSocket } from '@/hooks/use-websocket'
import { generateMessageId } from '@/lib/utils'
import toast from 'react-hot-toast'

interface ChatInterfaceProps {
  character: Character
}

export function ChatInterface({ character }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const [currentResponse, setCurrentResponse] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { sendMessage, isConnected } = useWebSocket({
    url: '/ws/chat',
    onMessage: handleWebSocketMessage,
    onConnect: () => {
      console.log('WebSocket connected')
      toast.success('Connected to chat')
    },
    onDisconnect: () => {
      console.log('WebSocket disconnected')
      toast.error('Disconnected from chat')
    },
  })

  function handleWebSocketMessage(message: WebSocketMessage) {
    switch (message.type) {
      case 'status':
        if (message.task === 'processing_message') {
          setIsTyping(true)
        } else if (message.task === 'generating_response') {
          setCurrentResponse('')
        }
        break

      case 'token':
        setIsTyping(false)
        setCurrentResponse((prev) => prev + message.content)
        break

      case 'complete':
        if (currentResponse) {
          const assistantMessage: Message = {
            id: generateMessageId(),
            role: 'assistant',
            content: currentResponse,
            timestamp: new Date().toISOString(),
            metadata: {
              sentiment: message.sentiment,
            },
          }
          setMessages((prev) => [...prev, assistantMessage])
          setCurrentResponse('')
        }
        break

      case 'error':
        toast.error(message.content || 'An error occurred')
        setIsTyping(false)
        setCurrentResponse('')
        break
    }
  }

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || !isConnected) return

    // Add user message
    const userMessage: Message = {
      id: generateMessageId(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
      metadata: {
        status: 'sending',
      },
    }

    setMessages((prev) => [...prev, userMessage])

    // Send via WebSocket
    sendMessage({
      message: content,
      character_id: character.character_id,
      user_id: 'user123', // TODO: Get from auth
    })

    // Update message status
    setTimeout(() => {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === userMessage.id
            ? { ...msg, metadata: { ...msg.metadata, status: 'sent' } }
            : msg
        )
      )
    }, 100)
  }

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, currentResponse])

  return (
    <>
      <MessageList
        messages={messages}
        isTyping={isTyping}
        currentResponse={currentResponse}
        character={character}
      />
      <div ref={messagesEndRef} />
      <MessageInput
        onSend={handleSendMessage}
        disabled={!isConnected || isTyping}
        placeholder={
          !isConnected
            ? 'Connecting...'
            : isTyping
            ? `${character.name} is typing...`
            : `Message ${character.name}...`
        }
      />
    </>
  )
}
