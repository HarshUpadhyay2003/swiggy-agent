import React from 'react'
import MealCard from './MealCard'

export function DayCard({ dayData, dayName = 'Monday', onAddMeal, onReplaceMeal, onRemoveMeal, dayIndex = 0 }) {
  if (!dayData) return null

  const breakfast = dayData.breakfast || dayData.meals?.[0]
  const lunch = dayData.lunch || dayData.meals?.[1]
  const dinner = dayData.dinner || dayData.meals?.[2]

  const totalCost = dayData.total_cost || ((breakfast?.price || 350) + (lunch?.price || 450) + (dinner?.price || 450))
  const totalCalories = dayData.total_calories || ((breakfast?.calories || 450) + (lunch?.calories || 650) + (dinner?.calories || 700))

  return (
    <div className="w-full sm:w-[320px] flex flex-col space-y-4 shrink-0">
      {/* Sticky Day Header */}
      <div className="sticky top-16 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md z-20 py-2 border-b border-slate-200/80 dark:border-slate-800">
        <h2 className="font-serif text-2xl font-bold text-slate-900 dark:text-slate-100">
          {dayName}
        </h2>
        <div className="flex justify-between mt-1 text-xs font-semibold text-slate-500 dark:text-slate-400">
          <span>₹{totalCost}</span>
          <span>{totalCalories} Cal</span>
        </div>
      </div>

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
  )
}

export default DayCard
