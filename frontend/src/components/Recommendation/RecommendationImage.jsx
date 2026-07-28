import React from 'react'
import { foodImages } from '../../assets/images'
import MatchScoreBadge from './MatchScoreBadge'
import Badge from '../ui/Badge'

export function RecommendationImage({ name = '', imageUrl = null, matchScore = 0.95, price = 240, index = 0 }) {
  // Map food image from registry
  const getRegistryImage = () => {
    if (imageUrl) return imageUrl
    const keys = Object.keys(foodImages)
    if (!name) return foodImages[keys[index % keys.length]]
    const lower = name.toLowerCase()
    if (lower.includes('avocado') || lower.includes('toast') || lower.includes('breakfast')) return foodImages.avocadoToast
    if (lower.includes('salad') || lower.includes('greek') || lower.includes('healthy')) return foodImages.greekSalad
    if (lower.includes('smoothie') || lower.includes('bowl') || lower.includes('berry')) return foodImages.smoothieBowl
    if (lower.includes('chicken') || lower.includes('grilled') || lower.includes('protein')) return foodImages.grilledChicken
    if (lower.includes('pizza') || lower.includes('margherita') || lower.includes('cheese')) return foodImages.margheritaPizza
    if (lower.includes('poke') || lower.includes('salmon') || lower.includes('fish')) return foodImages.pokeBowl
    return foodImages[keys[index % keys.length]]
  }

  const finalSrc = getRegistryImage()

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
