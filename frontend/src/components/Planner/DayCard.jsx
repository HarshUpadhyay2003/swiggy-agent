import React, { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import MealCard from './MealCard'

export function DayCard({ dayData, dayName = 'Monday', onAddMeal, onReplaceMeal, onRemoveMeal, dayIndex = 0 }) {
  const [isExpanded, setIsExpanded] = useState(dayIndex === 0)

  if (!dayData) return null

  const breakfast = dayData.breakfast || dayData.meals?.[0]
  const lunch = dayData.lunch || dayData.meals?.[1]
  const dinner = dayData.dinner || dayData.meals?.[2]

  const totalCost = dayData.total_cost || ((breakfast?.price || 350) + (lunch?.price || 450) + (dinner?.price || 450))
  const totalCalories = dayData.total_calories || ((breakfast?.calories || 450) + (lunch?.calories || 650) + (dinner?.calories || 700))

  return (
    <div
      id={`day-card-${dayIndex}`}
      className="w-full sm:w-[320px] flex flex-col space-y-4 shrink-0 snap-start transition-all duration-300"
    >
      {/* Sticky Day Column Header */}
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="sticky top-16 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md z-20 py-2.5 px-3 rounded-xl border border-slate-200/80 dark:border-slate-800 shadow-sm cursor-pointer flex justify-between items-center group"
      >
        <div>
          <h2 className="font-serif text-xl font-bold text-slate-900 dark:text-slate-100 group-hover:text-swiggy-500 transition-colors">
            {dayName}
          </h2>
          <div className="flex justify-between items-center gap-3 mt-0.5 text-xs font-semibold text-slate-500 dark:text-slate-400">
            <span className="text-slate-900 dark:text-slate-100 font-bold">₹{totalCost}</span>
            <span>•</span>
            <span>{totalCalories} Cal</span>
          </div>
        </div>

        <button
          type="button"
          className="p-1 rounded-full text-slate-400 group-hover:text-swiggy-500 transition-colors"
        >
          {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
        </button>
      </div>

      {/* Meals Container */}
      {isExpanded && (
        <div className="space-y-4 animate-fadeIn">
          {/* Breakfast Meal */}
          {breakfast && (
            <MealCard
              meal={breakfast}
              mealType="Breakfast"
              onAdd={onAddMeal}
              onReplace={onReplaceMeal}
              onRemove={onRemoveMeal}
              index={dayIndex * 3 + 0}
            />
          )}

          {/* Lunch Meal */}
          {lunch && (
            <MealCard
              meal={lunch}
              mealType="Lunch"
              onAdd={onAddMeal}
              onReplace={onReplaceMeal}
              onRemove={onRemoveMeal}
              index={dayIndex * 3 + 1}
            />
          )}

          {/* Dinner Meal */}
          {dinner && (
            <MealCard
              meal={dinner}
              mealType="Dinner"
              onAdd={onAddMeal}
              onReplace={onReplaceMeal}
              onRemove={onRemoveMeal}
              index={dayIndex * 3 + 2}
            />
          )}
        </div>
      )}
    </div>
  )
}

export default DayCard
