import React from 'react'
import { Sparkles, Bot, RotateCcw } from 'lucide-react'
import Badge from '../ui/Badge'
import Button from '../ui/Button'

export function ConversationHeader({ onReset }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-200/70 dark:border-slate-800 px-6 py-4 bg-white/40 dark:bg-slate-900/40 backdrop-blur-md">
      <div className="flex items-center gap-3">
        <div className="relative flex h-10 w-10 items-center justify-center rounded-2xl bg-swiggy-500 text-white shadow-glow">
          <Bot className="h-5 w-5" />
          <span className="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-white bg-emerald-500 dark:border-slate-900" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h2 className="font-serif text-lg font-bold text-slate-900 dark:text-slate-100 leading-tight">
              CraveAI Concierge
            </h2>
            <Badge variant="primary" size="sm" icon={Sparkles}>
              v2.0
            </Badge>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Powered by Swiggy Gourmet Intelligence
          </p>
        </div>
      </div>

      {onReset && (
        <Button
          variant="ghost"
          size="sm"
          icon={RotateCcw}
          onClick={onReset}
          className="text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
          title="Reset conversation"
        >
          <span className="hidden sm:inline">New Chat</span>
        </Button>
      )}
    </div>
  )
}

export default ConversationHeader
