'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { useCharacterStore } from '@/store/character-store'
import { CharacterFormData } from '@/types'
import { Button } from '@/components/ui/button'
import { CharacterForm } from '@/components/character/character-form'
import { ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'

export default function CreateCharacterPage() {
  const router = useRouter()
  const { createCharacter } = useCharacterStore()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<CharacterFormData>({
    defaultValues: {
      name: '',
      personality_traits: [],
      hobbies: [],
      voice_id: undefined,
      persona_prompt: '',
      images: [],
    },
  })

  const handleSubmit = async (data: CharacterFormData) => {
    setIsSubmitting(true)

    try {
      // If images are provided, use the multipart endpoint
      if (data.images && data.images.length > 0) {
        const formData = new FormData()
        formData.append('name', data.name)
        formData.append('user_id', 'user123') // TODO: Get from auth
        
        if (data.persona_prompt) {
          formData.append('persona_prompt', data.persona_prompt)
        }
        
        if (data.voice_id) {
          formData.append('voice_id', data.voice_id)
        }
        
        if (data.personality_traits.length > 0) {
          formData.append('personality_traits', data.personality_traits.join(','))
        }
        
        if (data.hobbies.length > 0) {
          formData.append('hobbies', data.hobbies.join(','))
        }
        
        data.images.forEach((file) => {
          formData.append('images', file)
        })

        const response = await fetch('/api/characters/with-images', {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) throw new Error('Failed to create character')
        
        const character = await response.json()
        toast.success('Character created successfully!')
        router.push('/chat')
      } else {
        // Use regular JSON endpoint
        await createCharacter({
          name: data.name,
          user_id: 'user123', // TODO: Get from auth
          persona_prompt: data.persona_prompt,
          voice_id: data.voice_id,
          personality_traits: data.personality_traits,
          hobbies: data.hobbies,
        })
        
        toast.success('Character created successfully!')
        router.push('/chat')
      }
    } catch (error) {
      console.error('Failed to create character:', error)
      toast.error('Failed to create character')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-100">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => router.push('/')}
            className="mb-4 gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Button>
          
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Create Your AI Companion
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Design a unique personality for your new AI companion
          </p>
        </div>

        {/* Form */}
        <div className="bg-white dark:bg-dark-200 rounded-xl shadow-lg p-8">
          <CharacterForm
            form={form}
            onSubmit={handleSubmit}
            isSubmitting={isSubmitting}
          />
        </div>
      </div>
    </div>
  )
}
