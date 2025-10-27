'use client'

import { useCharacterStore } from '@/store/character-store'
import { Character } from '@/types'
import { cn, formatDate } from '@/lib/utils'
import { Check, User, Volume2 } from 'lucide-react'

export function CharacterSelector() {
  const { characters, selectedCharacter, selectCharacter } = useCharacterStore()

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {characters.map((character) => (
        <CharacterCard
          key={character.character_id}
          character={character}
          isSelected={selectedCharacter?.character_id === character.character_id}
          onSelect={() => selectCharacter(character)}
        />
      ))}
    </div>
  )
}

interface CharacterCardProps {
  character: Character
  isSelected: boolean
  onSelect: () => void
}

function CharacterCard({ character, isSelected, onSelect }: CharacterCardProps) {
  return (
    <button
      onClick={onSelect}
      className={cn(
        'relative p-6 rounded-xl border-2 transition-all text-left hover:shadow-lg',
        isSelected
          ? 'border-primary-500 bg-primary-50 dark:bg-primary-950/20'
          : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'
      )}
    >
      {isSelected && (
        <div className="absolute top-4 right-4">
          <div className="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
            <Check className="w-4 h-4 text-white" />
          </div>
        </div>
      )}

      <div className="flex items-start gap-4">
        <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center flex-shrink-0">
          <User className="w-6 h-6 text-white" />
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
            {character.name}
          </h3>
          
          <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-3">
            {character.persona_prompt}
          </p>

          <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-500">
            {character.voice_id && (
              <div className="flex items-center gap-1">
                <Volume2 className="w-3 h-3" />
                <span>Voice enabled</span>
              </div>
            )}
            <span>Created {formatDate(character.created_at)}</span>
          </div>
        </div>
      </div>
    </button>
  )
}
