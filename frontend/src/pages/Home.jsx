import { useState } from 'react'
import { Bolt, Sparkles } from 'lucide-react'
import Navbar from '../components/Shared/Navbar'
import ChatWindow from '../components/Chat/ChatWindow'
import ChatInput from '../components/Chat/ChatInput'
import CartPanel from '../components/Cart/CartPanel'
import MealPlanCard from '../components/MealPlan/MealPlanCard'
import RecommendationList from '../components/Cards/RecommendationList'
import QuickPrompts from '../components/Shared/QuickPrompts'
import { ConversationNotStarted, ErrorState, NetworkUnavailable, SessionExpired } from '../components/Shared/EmptyStates'
import ErrorBoundary from '../components/Shared/ErrorBoundary'
import { useAppActions, useAppState } from '../store/AppStore'

const quickOptions = [
  'Healthy lunch',
  'Cheap comfort food',
  'High protein meals',
  'Weekly meal plan',
  'Show my cart',
  'Checkout',
  'Track order',
  'Veg dinner',
  'Non-veg under 200',
]

function Home() {
  const [inputValue, setInputValue] = useState('')
  const { messages, loading, recommendations, cart, planner, typing, error, loadingStates } = useAppState()
  const { sendChat, addToCart, checkout, removeRecommendation, replaceRecommendation, syncCart } = useAppActions()

  const isSessionRestoring = loadingStates?.sessionRestore
  const recommendationLoading = loadingStates?.recommendations
  const plannerLoading = loadingStates?.planner
  const cartLoading = loadingStates?.cart
  const hasUserStarted = messages.some((message) => message.author === 'user')
  const showSessionExpired = /session.*expired|expired session/i.test(error || '')
  const showNetworkUnavailable = /network|timeout|backend unavailable|failed to connect|server unavailable/i.test(error || '')

  const handleSend = async (text) => {
    if (!text?.trim() || loading) return
    setInputValue('')
    await sendChat(text.trim())
  }

  const handlePrompt = (promptText) => {
    setInputValue(promptText)
    handleSend(promptText)
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto w-[95vw] max-w-[95vw] px-4 py-6 sm:px-6 lg:px-8">
        <Navbar />

        <div className="mt-6 space-y-6">
          <section className="rounded-3xl border border-slate-200 bg-white/90 p-6 shadow-sm shadow-slate-200/50 backdrop-blur dark:border-slate-700/70 dark:bg-slate-900/80">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-brand-600">AI Commerce Copilot</p>
                <h1 className="mt-3 text-3xl font-semibold text-slate-950 dark:text-slate-100">Customer conversation workspace</h1>
                <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">
                  A responsive assistant interface for conversational commerce with live chat, planner, cart, and recommendations.
                </p>
              </div>

              <div className="flex items-center gap-3 rounded-2xl bg-brand-50 px-4 py-3 text-sm text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                <Bolt className="h-5 w-5 text-brand-600" />
                <span>Modern, AI-native commerce experience.</span>
              </div>
            </div>
          </section>

          {isSessionRestoring ? (
            <div className="rounded-3xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900 shadow-sm dark:border-amber-900 dark:bg-amber-950 dark:text-amber-100">
              Restoring your session and cart state. Your conversation and saved items are being recovered.
            </div>
          ) : null}

          {showSessionExpired ? (
            <SessionExpired />
          ) : showNetworkUnavailable ? (
            <NetworkUnavailable />
          ) : error ? (
            <ErrorState message={error} onRetry={syncCart} />
          ) : null}

          <div className="grid gap-6 xl:grid-cols-[70%_30%]">
            <div className="space-y-6">
              <QuickPrompts options={quickOptions} onSelect={handlePrompt} />

              <ErrorBoundary>
                <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-200/50 dark:border-slate-700/70 dark:bg-slate-950">
                <div className="mb-4 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Live assistant</p>
                    <h2 className="mt-1 text-xl font-semibold text-slate-950 dark:text-slate-100">Customer chat</h2>
                  </div>
                  <div className="inline-flex items-center gap-2 rounded-2xl bg-slate-100 px-3 py-2 text-sm text-slate-700 dark:bg-slate-900 dark:text-slate-200">
                    <Sparkles className="h-4 w-4 text-amber-500" /> AI ready
                  </div>
                </div>

                <ChatWindow messages={messages} typing={typing} />
                {!hasUserStarted && !typing ? (
                  <div className="mt-5 rounded-3xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
                    <ConversationNotStarted />
                  </div>
                ) : null}
                <ChatInput value={inputValue} onChange={setInputValue} onSend={handleSend} disabled={loading} />
              </div>
              </ErrorBoundary>

              <ErrorBoundary>
                <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-200/40 dark:border-slate-700/70 dark:bg-slate-900">
                <h3 className="mb-3 text-sm font-semibold text-slate-900 dark:text-slate-100">Recommendations</h3>
                <RecommendationList
                  items={recommendations}
                  loading={recommendationLoading}
                  onAdd={addToCart}
                  onRemove={removeRecommendation}
                  onReplace={replaceRecommendation}
                />
              </div>
              </ErrorBoundary>

              {plannerLoading ? (
                <div className="mt-4 rounded-3xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600 shadow-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
                  Generating your updated meal plan…
                </div>
              ) : null}

              {error ? (
                <div className="rounded-3xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 shadow-sm shadow-rose-100">
                  {error}
                </div>
              ) : null}
            </div>

            <div className="space-y-6">
              <ErrorBoundary>
                <CartPanel />
              </ErrorBoundary>
              <ErrorBoundary>
                <MealPlanCard />
              </ErrorBoundary>
            </div>
          </div>
        </div>
      </div>
      </div>

      <div className="fixed bottom-4 left-4 right-4 z-30 block md:hidden">
        <div className="rounded-3xl border border-slate-200 bg-white/95 p-4 shadow-soft backdrop-blur-xl dark:border-slate-700/70 dark:bg-slate-950/95">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">Cart summary</p>
              <p className="mt-1 text-lg font-semibold text-slate-900 dark:text-slate-100">₹{cart.total ?? 0}</p>
            </div>
            <button
              type="button"
              onClick={checkout}
              disabled={!cart.items?.length || loading}
              className="rounded-3xl bg-swiggy-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-swiggy-600 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Checkout
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
