import React, { useState } from 'react'
import { Sparkles, X, HelpCircle, Check, ShoppingBag } from 'lucide-react'
import { foodImages } from '../../assets/images'

export function MealCard({ meal, mealType = 'Breakfast', onAdd, onReplace, onRemove, index = 0 }) {
  const [showWhyThis, setShowWhyThis] = useState(false)
  const [added, setAdded] = useState(false)

  if (!meal) return null

  const name = meal.name || meal.title || 'Curated Meal'
  const price = meal.price ?? meal.estimated_cost ?? 350
  const restaurant = meal.restaurant_name || meal.brand || 'Gourmet Cafe'

  // Image registry mapper
  const getRegistryImage = () => {
    if (meal.image_url) return meal.image_url
    const keys = Object.keys(foodImages)
    if (!name) return foodImages[keys[index % keys.length]]
    const lower = name.toLowerCase()
    if (lower.includes('avocado') || lower.includes('toast') || lower.includes('egg') || lower.includes('breakfast')) return foodImages.avocadoToast
    if (lower.includes('salad') || lower.includes('greek') || lower.includes('green')) return foodImages.greekSalad
    if (lower.includes('smoothie') || lower.includes('bowl') || lower.includes('berry')) return foodImages.smoothieBowl
    if (lower.includes('chicken') || lower.includes('grilled') || lower.includes('protein')) return foodImages.grilledChicken
    if (lower.includes('pizza') || lower.includes('margherita') || lower.includes('cheese')) return foodImages.margheritaPizza
    if (lower.includes('poke') || lower.includes('salmon') || lower.includes('fish')) return foodImages.pokeBowl
    return foodImages[keys[index % keys.length]]
  }

  const imgUrl = getRegistryImage()

  const handleAdd = (e) => {
    e?.stopPropagation()
    onAdd && onAdd(meal)
    setAdded(true)
    setTimeout(() => setAdded(false), 1800)
  }

  return (
    <div className="glass-card rounded-xl overflow-hidden relative group border border-white/60 dark:border-slate-800 transition-all duration-300">
      {/* 'Why This' button top-left */}
      <div className="absolute top-2 left-2 z-10">
        <button
          type="button"
          onClick={() => setShowWhyThis(!showWhyThis)}
          className="bg-swiggy-500 text-white rounded-full p-1.5 shadow-sm hover:scale-105 transition-transform flex items-center justify-center"
          title="Why this?"
        >
          <HelpCircle className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Image Area */}
      <div className="h-32 relative overflow-hidden bg-slate-100 dark:bg-slate-800">
        <img
          src={imgUrl}
          alt={name}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          loading="lazy"
          onError={(e) => {
            e.target.style.display = 'none'
          }}
        />
        {/* Price Pill */}
        <div className="absolute top-2 right-2 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm px-2.5 py-1 rounded-full text-xs font-bold text-slate-900 dark:text-slate-100 shadow-sm">
          ₹{price}
        </div>
      </div>

      {/* Body */}
      <div className="p-4 bg-white/40 dark:bg-slate-900/40">
        <div className="text-xs font-semibold text-swiggy-600 dark:text-swiggy-400 uppercase tracking-wider mb-1">
          {mealType}
        </div>
        <h3 className="font-serif font-bold text-base leading-tight text-slate-900 dark:text-slate-100 mb-1 truncate">
          {name}
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
          {restaurant}
        </p>

        {/* Footer Actions */}
        <div className="mt-4 flex items-center justify-between border-t border-slate-200/50 dark:border-slate-800 pt-3 gap-2">
          <button
            type="button"
            onClick={() => onReplace && onReplace(meal)}
            className="text-slate-400 hover:text-swiggy-500 transition-colors p-1"
            title="Replace (AI)"
          >
            <Sparkles className="h-4 w-4" />
          </button>

          <button
            type="button"
            onClick={handleAdd}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold ${
              added ? 'bg-emerald-600 text-white' : 'bg-swiggy-500 hover:bg-swiggy-600 text-white'
            } transition-colors flex items-center gap-1`}
          >
            {added ? <Check className="h-3.5 w-3.5" /> : <ShoppingBag className="h-3.5 w-3.5" />}
            <span>{added ? 'Added' : 'Add to cart'}</span>
          </button>

          <button
            type="button"
            onClick={() => onRemove && onRemove(meal)}
            className="text-slate-400 hover:text-rose-500 transition-colors p-1"
            title="Remove"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* 'Why This' Popup Overlay (Glassmorphic) */}
      {showWhyThis && (
        <div className="absolute inset-0 z-30 glass-panel rounded-xl p-4 flex flex-col justify-center animate-fadeIn bg-white/95 dark:bg-slate-900/95">
          <div className="flex justify-between items-start mb-2">
            <h4 className="font-semibold text-xs text-swiggy-600 dark:text-swiggy-400 flex items-center gap-1">
              <Sparkles className="h-3.5 w-3.5" /> AI Analysis
            </h4>
            <button
              type="button"
              onClick={() => setShowWhyThis(false)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <p className="text-xs leading-snug text-slate-600 dark:text-slate-300 mb-3 italic">
            "{meal.reason || `We chose this ${name} because it complements your nutritional balance and fits your daily budget.`}"
          </p>
          <div className="space-y-1.5 text-[10px] text-slate-500 dark:text-slate-400">
            <div>
              <div className="flex justify-between mb-0.5 uppercase">
                <span>Budget Match</span>
                <span className="font-bold text-emerald-600">95%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 w-[95%] rounded-full" />
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-0.5 uppercase">
                <span>Health Score</span>
                <span className="font-bold text-emerald-600">88%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 w-[88%] rounded-full" />
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-0.5 uppercase">
                <span>Protein Focus</span>
                <span className="font-bold text-swiggy-500">High</span>
              </div>
              <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-swiggy-500 w-[80%] rounded-full" />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MealCard
