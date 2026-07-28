import React from 'react'
import { Bot } from 'lucide-react'

export function TypingBubble() {
  return (
    <div className="flex items-start gap-3 max-w-[80%] my-3 animate-fadeIn">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-2xl bg-swiggy-500/15 text-swiggy-600 dark:text-swiggy-400 border border-swiggy-500/20">
        <Bot className="h-4 w-4" />
      </div>

      <div className="glass-card px-4 py-3 rounded-2xl rounded-tl-xs flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-swiggy-500 animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="h-2 w-2 rounded-full bg-swiggy-500 animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="h-2 w-2 rounded-full bg-swiggy-500 animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
        <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
          CraveAI is thinking…
        </span>
      </div>
    </div>
  )
}

export default TypingBubble
