import React, { useState } from 'react'
import { Sparkles, Trash2, HelpCircle, Check, ShoppingBag, X } from 'lucide-react'
import { getFoodImage } from '../../assets/images'

export function MealCard({ meal, mealType = 'Breakfast', onAdd, onReplace, onRemove, index = 0 }) {
  const [showWhyThis, setShowWhyThis] = useState(false)
  const [added, setAdded] = useState(false)

  if (!meal) return null

  const name = meal.name || meal.title || 'Curated Meal'
  const price = meal.price ?? meal.estimated_cost ?? 350
  const restaurant = meal.restaurant_name || meal.brand || 'Gourmet Kitchen'

  const imgUrl = meal.image_url || getFoodImage(name, index)

  const handleAdd = (e) => {
    e?.stopPropagation()
    onAdd && onAdd(meal)
    setAdded(true)
    setTimeout(() => setAdded(false), 1800)
  }

  return (
    <div className="glass-card rounded-2xl overflow-hidden relative group border border-white/60 dark:border-slate-800 shadow-sm hover:shadow-md transition-all duration-300">
      {/* 'Why This' button top-left */}
      <div className="absolute top-3 left-3 z-10">
        <button
          type="button"
          onClick={() => setShowWhyThis(!showWhyThis)}
          className="bg-swiggy-500 hover:bg-swiggy-600 text-white rounded-full p-1.5 shadow-sm hover:scale-105 transition-transform flex items-center justify-center"
          title="Why this meal?"
        >
          <HelpCircle className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Image Area */}
      <div className="h-36 relative overflow-hidden bg-slate-100 dark:bg-slate-800">
        <img
          src={imgUrl}
          alt={name}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          loading="lazy"
          onError={(e) => {
            e.target.onerror = null
            e.target.src = getFoodImage(name, index)
          }}
        />
        {/* Price Tag Pill */}
        <div className="absolute top-3 right-3 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md px-3 py-1 rounded-full text-xs font-bold text-slate-900 dark:text-slate-100 shadow-sm">
          ₹{price}
        </div>
      </div>

      {/* Body Content */}
      <div className="p-4 bg-white/40 dark:bg-slate-900/40 flex flex-col justify-between space-y-3">
        <div>
          <div className="text-[11px] font-bold text-swiggy-600 dark:text-swiggy-400 uppercase tracking-wider mb-1">
            {mealType}
          </div>
          <h3 className="font-serif font-bold text-base leading-tight text-slate-900 dark:text-slate-100 truncate">
            {name}
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 font-medium truncate mt-0.5">
            {restaurant}
          </p>
        </div>

        {/* AI Rationale Quote */}
        <div className="bg-white/60 dark:bg-slate-800/60 rounded-xl p-2.5 border border-slate-200/50 dark:border-slate-700/50">
          <p className="text-[11px] leading-relaxed text-slate-600 dark:text-slate-300 italic line-clamp-2">
            "{meal.reason || `Nutritious ${mealType.toLowerCase()} choice matching your protein goal.`}"
          </p>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between border-t border-slate-200/50 dark:border-slate-800 pt-3 gap-2">
          <button
            type="button"
            onClick={() => onReplace && onReplace(meal)}
            className="text-slate-400 hover:text-swiggy-500 transition-colors p-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800"
            title="Replace meal (AI)"
          >
            <Sparkles className="h-4 w-4" />
          </button>

          <button
            type="button"
            onClick={handleAdd}
            className={`flex-1 px-3 py-1.5 rounded-full text-xs font-bold ${
              added ? 'bg-emerald-600 text-white' : 'bg-swiggy-500 hover:bg-swiggy-600 text-white'
            } transition-colors flex items-center justify-center gap-1 shadow-sm`}
          >
            {added ? <Check className="h-3.5 w-3.5" /> : <ShoppingBag className="h-3.5 w-3.5" />}
            <span>{added ? 'Added' : 'Add to cart'}</span>
          </button>

          <button
            type="button"
            onClick={() => onRemove && onRemove(meal)}
            className="text-slate-400 hover:text-rose-500 transition-colors p-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800"
            title="Remove meal"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* 'Why This' Glass Popover Overlay */}
      {showWhyThis && (
        <div className="absolute inset-0 z-30 glass-panel rounded-2xl p-4 flex flex-col justify-between animate-fadeIn bg-white/95 dark:bg-slate-900/95 border border-swiggy-500/30">
          <div className="flex justify-between items-start mb-1">
            <h4 className="font-semibold text-xs text-swiggy-600 dark:text-swiggy-400 flex items-center gap-1 font-serif">
              <Sparkles className="h-3.5 w-3.5" /> AI Match Analysis
            </h4>
            <button
              type="button"
              onClick={() => setShowWhyThis(false)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <p className="text-xs leading-relaxed text-slate-600 dark:text-slate-300 italic mb-2">
            "{meal.reason || `We selected ${name} to maintain optimal calorie distribution for ${mealType.toLowerCase()}.`}"
          </p>
          <div className="space-y-1.5 text-[10px] text-slate-500 dark:text-slate-400">
            <div>
              <div className="flex justify-between mb-0.5 font-bold uppercase">
                <span>Budget Match</span>
                <span className="text-emerald-600">95%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 w-[95%] rounded-full" />
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-0.5 font-bold uppercase">
                <span>Health Score</span>
                <span className="text-emerald-600">88%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 w-[88%] rounded-full" />
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-0.5 font-bold uppercase">
                <span>Protein Focus</span>
                <span className="text-swiggy-500">High</span>
              </div>
              <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-swiggy-500 w-[82%] rounded-full" />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MealCard
