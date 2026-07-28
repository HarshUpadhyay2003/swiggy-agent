import React, { useState } from 'react'
import { Star, Clock, HelpCircle, Check, Sparkles, X } from 'lucide-react'
import { foodImages } from '../../assets/images'

export function RecommendationCard({ item, index = 0, onAdd, onReplace }) {
  const [added, setAdded] = useState(false)
  const [showWhyThis, setShowWhyThis] = useState(false)

  if (!item) return null

  const name = item.name || item.title || 'Gourmet Selection'
  const price = item.price ?? item.estimated_cost ?? 450
  const restaurant = item.restaurant_name || item.brand || 'The Bowl Co.'
  const rating = item.rating || 4.8
  const deliveryTime = item.delivery_time || '25 mins'
  const isVeg = item.is_veg !== false && item.dietary_tags?.includes('veg') !== false

  // Image registry mapper
  const getRegistryImage = () => {
    if (item.image_url) return item.image_url
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

  const imgUrl = getRegistryImage()

  const handleAdd = () => {
    onAdd && onAdd(item)
    setAdded(true)
    setTimeout(() => setAdded(false), 1800)
  }

  return (
    <div className="glass-panel rounded-xl shrink-0 w-full sm:w-[320px] md:w-[340px] flex flex-col overflow-hidden card-shadow group relative border border-white/60 dark:border-slate-800 transition-all duration-300">
      {/* Image Area */}
      <div className="relative h-[200px] w-full overflow-hidden bg-slate-100 dark:bg-slate-800">
        <img
          src={imgUrl}
          alt={name}
          className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
          loading="lazy"
          onError={(e) => {
            e.target.style.display = 'none'
          }}
        />
        {/* Price Pill */}
        <div className="absolute top-3 right-3 glass-panel rounded-full px-3 py-1 text-sm font-semibold text-slate-900 dark:text-slate-100 shadow-sm">
          ₹{price}
        </div>
      </div>

      {/* Content Body */}
      <div className="p-5 flex flex-col flex-grow bg-white/40 dark:bg-slate-900/40">
        <div className="flex justify-between items-start mb-1">
          <h3 className="font-serif text-xl font-bold text-slate-900 dark:text-slate-100 leading-tight">
            {name}
          </h3>
        </div>
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-3 font-medium">
          {restaurant}
        </p>

        {/* Rating & ETA */}
        <div className="flex items-center gap-3 mb-4">
          <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 rounded-full px-2.5 py-0.5 text-xs font-semibold text-slate-900 dark:text-slate-100">
            <Star className="h-3.5 w-3.5 fill-swiggy-500 text-swiggy-500" />
            <span>{rating}</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
            <Clock className="h-3.5 w-3.5" />
            <span>{deliveryTime}</span>
          </div>
        </div>

        {/* Tag Chips */}
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="bg-veg-bg text-veg-dark font-medium text-xs px-2.5 py-1 rounded-md border border-veg-border dark:bg-veg-dark/20 dark:text-veg-container">
            {isVeg ? 'Veg' : 'Non-Veg'}
          </span>
          <span className="bg-emerald-50 text-emerald-800 font-medium text-xs px-2.5 py-1 rounded-md border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300">
            High Protein
          </span>
          <span className="bg-amber-50 text-amber-800 font-medium text-xs px-2.5 py-1 rounded-md border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300">
            Fresh
          </span>
        </div>

        {/* AI Reason Quote Box */}
        <div className="bg-white/60 dark:bg-slate-800/60 rounded-lg p-3 mb-4 border border-slate-200/50 dark:border-slate-700/50 flex-grow">
          <p className="text-xs leading-relaxed text-slate-600 dark:text-slate-300 italic">
            "{item.reason || 'Matches your craving for a fresh meal and hits your nutritional goals.'}"
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 mt-auto">
          <button
            type="button"
            onClick={handleAdd}
            className={`flex-1 ${
              added ? 'bg-emerald-600' : 'bg-swiggy-500 hover:bg-swiggy-600'
            } text-white font-semibold text-sm py-3 rounded-full transition-colors shadow-sm flex items-center justify-center gap-1.5`}
          >
            {added ? <Check className="h-4 w-4" /> : null}
            {added ? 'Added to Cart' : 'Add to Cart'}
          </button>
          <button
            type="button"
            onClick={() => setShowWhyThis(!showWhyThis)}
            className="w-12 h-12 flex items-center justify-center bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 rounded-full hover:bg-slate-100 transition-colors shrink-0"
            title="Why this?"
          >
            <HelpCircle className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Why This Popup Overlay */}
      {showWhyThis && (
        <div className="absolute inset-0 z-30 glass-panel rounded-xl p-4 flex flex-col justify-between animate-fadeIn bg-white/95 dark:bg-slate-900/95 border border-swiggy-500/30">
          <div className="flex justify-between items-start mb-2">
            <h4 className="font-semibold text-xs text-swiggy-600 dark:text-swiggy-400 flex items-center gap-1">
              <Sparkles className="h-4 w-4" /> AI Match Analysis
            </h4>
            <button
              type="button"
              onClick={() => setShowWhyThis(false)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <p className="text-xs leading-snug text-slate-600 dark:text-slate-300 mb-4 italic">
            "{item.reason || 'We chose this item because it complements your nutritional preferences and budget constraint.'}"
          </p>
          <div className="space-y-2 text-[11px] text-slate-600 dark:text-slate-300">
            <div>
              <div className="flex justify-between mb-1">
                <span>Budget Match</span>
                <span className="font-bold text-emerald-600">95%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 w-[95%] rounded-full" />
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span>Health Score</span>
                <span className="font-bold text-amber-600">88%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-amber-500 w-[88%] rounded-full" />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default RecommendationCard
