import React from 'react'
import { Bot, Calendar, Utensils, ShoppingBag } from 'lucide-react'
import RichRecommendationMessage from './RichRecommendationMessage'
import PlannerMessage from './PlannerMessage'
import CartMessage from './CartMessage'

export function AssistantMessage({ message, onSelectPrompt }) {
  const content = typeof message === 'string' ? message : message.content || message.text || ''
  const recommendations =
    message.recommendations ??
    message.data?.recommendations ??
    message.items ??
    null

  const planner =
    message.planner ??
    message.data?.meal_plan ??
    message.data?.planner ??
    message.meal_plan ??
    null

  const cartActionData =
    message.cart_data ??
    message.cart ??
    message.data?.cart ??
    null

  return (
    <div className="flex flex-col gap-3 my-4 w-full">
      {/* AI Bubble Header & Content */}
      <div className="flex items-end gap-4 max-w-[85%] w-full">
        <div className="w-10 h-10 rounded-full bg-swiggy-500/15 flex items-center justify-center shrink-0 shadow-sm border border-swiggy-500/20 text-swiggy-600">
          <Bot className="h-5 w-5" />
        </div>
        <div className="glass-panel ambient-shadow px-6 py-5 rounded-[24px] rounded-bl-[8px] text-base leading-relaxed text-slate-900 dark:text-slate-100 font-sans relative">
          <p className="whitespace-pre-wrap">{content}</p>

          {/* Embedded Action Cards */}
          {planner && (
            <PlannerMessage plan={planner} />
          )}

          {cartActionData && (
            <CartMessage cartActionData={cartActionData} />
          )}
        </div>
      </div>

      {/* Follow-up Intent Chips */}
      {onSelectPrompt && (
        <div className="flex flex-wrap gap-3 pl-14">
          <button
            type="button"
            onClick={() => onSelectPrompt('Create a 7 day meal plan')}
            className="bg-white dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700 px-4 py-2 rounded-full text-xs font-semibold text-slate-700 dark:text-slate-200 hover:text-swiggy-600 hover:border-swiggy-300 transition-all shadow-sm flex items-center gap-1.5"
          >
            <Calendar className="h-3.5 w-3.5" />
            Plan my week
          </button>
          <button
            type="button"
            onClick={() => onSelectPrompt('Suggest healthy lunch ideas under ₹300')}
            className="bg-white dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700 px-4 py-2 rounded-full text-xs font-semibold text-slate-700 dark:text-slate-200 hover:text-swiggy-600 hover:border-swiggy-300 transition-all shadow-sm flex items-center gap-1.5"
          >
            <Utensils className="h-3.5 w-3.5" />
            Find me dinner
          </button>
          <button
            type="button"
            onClick={() => onSelectPrompt('Show my cart')}
            className="bg-white dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700 px-4 py-2 rounded-full text-xs font-semibold text-slate-700 dark:text-slate-200 hover:text-swiggy-600 hover:border-swiggy-300 transition-all shadow-sm flex items-center gap-1.5"
          >
            <ShoppingBag className="h-3.5 w-3.5" />
            Check my cart
          </button>
        </div>
      )}
    </div>
  )
}

export default AssistantMessage
