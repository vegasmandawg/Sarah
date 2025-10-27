'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useCharacterStore } from '@/store/character-store'
import { CharacterSelector } from '@/components/character-selector'
import { Button } from '@/components/ui/button'
import { MessageSquare, Sparkles, User } from 'lucide-react'

export default function HomePage() {
  const router = useRouter()
  const { characters, selectedCharacter, fetchCharacters } = useCharacterStore()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadCharacters = async () => {
      setIsLoading(true)
      // TODO: Get actual user ID from auth
      await fetchCharacters('user123')
      setIsLoading(false)
    }
    loadCharacters()
  }, [fetchCharacters])

  const handleStartChat = () => {
    if (selectedCharacter) {
      router.push('/chat')
    }
  }

  const handleCreateCharacter = () => {
    router.push('/character/create')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-dark-100 dark:via-dark-200 dark:to-dark-300">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Sarah AI Companion
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Your intelligent, empathetic AI companion
          </p>
        </header>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
            </div>
          ) : (
            <>
              {/* Character Selection */}
              <div className="bg-white dark:bg-dark-200 rounded-2xl shadow-xl p-8 mb-8">
                <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
                  <User className="w-6 h-6 text-primary-500" />
                  Choose Your Companion
                </h2>
                
                {characters.length > 0 ? (
                  <>
                    <CharacterSelector />
                    
                    <div className="mt-8 flex gap-4 justify-center">
                      <Button
                        onClick={handleStartChat}
                        disabled={!selectedCharacter}
                        size="lg"
                        className="gap-2"
                      >
                        <MessageSquare className="w-5 h-5" />
                        Start Chatting
                      </Button>
                      
                      <Button
                        onClick={handleCreateCharacter}
                        variant="outline"
                        size="lg"
                        className="gap-2"
                      >
                        <Sparkles className="w-5 h-5" />
                        Create New Character
                      </Button>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                      You haven't created any companions yet. Let's create your first one!
                    </p>
                    <Button
                      onClick={handleCreateCharacter}
                      size="lg"
                      className="gap-2"
                    >
                      <Sparkles className="w-5 h-5" />
                      Create Your First Companion
                    </Button>
                  </div>
                )}
              </div>

              {/* Features Section */}
              <div className="grid md:grid-cols-3 gap-6">
                <FeatureCard
                  icon={<MessageSquare className="w-8 h-8" />}
                  title="Natural Conversations"
                  description="Engage in fluid, context-aware conversations with your AI companion"
                />
                <FeatureCard
                  icon={<Sparkles className="w-8 h-8" />}
                  title="Unique Personalities"
                  description="Create companions with distinct personalities, voices, and appearances"
                />
                <FeatureCard
                  icon={<User className="w-8 h-8" />}
                  title="Perfect Memory"
                  description="Your companion remembers past conversations and learns about you"
                />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function FeatureCard({ icon, title, description }: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="bg-white dark:bg-dark-200 rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
      <div className="text-primary-500 mb-4">{icon}</div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-gray-600 dark:text-gray-400">{description}</p>
    </div>
  )
}
