import React from 'react'
import { useAppActions, useAppState } from '../../store/AppStore'
import WeeklyPlanner from '../Planner/WeeklyPlanner'

function MealPlanCard() {
  const { planner, loadingStates } = useAppState()
  const { addToCart, sendChat } = useAppActions()

  const plannerLoading = loadingStates?.planner

  const handlePrompt = (text) => {
    sendChat(text)
  }

  return (
    <WeeklyPlanner
      planner={planner}
      loading={plannerLoading}
      onAddMeal={(meal) => addToCart(meal, 1)}
      onSelectPrompt={handlePrompt}
    />
  )
}

export default MealPlanCard
