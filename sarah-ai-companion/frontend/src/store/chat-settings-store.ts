import { create } from 'zustand'
import { ChatPreferencesPayload } from '@/types'

const DEFAULT_GREEN_LIGHTS = ['Dirty talk', 'Physical affection', 'Compliments'] as const
const DEFAULT_LIMITS = ['Non-consent', 'Gore', 'Humiliation'] as const

type MoodOption = 'romantic' | 'playful' | 'teasing' | 'dominant' | 'submissive' | 'tender'
type ExplicitLevel = 'suggestive' | 'heated' | 'explicit'
type NarrationStyle = 'first_person' | 'third_person' | 'mixed'
type Pacing = 'slow_burn' | 'steady' | 'fast'

type SettingsFields = {
  mood: MoodOption
  explicitLevel: ExplicitLevel
  intensity: number
  pacing: Pacing
  narrationStyle: NarrationStyle
  roleplayMode: boolean
  allowNarration: boolean
  voiceResponses: boolean
  showSentiment: boolean
  autoImages: boolean
  safeWord: string
  greenLights: string[]
  hardLimits: string[]
  aftercareNotes: string
}

const defaultSettings: SettingsFields = {
  mood: 'romantic',
  explicitLevel: 'heated',
  intensity: 65,
  pacing: 'steady',
  narrationStyle: 'mixed',
  roleplayMode: true,
  allowNarration: true,
  voiceResponses: true,
  showSentiment: true,
  autoImages: false,
  safeWord: 'red',
  greenLights: [...DEFAULT_GREEN_LIGHTS],
  hardLimits: [...DEFAULT_LIMITS],
  aftercareNotes: 'Be tender, check in on emotions, and offer affectionate aftercare.',
}

type SettingsKeys = keyof SettingsFields

interface ChatSettingsState extends SettingsFields {
  updateSetting: <K extends SettingsKeys>(key: K, value: SettingsFields[K]) => void
  toggleGreenLight: (item: string) => void
  toggleHardLimit: (item: string) => void
  reset: () => void
}

export const useChatSettingsStore = create<ChatSettingsState>((set) => ({
  ...defaultSettings,
  updateSetting: (key, value) =>
    set(() => ({ [key]: value } as Partial<ChatSettingsState>)),
  toggleGreenLight: (item) =>
    set((state) => ({
      greenLights: state.greenLights.includes(item)
        ? state.greenLights.filter((entry) => entry !== item)
        : [...state.greenLights, item],
    })),
  toggleHardLimit: (item) =>
    set((state) => ({
      hardLimits: state.hardLimits.includes(item)
        ? state.hardLimits.filter((entry) => entry !== item)
        : [...state.hardLimits, item],
    })),
  reset: () =>
    set(() => ({
      ...defaultSettings,
      greenLights: [...defaultSettings.greenLights],
      hardLimits: [...defaultSettings.hardLimits],
    })),
}))

export const selectChatPreferences = (state: ChatSettingsState): ChatPreferencesPayload => ({
  mood: state.mood,
  explicit_level: state.explicitLevel,
  intensity: state.intensity,
  pacing: state.pacing,
  narration_style: state.narrationStyle,
  roleplay_mode: state.roleplayMode,
  allow_narration: state.allowNarration,
  safe_word: state.safeWord,
  green_lights: state.greenLights,
  hard_limits: state.hardLimits,
  aftercare_notes: state.aftercareNotes,
})
