'use client'

import { useState, useRef, KeyboardEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Send, Paperclip, Mic, Image as ImageIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface MessageInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

export function MessageInput({ onSend, disabled, placeholder }: MessageInputProps) {
  const [message, setMessage] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message)
      setMessage('')
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value)
    
    // Auto-resize textarea
    const textarea = e.target
    textarea.style.height = 'auto'
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
  }

  return (
    <div className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-dark-200 p-4">
      <div className="flex items-end gap-2">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder={placeholder || 'Type a message...'}
            disabled={disabled}
            rows={1}
            className={cn(
              'w-full resize-none rounded-lg border border-gray-300 dark:border-gray-700',
              'bg-white dark:bg-dark-100 px-4 py-3 pr-12',
              'focus:outline-none focus:ring-2 focus:ring-primary-500',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'scrollbar-thin'
            )}
          />
          
          <Button
            onClick={handleSend}
            disabled={!message.trim() || disabled}
            size="icon"
            className="absolute right-2 bottom-2 h-8 w-8"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>

        <div className="flex gap-2">
          <Button
            variant="outline"
            size="icon"
            className="h-11 w-11"
            onClick={() => {
              // TODO: Implement image upload
              console.log('Image upload')
            }}
          >
            <ImageIcon className="w-5 h-5" />
          </Button>

          <Button
            variant="outline"
            size="icon"
            className={cn(
              'h-11 w-11',
              isRecording && 'bg-red-100 text-red-600 border-red-300'
            )}
            onClick={() => {
              // TODO: Implement voice recording
              setIsRecording(!isRecording)
              console.log('Voice recording')
            }}
          >
            <Mic className="w-5 h-5" />
          </Button>

          <Button
            variant="outline"
            size="icon"
            className="h-11 w-11"
            onClick={() => {
              // TODO: Implement file attachment
              console.log('File attachment')
            }}
          >
            <Paperclip className="w-5 h-5" />
          </Button>
        </div>
      </div>

      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  )
}
