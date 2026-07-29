import React from 'react'
import { getFoodImage } from '../../assets/images'
import MatchScoreBadge from './MatchScoreBadge'
import Badge from '../ui/Badge'

export function RecommendationImage({ name = '', imageUrl = null, matchScore = 0.95, price = 240, index = 0 }) {
  const finalSrc = imageUrl || getFoodImage(name, index)

  return (
    <div className="relative aspect-[16/10] w-full overflow-hidden bg-slate-100 dark:bg-slate-800">
      <img
        src={finalSrc}
        alt={name}
        className="h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-108"
        loading="lazy"
        onError={(e) => {
          e.target.style.display = 'none'
        }}
      />

      {/* Dark Vignette Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/30" />

      {/* Top Floating Match Score Badge */}
      <div className="absolute top-3 left-3">
        <MatchScoreBadge score={matchScore} />
      </div>

      {/* Top Price Pill */}
      <div className="absolute top-3 right-3">
        <Badge variant="glass" size="md" className="font-bold text-slate-900 dark:text-slate-100">
          ₹{price}
        </Badge>
      </div>
    </div>
  )
}

export default RecommendationImage
