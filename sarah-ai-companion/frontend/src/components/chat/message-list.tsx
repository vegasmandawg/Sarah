'use client'

import { Message, Character } from '@/types'
import { cn, formatDate, getSentimentColor, getSentimentEmoji } from '@/lib/utils'
import { User } from 'lucide-react'

interface MessageListProps {
  messages: Message[]
  isTyping: boolean
  currentResponse: string
  character: Character
  showSentiment: boolean
}

export function MessageList({
  messages,
  isTyping,
  currentResponse,
  character,
  showSentiment,
}: MessageListProps) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
      {messages.length === 0 && !isTyping && !currentResponse && (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">
            Start a conversation with {character.name}
          </p>
        </div>
      )}

      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
          character={character}
          showSentiment={showSentiment}
        />
      ))}

      {currentResponse && (
        <MessageBubble
          message={{
            id: 'current',
            role: 'assistant',
            content: currentResponse,
            timestamp: new Date().toISOString(),
          }}
          character={character}
          isStreaming
          showSentiment={showSentiment}
        />
      )}

      {isTyping && !currentResponse && (
        <div className="flex gap-3">
          <Avatar character={character} />
          <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl px-4 py-3">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

interface MessageBubbleProps {
  message: Message
  character: Character
  isStreaming?: boolean
  showSentiment: boolean
}

function MessageBubble({ message, character, isStreaming, showSentiment }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div
      className={cn(
        'flex gap-3 message-appear',
        isUser && 'flex-row-reverse'
      )}
    >
      {isUser ? <UserAvatar /> : <Avatar character={character} />}

      <div
        className={cn(
          'max-w-[70%] rounded-2xl px-4 py-3',
          isUser
            ? 'bg-primary-600 text-white'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
        )}
      >
        {message.metadata?.quickActionLabel && (
          <div
            className={cn(
              'mb-2 text-[10px] font-semibold uppercase tracking-wide',
              isUser ? 'text-primary-100' : 'text-primary-500'
            )}
          >
            {message.metadata.quickActionLabel}
          </div>
        )}

        <p className="whitespace-pre-wrap">{message.content}</p>

        {!isStreaming && (
          <div
            className={cn(
              'mt-2 text-xs flex items-center gap-2',
              isUser ? 'text-primary-100' : 'text-gray-500 dark:text-gray-400'
            )}
          >
            <span>{formatDate(message.timestamp)}</span>

            {showSentiment && message.metadata?.sentiment && (
              <span className={cn('flex items-center gap-1', getSentimentColor(message.metadata.sentiment.compound))}>
                {getSentimentEmoji(message.metadata.sentiment.compound)}
                <span className="font-medium">
                  {(message.metadata.sentiment.compound * 100).toFixed(0)}%
                </span>
              </span>
            )}
          </div>
        )}
        
        {isStreaming && (
          <span className="inline-block w-1 h-4 bg-current animate-typing ml-1" />
        )}
      </div>
    </div>
  )
}

function Avatar({ character }: { character: Character }) {
  return (
    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-secondary-400 flex items-center justify-center flex-shrink-0">
      <span className="text-white font-medium">
        {character.name[0].toUpperCase()}
      </span>
    </div>
  )
}

function UserAvatar() {
  return (
    <div className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center flex-shrink-0">
      <User className="w-5 h-5 text-gray-600 dark:text-gray-300" />
    </div>
  )
}
