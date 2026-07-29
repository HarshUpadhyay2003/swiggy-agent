import React, { useState } from 'react'
import { Star, Clock, HelpCircle, Check, Sparkles, X, Heart } from 'lucide-react'
import { getFoodImage } from '../../assets/images'

export function RecommendationCard({ item, index = 0, onAdd, onReplace }) {
  const [added, setAdded] = useState(false)
  const [isFavorite, setIsFavorite] = useState(false)
  const [showWhyThis, setShowWhyThis] = useState(false)

  if (!item) return null

  const name = item.name || item.item_name || item.title || 'Gourmet Selection'
  const price = item.price ?? item.estimated_cost ?? 450
  const restaurant = item.restaurant_name || item.brand || 'The Bowl Co.'
  const rating = item.rating || 4.8
  const deliveryTime = item.delivery_time || '25 mins'
  const isVeg = item.is_veg !== false && item.dietary_tags?.includes('veg') !== false
  const matchScore = item.recommendation_score ?? item.score ?? item.match_score
  const matchPercentage = typeof matchScore === 'number' ? Math.round(matchScore > 1 ? matchScore : matchScore * 100) : null

  const imgUrl = item.image_url || getFoodImage(name, index)

  const handleAdd = () => {
    onAdd && onAdd(item)
    setAdded(true)
    setTimeout(() => setAdded(false), 1800)
  }

  return (
    <div className="glass-panel rounded-2xl shrink-0 w-full sm:w-[320px] md:w-[340px] flex flex-col overflow-hidden shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group relative border border-white/60 dark:border-slate-800">
      {/* Image Area */}
      <div className="relative h-[200px] w-full overflow-hidden bg-slate-100 dark:bg-slate-800">
        <img
          src={imgUrl}
          alt={name}
          className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
          loading="lazy"
          onError={(e) => {
            e.target.onerror = null
            e.target.src = getFoodImage(name, index)
          }}
        />
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/70 via-transparent to-transparent opacity-60 group-hover:opacity-40 transition-opacity" />

        {/* Favorite Button (Top-Left) */}
        <button
          type="button"
          onClick={() => setIsFavorite(!isFavorite)}
          className="absolute top-3 left-3 w-8 h-8 rounded-full glass-panel flex items-center justify-center text-slate-700 dark:text-slate-200 hover:scale-110 active:scale-95 transition-all shadow-sm z-10"
          title="Favorite"
        >
          <Heart className={`h-4 w-4 ${isFavorite ? 'fill-rose-500 text-rose-500' : ''}`} />
        </button>

        {/* AI Match Badge (Top-Left near Favorite) */}
        <div className="absolute bottom-3 left-3 bg-swiggy-500/90 text-white rounded-full px-2.5 py-0.5 text-[11px] font-bold shadow-sm flex items-center gap-1 backdrop-blur-md z-10">
          <Sparkles className="h-3 w-3" />
          <span>{matchPercentage ? `${matchPercentage}% Match` : 'AI Choice'}</span>
        </div>

        {/* Floating Price Pill (Top-Right) */}
        <div className="absolute top-3 right-3 glass-panel rounded-full px-3 py-1 text-xs font-bold text-slate-900 dark:text-slate-100 shadow-sm z-10">
          ₹{price}
        </div>
      </div>

      {/* Content Body */}
      <div className="p-5 flex flex-col flex-grow bg-white/40 dark:bg-slate-900/40 justify-between">
        <div>
          <h3 className="font-serif text-xl font-bold text-slate-900 dark:text-slate-100 leading-tight mb-1 truncate">
            {name}
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 font-medium mb-3">
            {restaurant}
          </p>

          {/* Rating & Delivery Time */}
          <div className="flex items-center gap-3 mb-3">
            <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 rounded-full px-2.5 py-0.5 text-xs font-bold text-slate-900 dark:text-slate-100">
              <Star className="h-3.5 w-3.5 fill-swiggy-500 text-swiggy-500" />
              <span>{rating}</span>
            </div>
            <div className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400 font-medium">
              <Clock className="h-3.5 w-3.5" />
              <span>{deliveryTime}</span>
            </div>
          </div>

          {/* Tag Chips */}
          <div className="flex flex-wrap gap-2 mb-4">
            <span className="bg-veg-bg text-veg-dark font-semibold text-[11px] px-2.5 py-0.5 rounded-md border border-veg-border dark:bg-veg-dark/20 dark:text-veg-container">
              {isVeg ? 'Veg' : 'Non-Veg'}
            </span>
            <span className="bg-emerald-50 text-emerald-800 font-semibold text-[11px] px-2.5 py-0.5 rounded-md border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300">
              High Protein
            </span>
            <span className="bg-amber-50 text-amber-800 font-semibold text-[11px] px-2.5 py-0.5 rounded-md border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300">
              Fresh
            </span>
          </div>

          {/* AI Reason Card */}
          <div className="bg-white/70 dark:bg-slate-800/70 rounded-xl p-3 mb-4 border border-slate-200/60 dark:border-slate-700/60 space-y-1">
            <p className="text-xs font-bold text-swiggy-600 dark:text-swiggy-400 flex items-center gap-1">
              <Sparkles className="h-3.5 w-3.5" /> Why this meal?
            </p>
            <p className="text-xs leading-relaxed text-slate-600 dark:text-slate-300 italic">
              "{item.reason || 'Fits your taste profile and complements your daily nutritional goals.'}"
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 pt-1">
          <button
            type="button"
            onClick={handleAdd}
            className={`flex-1 ${
              added ? 'bg-emerald-600' : 'bg-swiggy-500 hover:bg-swiggy-600'
            } text-white font-bold text-xs py-3 rounded-full transition-all shadow-md active:scale-95 flex items-center justify-center gap-1.5`}
          >
            {added ? <Check className="h-4 w-4" /> : null}
            <span>{added ? 'Added to Cart' : 'Add to Cart'}</span>
          </button>
          <button
            type="button"
            onClick={() => setShowWhyThis(!showWhyThis)}
            className="w-11 h-11 flex items-center justify-center bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors shrink-0"
            title="Detailed AI Analysis"
          >
            <HelpCircle className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Why This Glass Popover Overlay */}
      {showWhyThis && (
        <div className="absolute inset-0 z-30 glass-panel rounded-2xl p-5 flex flex-col justify-between animate-fadeIn bg-white/95 dark:bg-slate-900/95 border border-swiggy-500/30">
          <div className="flex justify-between items-start mb-2">
            <h4 className="font-serif font-bold text-sm text-swiggy-600 dark:text-swiggy-400 flex items-center gap-1.5">
              <Sparkles className="h-4 w-4" /> Comprehensive AI Analysis
            </h4>
            <button
              type="button"
              onClick={() => setShowWhyThis(false)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="space-y-2 text-xs text-slate-600 dark:text-slate-300">
            <p className="italic leading-relaxed">
              "{item.reason || 'Selected based on your preference for fresh, protein-rich gourmet dishes within budget.'}"
            </p>
            <div className="space-y-1.5 pt-2 text-[11px]">
              <div className="flex items-center justify-between">
                <span className="font-medium text-emerald-600">✓ Budget Friendly</span>
                <span className="font-bold text-slate-900 dark:text-slate-100">Under ₹{price + 100}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium text-emerald-600">✓ High Protein</span>
                <span className="font-bold text-slate-900 dark:text-slate-100">~28g / serving</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium text-emerald-600">✓ Express Delivery</span>
                <span className="font-bold text-slate-900 dark:text-slate-100">{deliveryTime}</span>
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={handleAdd}
            className="w-full bg-swiggy-500 hover:bg-swiggy-600 text-white font-bold text-xs py-2.5 rounded-full transition-colors mt-2"
          >
            Add Dish to Cart
          </button>
        </div>
      )}
    </div>
  )
}

export default RecommendationCard
