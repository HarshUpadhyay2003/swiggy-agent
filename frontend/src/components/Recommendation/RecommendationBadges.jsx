import React from 'react'
import VegIndicator from '../ui/VegIndicator'
import Chip from '../ui/Chip'

export function RecommendationBadges({ isVeg = true, tags = [], reason = '', className = '' }) {
  // Extract or formulate formatted reason chips
  const deriveChips = () => {
    const list = []
    if (tags && tags.length > 0) {
      tags.forEach((tag) => list.push(`✓ ${tag}`))
    }

    if (reason) {
      const lower = reason.toLowerCase()
      if (lower.includes('protein') && !list.some(c => c.toLowerCase().includes('protein'))) {
        list.push('✓ High Protein')
      }
      if (lower.includes('budget') || lower.includes('cheap') || lower.includes('under')) {
        list.push('✓ Within Budget')
      }
      if (lower.includes('healthy') || lower.includes('fresh')) {
        list.push('✓ Low Calorie')
      }
      if (lower.includes('popular') || lower.includes('trending')) {
        list.push('✓ Popular')
      }
    }

    if (list.length === 0) {
      list.push('✓ AI Pick')
    }

    return list.slice(0, 3)
  }

  const chips = deriveChips()

  return (
    <div className={`flex flex-wrap items-center gap-1.5 ${className}`}>
      <VegIndicator isVeg={isVeg} size="sm" />
      {chips.map((chipText, idx) => (
        <span
          key={idx}
          className="inline-flex items-center rounded-full bg-emerald-50 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-800 border border-emerald-200/60 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-900/60"
        >
          {chipText}
        </span>
      ))}
    </div>
  )
}

export default RecommendationBadges
