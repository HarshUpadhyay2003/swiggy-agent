import React from 'react'
import { Sparkles } from 'lucide-react'
import Badge from '../ui/Badge'

export function MatchScoreBadge({ score = 0.95, className = '' }) {
  const percentage = Math.round(score > 1 ? score : score * 100)

  return (
    <div className={`inline-flex items-center gap-1.5 rounded-full bg-white/85 dark:bg-slate-900/85 backdrop-blur-md px-3 py-1 text-xs font-bold text-swiggy-700 dark:text-swiggy-400 border border-swiggy-500/30 shadow-xs ${className}`}>
      <Sparkles className="h-3.5 w-3.5 text-swiggy-500 animate-pulse" />
      <span>{percentage}% AI Match</span>
    </div>
  )
}

export default MatchScoreBadge
