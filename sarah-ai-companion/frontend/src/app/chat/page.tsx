'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useCharacterStore } from '@/store/character-store'
import { ChatInterface } from '@/components/chat/chat-interface'
import { Button } from '@/components/ui/button'
import { ArrowLeft, Settings } from 'lucide-react'

export default function ChatPage() {
  const router = useRouter()
  const { selectedCharacter } = useCharacterStore()
  const [showSettings, setShowSettings] = useState(false)

  useEffect(() => {
    if (!selectedCharacter) {
      router.push('/')
    }
  }, [selectedCharacter, router])

  if (!selectedCharacter) {
    return null
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-dark-100">
      {/* Sidebar */}
      <div className="w-80 bg-white dark:bg-dark-200 border-r border-gray-200 dark:border-gray-800 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between mb-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.push('/')}
              className="hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowSettings(!showSettings)}
              className="hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <Settings className="w-5 h-5" />
            </Button>
          </div>

          <div className="text-center">
            <div className="w-20 h-20 mx-auto bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center mb-3">
              <span className="text-2xl font-bold text-white">
                {selectedCharacter.name[0].toUpperCase()}
              </span>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              {selectedCharacter.name}
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
              Online and ready to chat
            </p>
          </div>
        </div>

        {/* Character Info */}
        <div className="flex-1 p-4 overflow-y-auto">
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                About
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {selectedCharacter.persona_prompt}
              </p>
            </div>

            {showSettings && (
              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                  Settings
                </h3>
                <div className="space-y-2">
                  <label className="flex items-center gap-2 text-sm">
                    <input type="checkbox" className="rounded" defaultChecked />
                    <span>Enable voice responses</span>
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <input type="checkbox" className="rounded" defaultChecked />
                    <span>Show sentiment analysis</span>
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <input type="checkbox" className="rounded" />
                    <span>Auto-generate images</span>
                  </label>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        <ChatInterface character={selectedCharacter} />
      </div>
    </div>
  )
}
