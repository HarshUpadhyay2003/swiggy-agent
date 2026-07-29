import React, { useState } from 'react'
import { Send, Mic, Paperclip, Sparkles } from 'lucide-react'

export function StickyComposer({ onSend, loading = false, disabled = false }) {
  const [input, setInput] = useState('')

  const handleSubmit = (e) => {
    e?.preventDefault()
    if (!input.trim() || loading || disabled) return
    onSend(input.trim())
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="sticky bottom-6 z-40 w-full max-w-3xl mx-auto my-4 animate-slideUp pointer-events-auto px-2">
      <div className="glass-panel ambient-shadow rounded-full p-2 flex items-center relative border border-white/80 dark:border-slate-800 shadow-2xl bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl">
        <form onSubmit={handleSubmit} className="w-full relative flex items-center">
          {/* Attachment Icon */}
          <button
            type="button"
            className="absolute left-3.5 p-1.5 rounded-full text-slate-400 hover:text-swiggy-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title="Attach image or file"
          >
            <Paperclip className="h-4 w-4" />
          </button>

          {/* Input Text Area */}
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading || disabled}
            placeholder={loading ? 'CraveAI is thinking…' : 'Ask CraveAI for dishes, meal plans, or cart actions…'}
            className="w-full bg-slate-100/90 dark:bg-slate-800/90 text-slate-900 dark:text-slate-100 pl-11 pr-24 py-3 rounded-full text-sm font-medium focus:outline-none focus:ring-2 focus:ring-swiggy-500/50 border border-slate-200/60 dark:border-slate-700 transition-all placeholder:text-slate-400"
          />

          {/* Action Icons Right */}
          <div className="absolute right-2.5 flex items-center gap-1">
            {/* Mic Placeholder */}
            <button
              type="button"
              className="p-2 rounded-full text-slate-400 hover:text-swiggy-600 hover:bg-slate-200/60 dark:hover:bg-slate-700 transition-colors"
              title="Voice search"
            >
              <Mic className="h-4 w-4" />
            </button>

            {/* Send Button */}
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className={`w-9 h-9 rounded-full ${
                input.trim() && !loading
                  ? 'bg-swiggy-500 hover:bg-swiggy-600 text-white shadow-md scale-100'
                  : 'bg-slate-200 dark:bg-slate-700 text-slate-400 scale-95'
              } transition-all duration-200 flex items-center justify-center active:scale-90 disabled:opacity-50`}
              title="Send message"
            >
              {loading ? (
                <Sparkles className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default StickyComposer
