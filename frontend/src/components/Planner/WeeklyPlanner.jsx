import React from 'react'
import { Calendar } from 'lucide-react'
import PlannerHeader from './PlannerHeader'
import DayCard from './DayCard'
import PlannerSkeleton from './PlannerSkeleton'
import Chip from '../ui/Chip'
import { normalizePlanner } from '../../utils/plannerAdapter'

export function WeeklyPlanner({ planner = null, plan = null, loading = false, onAddMeal, onReplaceMeal, onRemoveMeal, onSelectPrompt }) {
  const promptChips = [
    'Healthy Week',
    'Weight Loss',
    'High Protein',
    'Vegetarian',
    'Family Meals',
    'Budget Meals',
  ]

  const normalized = normalizePlanner(planner || plan)

  if (loading) {
    return <PlannerSkeleton />
  }

  const days = normalized?.days || []

  if (!normalized || days.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-8 flex flex-col items-center justify-center text-center space-y-4 ambient-shadow">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-swiggy-500/15 text-swiggy-600 dark:text-swiggy-400">
          <Calendar className="h-7 w-7" />
        </div>

        <div className="space-y-1.5 max-w-md">
          <h3 className="font-serif font-bold text-2xl text-slate-900 dark:text-slate-100">
            Create your weekly meal plan
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed font-sans">
            Let CraveAI curate a 7-day dining schedule tailored to your health goals, macros, and weekly budget.
          </p>
        </div>

        {onSelectPrompt && (
          <div className="flex flex-wrap justify-center gap-2 pt-2">
            {promptChips.map((chip) => (
              <Chip
                key={chip}
                variant="default"
                size="sm"
                onClick={() => onSelectPrompt(`Create a ${chip.toLowerCase()} 7 day meal plan`)}
              >
                {chip}
              </Chip>
            ))}
          </div>
        )}
      </div>
    )
  }

  const handleAddAllToCart = () => {
    days.forEach((dayData) => {
      const meals = [dayData.breakfast, dayData.lunch, dayData.dinner, ...(dayData.meals || [])].filter(Boolean)
      meals.forEach((meal) => onAddMeal && onAddMeal(meal))
    })
  }

  const handleMakeHealthier = () => {
    onSelectPrompt && onSelectPrompt('Modify my current meal plan to make it lower calorie and healthier')
  }

  const handleOptimizeBudget = () => {
    onSelectPrompt && onSelectPrompt('Optimize my current meal plan to fit a lower budget under ₹2000')
  }

  return (
    <div className="w-full max-w-[1440px] mx-auto pt-4">
      {/* Header & Global Actions */}
      <PlannerHeader
        onAddAllToCart={handleAddAllToCart}
        onMakeHealthier={handleMakeHealthier}
        onOptimizeBudget={handleOptimizeBudget}
      />

      {/* Horizontal Scrollable Weekly View */}
      <div className="overflow-x-auto scrollbar-thin pb-8 -mx-4 px-4 md:mx-0 md:px-0">
        <div className="flex space-x-6 min-w-max">
          {days.map((dayData, idx) => (
            <DayCard
              key={dayData.day || idx}
              dayName={dayData.day}
              dayData={dayData}
              dayIndex={idx}
              onAddMeal={onAddMeal}
              onReplaceMeal={onReplaceMeal}
              onRemoveMeal={onRemoveMeal}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export default WeeklyPlanner
