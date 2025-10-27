import clsx, { type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { format, isValid, parseISO } from 'date-fns'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(value: string | number | Date) {
  if (!value) return ''

  let date: Date
  if (value instanceof Date) {
    date = value
  } else if (typeof value === 'number') {
    date = new Date(value)
  } else {
    const parsed = parseISO(value)
    date = isValid(parsed) ? parsed : new Date(value)
  }

  if (!isValid(date)) {
    return typeof value === 'string' ? value : ''
  }

  try {
    return format(date, 'MMM d, yyyy h:mm a')
  } catch (error) {
    return date.toLocaleString()
  }
}

export function getSentimentColor(compound: number) {
  if (compound >= 0.4) return 'text-emerald-500'
  if (compound <= -0.4) return 'text-red-500'
  if (compound >= 0.15) return 'text-lime-500'
  if (compound <= -0.15) return 'text-amber-500'
  return 'text-sky-500'
}

export function getSentimentEmoji(compound: number) {
  if (compound >= 0.4) return '😍'
  if (compound >= 0.15) return '😊'
  if (compound <= -0.4) return '😡'
  if (compound <= -0.15) return '😢'
  return '😌'
}

export function toTitleCase(value: string) {
  if (!value) return ''
  return value
    .split(/[\s_-]+/)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(' ')
}

export function generateMessageId(prefix = 'msg') {
  const random = Math.random().toString(36).slice(2, 10)
  const timestamp = Date.now().toString(36)
  return `${prefix}_${timestamp}_${random}`
}

export function describeIntensity(intensity: number) {
  if (intensity >= 80) return 'Feverish'
  if (intensity >= 60) return 'Heated'
  if (intensity >= 40) return 'Steamy'
  if (intensity >= 20) return 'Slow burn'
  return 'Tender'
}

export function describeExplicitLevel(level: string | undefined) {
  switch (level) {
    case 'suggestive':
      return 'Flirtatious'
    case 'heated':
      return 'Spicy'
    case 'explicit':
      return 'Unfiltered'
    default:
      return toTitleCase(level ?? '')
  }
}

export function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max)
}
