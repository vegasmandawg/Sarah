// Character types
export interface Character {
  character_id: string
  user_id: string
  name: string
  persona_prompt: string
  voice_id?: string
  appearance_seed?: string
  created_at: string
  updated_at: string
}

export interface CharacterCreateRequest {
  name: string
  user_id: string
  persona_prompt?: string
  voice_id?: string
  appearance_seed?: string
  personality_traits?: string[]
  hobbies?: string[]
}

// Chat types
export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: {
    sentiment?: SentimentData
    status?: 'sending' | 'sent' | 'error'
    image_url?: string
    audio_url?: string
  }
}

export interface SentimentData {
  compound: number
  positive: number
  negative: number
  neutral: number
}

// WebSocket message types
export type WebSocketMessage = 
  | { type: 'message'; content: string }
  | { type: 'token'; content: string }
  | { type: 'status'; task: string }
  | { type: 'complete'; sentiment?: SentimentData }
  | { type: 'error'; content: string }

// Voice options
export interface VoiceOption {
  voice_id: string
  name: string
  description: string
  preview_url?: string
  gender?: string
  age?: string
}

// Image generation
export interface ImageGenerationRequest {
  prompt: string
  negative_prompt?: string
  character_lora_id?: string
  width?: number
  height?: number
  num_inference_steps?: number
  guidance_scale?: number
  seed?: number
}

export interface ImageGenerationResponse {
  image_id: string
  filename: string
  prompt: string
  width: number
  height: number
  url: string
  timestamp: string
}

// Voice generation
export interface VoiceGenerationRequest {
  text: string
  voice_id?: string
  stability?: number
  similarity_boost?: number
  style?: number
}

export interface VoiceGenerationResponse {
  audio_id: string
  filename: string
  text: string
  enhanced_text: string
  voice_id: string
  url: string
  duration_seconds?: number
  timestamp: string
}

// Memory types
export interface MemoryContext {
  context: string
  relevant_facts: KeyFact[]
  conversation_snippets: string[]
}

export interface KeyFact {
  type: string
  key: string
  value: string
  timestamp: string
}

// Form types
export interface CharacterFormData {
  name: string
  personality_traits: string[]
  hobbies: string[]
  voice_id?: string
  persona_prompt?: string
  images?: File[]
}
