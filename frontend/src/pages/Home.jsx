import React, { useState, useEffect } from 'react'
import { Compass, Calendar, ArrowRight } from 'lucide-react'
import Navbar from '../components/Shared/Navbar'
import LandingHero from '../components/hero/LandingHero'
import ConversationView from '../components/Chat/ConversationView'
import RecommendationGrid from '../components/Recommendation/RecommendationGrid'
import StickyComposer from '../components/Chat/StickyComposer'
import { ErrorState, NetworkUnavailable, SessionExpired } from '../components/Shared/EmptyStates'
import ErrorBoundary from '../components/Shared/ErrorBoundary'
import { useAppActions, useAppState } from '../store/AppStore'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'

export function Home({ onNavigate, onOpenCart }) {
  const [inputValue, setInputValue] = useState('')
  const [hasUserStartedChat, setHasUserStartedChat] = useState(false)
  const { messages, loading, recommendations, error, loadingStates } = useAppState()
  const { sendChat, addToCart, removeRecommendation, replaceRecommendation, syncCart, requestMealPlan } = useAppActions()

  const isSessionRestoring = loadingStates?.sessionRestore
  const recommendationLoading = loadingStates?.recommendations
  const plannerLoading = loadingStates?.planner
  const showSessionExpired = /session.*expired|expired session/i.test(error || '')
  const showNetworkUnavailable = /network|timeout|backend unavailable|failed to connect|server unavailable/i.test(error || '')

  // Conversation starts only when user explicitly sends a prompt or has >1 messages in history
  const isConversationStarted = hasUserStartedChat || (messages && messages.length > 1)

  // Ensure fresh page load starts strictly at Hero (window.scrollY = 0)
  useEffect(() => {
    if (!isConversationStarted) {
      window.scrollTo(0, 0)
    }
  }, [isConversationStarted])

  const handleSend = async (text) => {
    if (!text?.trim() || loading) return
    setHasUserStartedChat(true)
    setInputValue('')
    const res = await sendChat(text.trim())
    const data = res?.data ?? res ?? {}
    if (data.meal_plan || data.planner || res?.meal_plan || res?.planner) {
      onNavigate && onNavigate('/planner')
    }
  }

  const handlePrompt = (promptText) => {
    setHasUserStartedChat(true)
    setInputValue(promptText)
    handleSend(promptText)
  }

  const handleGeneratePlan = async () => {
    setHasUserStartedChat(true)
    await requestMealPlan()
    onNavigate && onNavigate('/planner')
  }

  return (
    <div className="min-h-screen relative overflow-x-hidden bg-gourmet-surface text-gourmet-on-surface dark:bg-slate-950 dark:text-slate-100 transition-colors duration-300 font-sans pb-16">
      {/* Background Ambient Blobs */}
      <div className="fixed top-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-swiggy-500/5 blur-[120px] pointer-events-none z-0" />
      <div className="fixed bottom-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-emerald-500/5 blur-[100px] pointer-events-none z-0" />

      {/* Top App Bar */}
      <Navbar currentPath="/" onNavigate={onNavigate} onOpenCart={onOpenCart} />

      {/* Main Content Canvas */}
      <main className="relative z-10 w-full max-w-[1200px] mx-auto px-5 md:px-[64px] pt-[20px] md:pt-[30px] flex flex-col items-center">
        {/* Hero Section (Collapses smoothly after user sends first message) */}
        <LandingHero
          inputValue={inputValue}
          onChangeInput={setInputValue}
          onSendInput={handleSend}
          onSelectPrompt={handlePrompt}
          collapsed={isConversationStarted}
        />

        {/* Status Alerts */}
        <div className="w-full max-w-3xl space-y-4 mb-4">
          {isSessionRestoring && (
            <Card variant="glass" className="border-amber-200 bg-amber-50/80 text-amber-900 dark:border-amber-900/60 dark:bg-amber-950/60 dark:text-amber-200">
              <p className="text-sm font-medium text-center">
                Restoring your active session and cart state…
              </p>
            </Card>
          )}

          {showSessionExpired ? (
            <SessionExpired />
          ) : showNetworkUnavailable ? (
            <NetworkUnavailable />
          ) : error ? (
            <ErrorState message={error} onRetry={syncCart} />
          ) : null}
        </div>

        {/* AI Conversation Workspace Section */}
        <section className="w-full max-w-3xl mx-auto flex flex-col items-start gap-[24px] mb-2">
          <ErrorBoundary>
            <div className="w-full">
              <ConversationView
                messages={messages}
                typing={loading}
                onSelectPrompt={handlePrompt}
              />
            </div>
          </ErrorBoundary>
        </section>

        {/* Sticky Chat Composer (Positioned directly beneath Conversation Workspace) */}
        {isConversationStarted && (
          <StickyComposer onSend={handleSend} loading={loading} />
        )}

        {/* Recommendations Marketplace Section (Positioned below Conversation & Composer) */}
        <section className="w-full max-w-[1200px] mb-10 mt-6 animate-fadeIn">
          <ErrorBoundary>
            <div className="mb-4 flex items-center justify-between px-1">
              <div className="flex items-center gap-2">
                <Compass className="h-5 w-5 text-swiggy-500" />
                <h2 className="font-serif text-xl md:text-2xl font-bold text-slate-900 dark:text-slate-100">
                  Curated Culinary Marketplace
                </h2>
              </div>
              <Badge variant="primary" size="sm">
                AI Filtered
              </Badge>
            </div>

            <RecommendationGrid
              items={recommendations}
              loading={recommendationLoading}
              onAdd={addToCart}
              onRemove={removeRecommendation}
              onReplace={replaceRecommendation}
              onSelectPrompt={handlePrompt}
            />
          </ErrorBoundary>
        </section>

        {/* Generate Weekly Meal Plan CTA Card */}
        <section className="w-full max-w-[1200px] mb-8 animate-fadeIn">
          <div className="glass-panel rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-6 ambient-shadow border border-white/60 dark:border-slate-800">
            <div className="flex items-center gap-4 text-left">
              <div className="w-14 h-14 rounded-2xl bg-swiggy-500/15 text-swiggy-600 dark:text-swiggy-400 flex items-center justify-center shrink-0">
                <Calendar className="h-7 w-7" />
              </div>
              <div>
                <h3 className="font-serif text-2xl font-bold text-slate-900 dark:text-slate-100 mb-1">
                  Create Weekly Meal Plan
                </h3>
                <p className="text-sm text-slate-600 dark:text-slate-300 font-sans">
                  Generate a personalized 7-day dining schedule optimized for taste, health, and budget.
                </p>
              </div>
            </div>

            <button
              type="button"
              disabled={plannerLoading}
              onClick={handleGeneratePlan}
              className="bg-swiggy-500 hover:bg-swiggy-600 text-white px-6 py-3.5 rounded-full font-bold text-sm shadow-md transition-all flex items-center gap-2 shrink-0 disabled:opacity-60 active:scale-95"
            >
              <span>{plannerLoading ? 'Generating Plan...' : 'Generate Plan'}</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </section>
      </main>
    </div>
  )
}

export default Home
