'use client'

import { cn } from '@/lib/utils'
import { Flame, Heart, Rabbit, Shield, Sparkles, Sparkle } from 'lucide-react'

interface QuickAction {
  label: string
  description: string
  prompt: string
  icon: 'heat' | 'romance' | 'immersion' | 'aftercare' | 'pace' | 'boundary'
}

const ACTIONS: QuickAction[] = [
  {
    label: 'Turn up the heat',
    description: 'Ask Sarah to get more explicit and hungry',
    prompt:
      "Turn the intensity all the way up. Be explicit, hungry, and vividly detail what you're doing to me while honouring our boundaries.",
    icon: 'heat',
  },
  {
    label: 'Slow tease',
    description: 'Ease into the moment with lingering anticipation',
    prompt:
      "Dial things back to a slow, sensual tease. Build anticipation with whispered promises, soft touches, and vivid sensory description before anything explicit happens.",
    icon: 'pace',
  },
  {
    label: 'Romance me',
    description: 'Shift into affectionate, heart-melting energy',
    prompt:
      'Wrap me up in romantic affection. Compliment me, reassure me, and let the intimacy feel warm, safe, and deeply loving.',
    icon: 'romance',
  },
  {
    label: 'Stay in character',
    description: 'Reaffirm the persona and immersive roleplay',
    prompt:
      "Double down on the roleplay. Speak and act purely as your persona, react to me in real time, and avoid breaking the fourth wall.",
    icon: 'immersion',
  },
  {
    label: 'Aftercare',
    description: 'Shift into gentle check-ins and comfort',
    prompt:
      'Move into aftercare. Slow your tone, be tender, check on my emotional and physical wellbeing, and remind me how safe and adored I am.',
    icon: 'aftercare',
  },
  {
    label: 'Use safe word',
    description: 'Signal that things should pause immediately',
    prompt:
      'My safe word is active. Stop all erotic content, prioritise comfort, and guide me through a calming de-escalation while honouring my boundaries.',
    icon: 'boundary',
  },
]

const ICON_MAP = {
  heat: Flame,
  romance: Heart,
  immersion: Sparkles,
  aftercare: Shield,
  pace: Rabbit,
  boundary: Sparkle,
}

interface QuickActionsProps {
  onSelect: (action: { label: string; prompt: string }) => void
  disabled?: boolean
}

export function QuickActions({ onSelect, disabled }: QuickActionsProps) {
  return (
    <div className="border-b border-gray-200 bg-white px-4 py-3 dark:border-gray-800 dark:bg-dark-200">
      <div className="mb-2 flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Scene shortcuts</p>
        <span className="text-[11px] text-gray-400">Tap to inject a vibe shift</span>
      </div>
      <div className="flex snap-x gap-2 overflow-x-auto pb-1">
        {ACTIONS.map((action) => {
          const Icon = ICON_MAP[action.icon]
          return (
            <button
              key={action.label}
              type="button"
              className={cn(
                'snap-start rounded-xl border border-gray-200 bg-white px-3 py-2 text-left text-xs shadow-sm transition hover:-translate-y-0.5 hover:border-primary-400 hover:shadow-md dark:border-gray-700 dark:bg-dark-100',
                disabled && 'cursor-not-allowed opacity-60'
              )}
              disabled={disabled}
              onClick={() => onSelect({ label: action.label, prompt: action.prompt })}
            >
              <div className="mb-1 flex items-center gap-2 text-[11px] font-semibold uppercase text-gray-500 dark:text-gray-400">
                <Icon className="h-3.5 w-3.5 text-primary-500" />
                {action.label}
              </div>
              <p className="text-[11px] leading-tight text-gray-600 dark:text-gray-300">{action.description}</p>
            </button>
          )
        })}
      </div>
    </div>
  )
}
