/**
 * Empty state components for various UI sections
 */

import { ShoppingCart, MessageCircle, Calendar, AlertCircle, Wifi, Clock } from 'lucide-react'

export function EmptyCart() {
  return (
    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-8 text-center dark:border-slate-700 dark:bg-slate-900">
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
        <ShoppingCart className="h-8 w-8 text-slate-400 dark:text-slate-600" />
      </div>
      <h3 className="mt-4 text-lg font-semibold text-slate-900 dark:text-slate-100">Cart is empty</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">
        Add items from recommendations or ask the assistant to help you find meals.
      </p>
    </div>
  )
}

export function NoRecommendations() {
  return (
    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-8 text-center dark:border-slate-700 dark:bg-slate-900">
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
        <Wifi className="h-8 w-8 text-slate-400 dark:text-slate-600" />
      </div>
      <h3 className="mt-4 text-lg font-semibold text-slate-900 dark:text-slate-100">No recommendations yet</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">
        Ask the assistant for meal recommendations, meal plans, or dietary preferences.
      </p>
    </div>
  )
}

export function NoPlanAvailable() {
  return (
    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 text-center dark:border-slate-700 dark:bg-slate-900">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800">
        <Calendar className="h-6 w-6 text-slate-400 dark:text-slate-600" />
      </div>
      <h3 className="mt-3 text-base font-semibold text-slate-900 dark:text-slate-100">No meal plan</h3>
      <p className="mt-1 text-xs leading-5 text-slate-600 dark:text-slate-400">
        Request a plan or ask for weekly meal suggestions.
      </p>
    </div>
  )
}

export function ConversationNotStarted() {
  return (
    <div className="rounded-[28px] bg-slate-100 px-5 py-4 shadow-sm dark:bg-slate-900">
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-200 dark:bg-slate-800">
          <MessageCircle className="h-5 w-5 text-slate-500 dark:text-slate-400" />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">Welcome to AI Commerce Copilot</p>
          <p className="mt-1 text-xs text-slate-600 dark:text-slate-400">
            Start a conversation by asking for recommendations, meal plans, or help with your order.
          </p>
        </div>
      </div>
    </div>
  )
}

export function SessionExpired() {
  return (
    <div className="rounded-3xl border border-amber-200 bg-amber-50 p-6 shadow-sm dark:border-amber-900 dark:bg-amber-950">
      <div className="flex items-start gap-3">
        <Clock className="h-6 w-6 flex-shrink-0 text-amber-600 dark:text-amber-400" />
        <div>
          <h3 className="text-sm font-semibold text-amber-900 dark:text-amber-100">Session expired</h3>
          <p className="mt-1 text-sm text-amber-700 dark:text-amber-200">
            Your session has expired. Refresh the page to start a new conversation.
          </p>
        </div>
      </div>
    </div>
  )
}

export function NetworkUnavailable() {
  return (
    <div className="rounded-3xl border border-rose-200 bg-rose-50 p-6 shadow-sm dark:border-rose-900 dark:bg-rose-950">
      <div className="flex items-start gap-3">
        <AlertCircle className="h-6 w-6 flex-shrink-0 text-rose-600 dark:text-rose-400" />
        <div>
          <h3 className="text-sm font-semibold text-rose-900 dark:text-rose-100">Backend unavailable</h3>
          <p className="mt-1 text-sm text-rose-700 dark:text-rose-200">
            Unable to connect to the server. Please check your connection and try again.
          </p>
        </div>
      </div>
    </div>
  )
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="rounded-3xl border border-rose-200 bg-rose-50 p-6 shadow-sm dark:border-rose-900 dark:bg-rose-950">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 flex-1">
          <AlertCircle className="h-6 w-6 flex-shrink-0 text-rose-600 dark:text-rose-400 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-rose-900 dark:text-rose-100">Something went wrong</h3>
            <p className="mt-1 text-sm text-rose-700 dark:text-rose-200">{message || 'An unexpected error occurred.'}</p>
          </div>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex-shrink-0 rounded-full bg-rose-600 px-3 py-2 text-xs font-semibold text-white hover:bg-rose-700 transition"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  )
}
