import React, { useState, useEffect } from 'react'
import { Bot, Sparkles } from 'lucide-react'

export function TypingBubble() {
  const steps = [
    'Finding top rated dishes…',
    'Analysing weekly budget…',
    'Checking protein & calorie goals…',
    'Matching your taste preferences…',
  ]
  const [stepIndex, setStepIndex] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setStepIndex((prev) => (prev + 1) % steps.length)
    }, 1200)
    return () => clearInterval(timer)
  }, [steps.length])

  return (
    <div className="flex items-end gap-4 max-w-[85%] w-full my-4 animate-fadeIn">
      <div className="w-10 h-10 rounded-full bg-swiggy-500/15 flex items-center justify-center shrink-0 shadow-sm border border-swiggy-500/20 text-swiggy-600">
        <Bot className="h-5 w-5" />
      </div>

      <div className="glass-panel ambient-shadow px-5 py-4 rounded-[24px] rounded-bl-[8px] flex items-center gap-3 border border-swiggy-500/20">
        <div className="flex items-center gap-1.5 shrink-0">
          <span className="h-2.5 w-2.5 rounded-full bg-swiggy-500 animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="h-2.5 w-2.5 rounded-full bg-swiggy-500 animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="h-2.5 w-2.5 rounded-full bg-swiggy-500 animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
        <div className="flex items-center gap-1.5 text-xs font-semibold text-swiggy-600 dark:text-swiggy-400 font-sans transition-all duration-300">
          <Sparkles className="h-3.5 w-3.5 animate-spin" style={{ animationDuration: '3s' }} />
          <span>{steps[stepIndex]}</span>
        </div>
      </div>
    </div>
  )
}

export default TypingBubble
