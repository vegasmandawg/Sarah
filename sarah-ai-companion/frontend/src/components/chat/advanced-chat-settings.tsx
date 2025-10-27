'use client'

import { ChangeEvent } from 'react'
import { Button } from '@/components/ui/button'
import { cn, describeIntensity, describeExplicitLevel } from '@/lib/utils'
import { useChatSettingsStore } from '@/store/chat-settings-store'
import { Sparkles, Flame, RefreshCw } from 'lucide-react'

const MOOD_OPTIONS = [
  { value: 'romantic', label: 'Romantic' },
  { value: 'playful', label: 'Playful' },
  { value: 'teasing', label: 'Teasing' },
  { value: 'dominant', label: 'Dominant' },
  { value: 'submissive', label: 'Submissive' },
  { value: 'tender', label: 'Tender' },
] as const

const EXPLICIT_LEVELS = [
  { value: 'suggestive', description: 'Flirty hints, heavy teasing' },
  { value: 'heated', description: 'Bold descriptions, intense build-up' },
  { value: 'explicit', description: 'Unfiltered detail, raw desire' },
] as const

const PACING_OPTIONS = [
  { value: 'slow_burn', label: 'Slow Burn' },
  { value: 'steady', label: 'Steady' },
  { value: 'fast', label: 'All In' },
] as const

const NARRATION_OPTIONS = [
  { value: 'first_person', label: 'First Person' },
  { value: 'third_person', label: 'Third Person' },
  { value: 'mixed', label: 'Mixed' },
] as const

const GREEN_LIGHT_LIBRARY = [
  'Dirty talk',
  'Physical affection',
  'Sensory detail',
  'Roleplay',
  'Praise',
  'Spanking',
  'Power dynamics',
  'Voyeurism',
  'Public teasing',
  'Pet names',
] as const

const LIMIT_LIBRARY = [
  'Non-consent',
  'Gore',
  'Humiliation',
  'Pain',
  'Name-calling',
  'Breath control',
  'Toxic dynamics',
  'Public exposure',
  'Watersports',
  'Ageplay',
] as const

