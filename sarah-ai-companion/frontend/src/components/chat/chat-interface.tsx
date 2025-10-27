'use client'

import { useState, useEffect, useRef } from 'react'
import type { ReactNode } from 'react'
import { Character, Message, WebSocketMessage } from '@/types'
import { MessageList } from './message-list'
import { MessageInput } from './message-input'
import { QuickActions } from './quick-actions'
import { useWebSocket } from '@/hooks/use-websocket'
import {
  cn,
  describeExplicitLevel,
  describeIntensity,
  generateMessageId,
  toTitleCase,
} from '@/lib/utils'
import {
  selectChatPreferences,
  useChatSettingsStore,
} from '@/store/chat-settings-store'
import toast from 'react-hot-toast'
import { Flame, Shield, Sparkles } from 'lucide-react'

interface ChatInterfaceProps {
  character: Character
}

export function ChatInterface({ character }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const [currentResponse, setCurrentResponse] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const preferences = useChatSettingsStore(selectChatPreferences)
  const mood = useChatSettingsStore((state) => state.mood)
  const intensity = useChatSettingsStore((state) => state.intensity)
  const explicitLevel = useChatSettingsStore((state) => state.explicitLevel)
  const safeWord = useChatSettingsStore((state) => state.safeWord)
  const roleplayMode = useChatSettingsStore((state) => state.roleplayMode)
  const allowNarration = useChatSettingsStore((state) => state.allowNarration)
  const showSentiment = useChatSettingsStore((state) => state.showSentiment)
  const greenLights = useChatSettingsStore((state) => state.greenLights)
  const hardLimits = useChatSettingsStore((state) => state.hardLimits)

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

  const handleSendMessage = async (
    content: string,
    metadata: Partial<Message['metadata']> = {}
  ) => {
    if (!content.trim() || !isConnected) return

    const preferenceSnapshot = { ...preferences }

    const userMessage: Message = {
      id: generateMessageId(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
      metadata: {
        status: 'sending',
        preferences: preferenceSnapshot,
        ...metadata,
      },
    }

    setMessages((prev) => [...prev, userMessage])

    try {
      sendMessage({
        message: content,
        character_id: character.character_id,
        user_id: 'user123', // TODO: Get from auth
        preferences: preferenceSnapshot,
      })

      setTimeout(() => {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === userMessage.id
              ? { ...msg, metadata: { ...msg.metadata, status: 'sent' } }
              : msg
          )
        )
      }, 100)
    } catch (error) {
      console.error('Failed to send message:', error)
      toast.error('Failed to send message')

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === userMessage.id
            ? { ...msg, metadata: { ...msg.metadata, status: 'error' } }
            : msg
        )
      )
    }
  }

  const handleQuickAction = (action: { label: string; prompt: string }) => {
    handleSendMessage(action.prompt, {
      quickAction: true,
      quickActionLabel: action.label,
    })
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, currentResponse])

  const placeholder = !isConnected
    ? 'Connecting...'
    : isTyping
    ? `${character.name} is catching their breath...`
    : `Invite ${character.name} into a ${toTitleCase(mood)} moment...`

  const topGreenLights = greenLights.slice(0, 2).join(' • ')
  const topLimits = hardLimits.slice(0, 2).join(' • ')

  return (
    <div className="flex h-full flex-col bg-white/70 dark:bg-dark-200/60">
      <div className="border-b border-gray-200 bg-white px-6 py-4 dark:border-gray-800 dark:bg-dark-200">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
            <span
              className={cn(
                'h-2.5 w-2.5 rounded-full',
                isConnected ? 'bg-emerald-500' : 'bg-amber-400 animate-pulse'
              )}
            />
            {isConnected ? 'Connected' : 'Reconnecting'} to {character.name}
          </div>

          <div className="flex flex-wrap items-center gap-2 text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
            <PreferenceChip
              icon={<Sparkles className="h-3.5 w-3.5 text-primary-500" />}
              label="Mood"
              value={toTitleCase(mood)}
            />
            <PreferenceChip
              icon={<Flame className="h-3.5 w-3.5 text-secondary-500" />}
              label={describeIntensity(intensity)}
              value={`${intensity}% heat`}
            />
            <PreferenceChip
              icon={<Sparkles className="h-3.5 w-3.5 text-rose-500" />}
              label="Explicit"
              value={describeExplicitLevel(explicitLevel)}
            />
          </div>
        </div>

        <div className="mt-2 flex flex-wrap items-center gap-x-6 gap-y-1 text-[11px] text-gray-500 dark:text-gray-400">
          {roleplayMode && (
            <span className="flex items-center gap-1">
              <Sparkles className="h-3 w-3 text-primary-400" /> Immersive roleplay on
            </span>
          )}
          {allowNarration && (
            <span className="flex items-center gap-1">
              <Sparkles className="h-3 w-3 text-secondary-400" /> Sensory narration encouraged
            </span>
          )}
          {safeWord && (
            <span className="flex items-center gap-1 font-semibold text-secondary-600 dark:text-secondary-300">
              <Shield className="h-3 w-3" /> Safe word: {safeWord}
            </span>
          )}
        </div>

        <div className="mt-2 grid gap-2 text-[11px] text-gray-500 dark:text-gray-400 md:grid-cols-2">
          {greenLights.length > 0 && (
            <span>
              <span className="font-semibold text-primary-500">Turn-ons:</span> {topGreenLights}
              {greenLights.length > 2 && ' +' + (greenLights.length - 2)}
            </span>
          )}
          {hardLimits.length > 0 && (
            <span>
              <span className="font-semibold text-red-500">Limits:</span> {topLimits}
              {hardLimits.length > 2 && ' +' + (hardLimits.length - 2)}
            </span>
          )}
        </div>
      </div>

      <QuickActions onSelect={handleQuickAction} disabled={!isConnected || isTyping} />

      <div className="flex-1 overflow-hidden">
        <MessageList
          messages={messages}
          isTyping={isTyping}
          currentResponse={currentResponse}
          character={character}
          showSentiment={showSentiment}
        />
        <div ref={messagesEndRef} />
      </div>

      <MessageInput
        onSend={handleSendMessage}
        disabled={!isConnected || isTyping}
        placeholder={placeholder}
      />
    </div>
  )
}

function PreferenceChip({
  icon,
  label,
  value,
}: {
  icon: ReactNode
  label: string
  value: string
}) {
  return (
    <span className="flex items-center gap-1 rounded-full bg-gray-100 px-2 py-1 text-[11px] font-medium text-gray-700 dark:bg-gray-800 dark:text-gray-300">
      {icon}
      {label}
      <span className="text-gray-500">•</span>
      <span className="text-gray-900 dark:text-gray-100">{value}</span>
    </span>
  )
}
