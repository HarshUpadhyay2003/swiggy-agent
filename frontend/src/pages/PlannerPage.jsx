import React from 'react'
import Navbar from '../components/Shared/Navbar'
import WeeklyPlanner from '../components/Planner/WeeklyPlanner'
import ErrorBoundary from '../components/Shared/ErrorBoundary'
import { useAppActions, useAppState } from '../store/AppStore'

export function PlannerPage({ onNavigate, onOpenCart }) {
  const { planner, loadingStates } = useAppState()
  const { addToCart, sendChat } = useAppActions()

  const plannerLoading = loadingStates?.planner

  const handlePrompt = (text) => {
    sendChat(text)
  }

  return (
    <div className="min-h-screen relative overflow-x-hidden bg-gourmet-surface text-gourmet-on-surface dark:bg-slate-950 dark:text-slate-100 transition-colors duration-300 font-sans">
      {/* Background Ambient Blobs */}
      <div className="fixed top-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-swiggy-500/5 blur-[120px] pointer-events-none z-0" />
      <div className="fixed bottom-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-emerald-500/5 blur-[100px] pointer-events-none z-0" />

      {/* Top App Bar */}
      <Navbar currentPath="/planner" onNavigate={onNavigate} onOpenCart={onOpenCart} />

      {/* Main Content Canvas */}
      <main className="relative z-10 w-full max-w-[1440px] mx-auto px-4 md:px-8 pt-4 pb-16">
        <ErrorBoundary>
          <WeeklyPlanner
            planner={planner}
            loading={plannerLoading}
            onAddMeal={(meal) => addToCart(meal, 1)}
            onSelectPrompt={handlePrompt}
          />
        </ErrorBoundary>
      </main>
    </div>
  )
}

export default PlannerPage
