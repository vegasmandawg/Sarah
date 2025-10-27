import { create } from 'zustand'
import { Character } from '@/types'
import { api } from '@/lib/api'

interface CharacterStore {
  characters: Character[]
  selectedCharacter: Character | null
  isLoading: boolean
  error: string | null
  
  // Actions
  fetchCharacters: (userId: string) => Promise<void>
  selectCharacter: (character: Character) => void
  createCharacter: (data: Partial<Character>) => Promise<Character>
  updateCharacter: (id: string, data: Partial<Character>) => Promise<void>
  deleteCharacter: (id: string) => Promise<void>
  clearError: () => void
}

export const useCharacterStore = create<CharacterStore>((set, get) => ({
  characters: [],
  selectedCharacter: null,
  isLoading: false,
  error: null,

  fetchCharacters: async (userId: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.get(`/characters/user/${userId}`)
      set({ 
        characters: response.data.characters,
        selectedCharacter: response.data.characters[0] || null,
        isLoading: false 
      })
    } catch (error) {
      set({ 
        error: 'Failed to fetch characters', 
        isLoading: false 
      })
    }
  },

  selectCharacter: (character: Character) => {
    set({ selectedCharacter: character })
  },

  createCharacter: async (data: Partial<Character>) => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.post('/characters', data)
      const newCharacter = response.data
      set((state) => ({
        characters: [...state.characters, newCharacter],
        selectedCharacter: newCharacter,
        isLoading: false
      }))
      return newCharacter
    } catch (error) {
      set({ 
        error: 'Failed to create character', 
        isLoading: false 
      })
      throw error
    }
  },

  updateCharacter: async (id: string, data: Partial<Character>) => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.put(`/characters/${id}`, data)
      const updatedCharacter = response.data
      set((state) => ({
        characters: state.characters.map(c => 
          c.character_id === id ? updatedCharacter : c
        ),
        selectedCharacter: state.selectedCharacter?.character_id === id 
          ? updatedCharacter 
          : state.selectedCharacter,
        isLoading: false
      }))
    } catch (error) {
      set({ 
        error: 'Failed to update character', 
        isLoading: false 
      })
      throw error
    }
  },

  deleteCharacter: async (id: string) => {
    set({ isLoading: true, error: null })
    try {
      await api.delete(`/characters/${id}`)
      set((state) => {
        const newCharacters = state.characters.filter(c => c.character_id !== id)
        return {
          characters: newCharacters,
          selectedCharacter: state.selectedCharacter?.character_id === id 
            ? newCharacters[0] || null 
            : state.selectedCharacter,
          isLoading: false
        }
      })
    } catch (error) {
      set({ 
        error: 'Failed to delete character', 
        isLoading: false 
      })
      throw error
    }
  },

  clearError: () => {
    set({ error: null })
  }
}))