export function AdvancedChatSettings() {
  const {
    mood,
    explicitLevel,
    intensity,
    pacing,
    narrationStyle,
    roleplayMode,
    allowNarration,
    voiceResponses,
    showSentiment,
    autoImages,
    safeWord,
    greenLights,
    hardLimits,
    aftercareNotes,
    updateSetting,
    toggleGreenLight,
    toggleHardLimit,
    reset,
  } = useChatSettingsStore()

  const handleSlider = (event: ChangeEvent<HTMLInputElement>) => {
    updateSetting('intensity', Number(event.target.value))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Advanced intimacy controls</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Tune the vibe, pacing, and boundaries for a fully immersive adult experience.
          </p>
        </div>
        <Button variant="ghost" size="sm" className="gap-2 text-xs" onClick={reset}>
          <RefreshCw className="h-3.5 w-3.5" /> Reset
        </Button>
      </div>

      <section className="space-y-3">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase text-gray-500">
          <Sparkles className="h-4 w-4 text-primary-500" /> Mood &amp; tone
        </div>
        <div className="grid grid-cols-2 gap-2">
          {MOOD_OPTIONS.map((option) => (
            <Button
              key={option.value}
              variant={mood === option.value ? 'secondary' : 'outline'}
              className="w-full"
              onClick={() => updateSetting('mood', option.value)}
            >
              {option.label}
            </Button>
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase text-gray-500">
          <Flame className="h-4 w-4 text-secondary-500" /> Heat level
        </div>
        <div>
          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>{describeIntensity(intensity)}</span>
            <span>{intensity}%</span>
          </div>
          <input
            type="range"
            min={0}
            max={100}
            step={5}
            value={intensity}
            onChange={handleSlider}
            className="mt-2 h-2 w-full cursor-pointer appearance-none rounded-full bg-gradient-to-r from-rose-400 via-primary-400 to-secondary-500"
          />
        </div>

        <div className="grid grid-cols-1 gap-2 md:grid-cols-3">
          {EXPLICIT_LEVELS.map((level) => (
            <button
              key={level.value}
              type="button"
              onClick={() => updateSetting('explicitLevel', level.value)}
              className={cn(
                'rounded-lg border px-3 py-3 text-left transition hover:border-primary-400 hover:shadow-sm',
                explicitLevel === level.value
                  ? 'border-primary-500 bg-primary-50 dark:border-primary-400/70 dark:bg-primary-500/10'
                  : 'border-gray-200 dark:border-gray-700'
              )}
            >
              <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                {describeExplicitLevel(level.value)}
              </p>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{level.description}</p>
            </button>
          ))}
        </div>
      </section>

      <section className="grid gap-3 md:grid-cols-3">
        {PACING_OPTIONS.map((option) => (
          <Button
            key={option.value}
            variant={pacing === option.value ? 'secondary' : 'outline'}
            onClick={() => updateSetting('pacing', option.value)}
          >
            {option.label}
          </Button>
        ))}

        {NARRATION_OPTIONS.map((option) => (
          <Button
            key={option.value}
            variant={narrationStyle === option.value ? 'secondary' : 'outline'}
            onClick={() => updateSetting('narrationStyle', option.value)}
          >
            {option.label}
          </Button>
        ))}
      </section>

      <section className="grid gap-3 md:grid-cols-2">
        <label className="flex items-center gap-3 rounded-lg border border-gray-200 p-3 text-sm dark:border-gray-700">
          <input
            type="checkbox"
            checked={roleplayMode}
            onChange={(event) => updateSetting('roleplayMode', event.target.checked)}
            className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <div>
            <p className="font-medium text-gray-900 dark:text-gray-100">Immersive roleplay mode</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Stay fully in character, narrate actions, and embrace the fantasy.
            </p>
          </div>
        </label>

        <label className="flex items-center gap-3 rounded-lg border border-gray-200 p-3 text-sm dark:border-gray-700">
          <input
            type="checkbox"
            checked={allowNarration}
            onChange={(event) => updateSetting('allowNarration', event.target.checked)}
            className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <div>
            <p className="font-medium text-gray-900 dark:text-gray-100">Narrate sensations</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Encourage vivid sensory detail describing touch, taste, scent, and emotion.
            </p>
          </div>
        </label>
      </section>

      <section className="space-y-3">
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="text-xs font-semibold uppercase text-gray-500">Safe word</label>
            <input
              type="text"
              value={safeWord}
              onChange={(event) => updateSetting('safeWord', event.target.value)}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/40 dark:border-gray-700 dark:bg-dark-100"
              placeholder="Enter your safe word"
            />
          </div>

          <div>
            <label className="text-xs font-semibold uppercase text-gray-500">Aftercare notes</label>
            <textarea
              value={aftercareNotes}
              onChange={(event) => updateSetting('aftercareNotes', event.target.value)}
              rows={3}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/40 dark:border-gray-700 dark:bg-dark-100"
              placeholder="How should Sarah check in with you afterwards?"
            />
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <div>
          <div className="mb-2 text-xs font-semibold uppercase text-gray-500">Turn-ons</div>
          <div className="flex flex-wrap gap-2">
            {GREEN_LIGHT_LIBRARY.map((item) => {
              const isActive = greenLights.includes(item)
              return (
                <Button
                  key={item}
                  size="sm"
                  variant={isActive ? 'secondary' : 'outline'}
                  className="text-xs"
                  onClick={() => toggleGreenLight(item)}
                >
                  {item}
                </Button>
              )
            })}
          </div>
        </div>

        <div>
          <div className="mb-2 text-xs font-semibold uppercase text-gray-500">Hard limits</div>
          <div className="flex flex-wrap gap-2">
            {LIMIT_LIBRARY.map((item) => {
              const isActive = hardLimits.includes(item)
              return (
                <Button
                  key={item}
                  size="sm"
                  variant={isActive ? 'destructive' : 'outline'}
                  className={cn('text-xs', isActive && 'border-red-500 bg-red-50 text-red-600 dark:bg-red-500/10')}
                  onClick={() => toggleHardLimit(item)}
                >
                  {item}
                </Button>
              )
            })}
          </div>
        </div>
      </section>

      <section className="space-y-2">
        <h4 className="text-xs font-semibold uppercase text-gray-500">Immersion preferences</h4>
        <div className="grid gap-2 md:grid-cols-3">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={voiceResponses}
              onChange={(event) => updateSetting('voiceResponses', event.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span>Enable voice responses</span>
          </label>

          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showSentiment}
              onChange={(event) => updateSetting('showSentiment', event.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span>Show emotional heat meter</span>
          </label>

          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={autoImages}
              onChange={(event) => updateSetting('autoImages', event.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span>Auto-generate sensual imagery</span>
          </label>
        </div>
      </section>

      <section className="rounded-lg border border-dashed border-secondary-400/50 bg-secondary-500/5 p-4 text-xs text-secondary-600 dark:border-secondary-500/50 dark:text-secondary-200">
        Sarah follows your guidance to craft a consensual adult experience. Update these controls anytime if you want to shift the
        mood, push the heat, or slow things down.
      </section>
    </div>
  )
}
