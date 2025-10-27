'use client'

import { useState, useCallback } from 'react'
import { UseFormReturn } from 'react-hook-form'
import { CharacterFormData } from '@/types'
import { Button } from '@/components/ui/button'
import { Upload, X, Sparkles, Loader2 } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'

interface CharacterFormProps {
  form: UseFormReturn<CharacterFormData>
  onSubmit: (data: CharacterFormData) => void
  isSubmitting: boolean
}

const PERSONALITY_TRAITS = [
  'Empathetic', 'Intelligent', 'Witty', 'Supportive', 'Creative',
  'Curious', 'Thoughtful', 'Playful', 'Adventurous', 'Wise',
  'Caring', 'Confident', 'Optimistic', 'Patient', 'Honest'
]

const HOBBIES = [
  'Reading', 'Music', 'Art', 'Cooking', 'Gaming', 'Hiking',
  'Photography', 'Writing', 'Dancing', 'Travel', 'Movies',
  'Sports', 'Gardening', 'Technology', 'Fashion'
]

const VOICE_OPTIONS = [
  { id: '21m00Tcm4TlvDq8ikWAM', name: 'Rachel', description: 'Warm and friendly' },
  { id: 'AZnzlk1XvdvUeBnXmlld', name: 'Domi', description: 'Young and energetic' },
  { id: 'EXAVITQu4vr4xnSDxMaL', name: 'Bella', description: 'Soft and expressive' },
]

export function CharacterForm({ form, onSubmit, isSubmitting }: CharacterFormProps) {
  const [isGeneratingPersona, setIsGeneratingPersona] = useState(false)
  const { register, watch, setValue, formState: { errors } } = form
  
  const selectedTraits = watch('personality_traits') || []
  const selectedHobbies = watch('hobbies') || []
  const uploadedImages = watch('images') || []

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setValue('images', [...uploadedImages, ...acceptedFiles])
  }, [uploadedImages, setValue])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp']
    },
    maxFiles: 20,
  })

  const removeImage = (index: number) => {
    setValue('images', uploadedImages.filter((_, i) => i !== index))
  }

  const toggleTrait = (trait: string) => {
    if (selectedTraits.includes(trait)) {
      setValue('personality_traits', selectedTraits.filter(t => t !== trait))
    } else {
      setValue('personality_traits', [...selectedTraits, trait])
    }
  }

  const toggleHobby = (hobby: string) => {
    if (selectedHobbies.includes(hobby)) {
      setValue('hobbies', selectedHobbies.filter(h => h !== hobby))
    } else {
      setValue('hobbies', [...selectedHobbies, hobby])
    }
  }

  const generatePersona = async () => {
    if (selectedTraits.length === 0) {
      toast.error('Please select at least one personality trait')
      return
    }

    setIsGeneratingPersona(true)
    try {
      const response = await api.post('/characters/generate-prompt', {
        personality_traits: selectedTraits,
        hobbies: selectedHobbies,
      })
      
      setValue('persona_prompt', response.data.persona_prompt)
      toast.success('Persona generated successfully!')
    } catch (error) {
      toast.error('Failed to generate persona')
    } finally {
      setIsGeneratingPersona(false)
    }
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
      {/* Step 1: Basic Info */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Step 1: Basic Information</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Character Name <span className="text-red-500">*</span>
            </label>
            <input
              {...register('name', { required: 'Name is required' })}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              placeholder="e.g., Sarah, Luna, Max"
            />
            {errors.name && (
              <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Voice</label>
            <select
              {...register('voice_id')}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="">No voice (text only)</option>
              {VOICE_OPTIONS.map(voice => (
                <option key={voice.id} value={voice.id}>
                  {voice.name} - {voice.description}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Step 2: Personality */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Step 2: Personality & Interests</h2>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-3">
              Personality Traits (select 3-5)
            </label>
            <div className="flex flex-wrap gap-2">
              {PERSONALITY_TRAITS.map(trait => (
                <button
                  key={trait}
                  type="button"
                  onClick={() => toggleTrait(trait)}
                  className={`px-4 py-2 rounded-full text-sm transition-colors ${
                    selectedTraits.includes(trait)
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {trait}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-3">
              Hobbies & Interests (optional)
            </label>
            <div className="flex flex-wrap gap-2">
              {HOBBIES.map(hobby => (
                <button
                  key={hobby}
                  type="button"
                  onClick={() => toggleHobby(hobby)}
                  className={`px-4 py-2 rounded-full text-sm transition-colors ${
                    selectedHobbies.includes(hobby)
                      ? 'bg-secondary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {hobby}
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium">
                Persona Description
              </label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={generatePersona}
                disabled={isGeneratingPersona || selectedTraits.length === 0}
                className="gap-2"
              >
                {isGeneratingPersona ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Sparkles className="w-4 h-4" />
                )}
                Generate with AI
              </Button>
            </div>
            <textarea
              {...register('persona_prompt')}
              rows={6}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              placeholder="Describe your character's personality, background, and how they interact..."
            />
          </div>
        </div>
      </div>

      {/* Step 3: Appearance (Optional) */}
      <div>
        <h2 className="text-xl font-semibold mb-4">
          Step 3: Visual Appearance (Optional)
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          Upload 5-20 reference images to create a consistent visual appearance for your character
        </p>

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600">
            {isDragActive
              ? 'Drop the images here...'
              : 'Drag & drop images here, or click to select'}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            PNG, JPG, JPEG, WEBP up to 10MB each
          </p>
        </div>

        {uploadedImages.length > 0 && (
          <div className="mt-4 grid grid-cols-4 gap-4">
            {uploadedImages.map((file, index) => (
              <div key={index} className="relative group">
                <img
                  src={URL.createObjectURL(file)}
                  alt={`Reference ${index + 1}`}
                  className="w-full h-24 object-cover rounded-lg"
                />
                <button
                  type="button"
                  onClick={() => removeImage(index)}
                  className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Submit Button */}
      <div className="flex justify-end gap-4 pt-6 border-t">
        <Button
          type="button"
          variant="outline"
          onClick={() => window.history.back()}
          disabled={isSubmitting}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={isSubmitting}
          className="gap-2"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Creating...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Create Character
            </>
          )}
        </Button>
      </div>
    </form>
  )
}
