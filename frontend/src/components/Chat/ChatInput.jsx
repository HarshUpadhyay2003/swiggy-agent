import React from 'react'
import { Send, Mic, Paperclip, Sparkles, Loader2 } from 'lucide-react'
import Button from '../ui/Button'

export function ChatInput({ value, onChange, onSend, disabled = false }) {
  const handleSubmit = (e) => {
    e?.preventDefault()
    if (!value?.trim() || disabled) return
    onSend(value)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative w-full group">
      {/* Soft Glow Ring Container */}
      <div className="absolute inset-0 bg-swiggy-500/10 rounded-full blur-md opacity-0 group-focus-within:opacity-100 transition-opacity duration-500 pointer-events-none" />

      {/* Pill Input Bar */}
      <div className="relative z-10 flex items-center gap-2 rounded-full border border-slate-200/90 bg-white/95 px-4 py-2 shadow-gourmet backdrop-blur-xl transition-all duration-300 dark:border-slate-700/80 dark:bg-slate-900/95 group-focus-within:border-swiggy-500/80 group-focus-within:ring-4 group-focus-within:ring-swiggy-500/15">
        {/* Attachment Placeholder */}
        <button
          type="button"
          disabled={disabled}
          className="p-2 text-slate-400 hover:text-slate-600 dark:text-slate-500 dark:hover:text-slate-300 transition-colors rounded-full shrink-0"
          title="Attach food photo or recipe (coming soon)"
        >
          <Paperclip className="h-5 w-5" />
        </button>

        {/* Text Input */}
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask CraveAI for dishes, diets, budgets, or plans..."
          disabled={disabled}
          className="w-full bg-transparent text-sm sm:text-base font-sans text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none disabled:opacity-50 py-2.5"
        />

        {/* Voice Placeholder */}
        <button
          type="button"
          disabled={disabled}
          className="hidden sm:flex p-2 text-slate-400 hover:text-swiggy-500 transition-colors rounded-full shrink-0"
          title="Voice search (coming soon)"
        >
          <Mic className="h-5 w-5" />
        </button>

        {/* Send Action Button */}
        <Button
          type="submit"
          variant="primary"
          size="icon"
          disabled={!value?.trim() || disabled}
          className="h-10 w-10 shrink-0 shadow-glow"
        >
          {disabled ? (
            <Loader2 className="h-4 w-4 animate-spin text-white" />
          ) : (
            <Send className="h-4 w-4 text-white" />
          )}
        </Button>
      </div>
    </form>
  )
}

export default ChatInput
