import React, { useState, useRef } from 'react'
import WeeklySummaryHero from './WeeklySummaryHero'
import StickyPlannerBar from './StickyPlannerBar'
import DaySelector from './DaySelector'
import PlannerProgress from './PlannerProgress'
import DayCard from './DayCard'
import PlannerBottomStats from './PlannerBottomStats'
import PlannerEmptyState from './PlannerEmptyState'
import PlannerSkeleton from './PlannerSkeleton'
import { normalizePlanner } from '../../utils/plannerAdapter'

export function WeeklyPlanner({ planner = null, plan = null, loading = false, onAddMeal, onReplaceMeal, onRemoveMeal, onSelectPrompt }) {
  const [activeDayIndex, setActiveDayIndex] = useState(0)
  const scrollContainerRef = useRef(null)

  const normalized = normalizePlanner(planner || plan)

  if (loading) {
    return <PlannerSkeleton />
  }

  const days = normalized?.days || []

  if (!normalized || days.length === 0) {
    return <PlannerEmptyState onSelectPrompt={onSelectPrompt} />
  }

  const handleSelectDay = (index) => {
    setActiveDayIndex(index)
    if (scrollContainerRef.current) {
      const targetCard = scrollContainerRef.current.querySelector(`#day-card-${index}`)
      if (targetCard) {
        targetCard.scrollIntoView({ behavior: 'smooth', inline: 'start', block: 'nearest' })
      }
    }
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
    <div className="w-full max-w-[1440px] mx-auto pt-2">
      {/* 1. Weekly Summary Hero */}
      <WeeklySummaryHero normalizedPlanner={normalized} />

      {/* 2. Scroll-triggered Sticky Summary Bar */}
      <StickyPlannerBar
        normalizedPlanner={normalized}
        onAddAllToCart={handleAddAllToCart}
        onMakeHealthier={handleMakeHealthier}
        onOptimizeBudget={handleOptimizeBudget}
      />

      {/* 3. Planner Progress Bar */}
      <PlannerProgress days={days} />

      {/* 4. Day Navigation Selector */}
      <DaySelector days={days} activeDayIndex={activeDayIndex} onSelectDay={handleSelectDay} />

      {/* 5. Horizontal Snap-Scrollable 7-Day Matrix */}
      <div
        ref={scrollContainerRef}
        className="overflow-x-auto scrollbar-thin pb-8 -mx-4 px-4 md:mx-0 md:px-0 snap-x snap-mandatory flex space-x-6"
      >
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

      {/* 6. Planner Bottom Statistics */}
      <PlannerBottomStats normalizedPlanner={normalized} />
    </div>
  )
}

export default WeeklyPlanner
