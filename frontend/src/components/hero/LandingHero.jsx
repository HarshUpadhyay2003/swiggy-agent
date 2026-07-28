import React from 'react'
import { Sparkles, ArrowUp } from 'lucide-react'

export function LandingHero({ inputValue = '', onChangeInput, onSendInput, onSelectPrompt }) {
  const handleSubmit = (e) => {
    e?.preventDefault()
    if (!inputValue?.trim()) return
    onSendInput(inputValue)
  }

  const suggestionChips = [
    { label: 'Healthy Lunch', icon: '🥗' },
    { label: 'High Protein', icon: '⚡' },
    { label: 'Comfort Food', icon: '🍜' },
    { label: 'Budget Treat', icon: '🏷️' },
    { label: 'Under 30 mins', icon: '⏱️' },
  ]

  return (
    <section className="w-full flex flex-col items-center text-center my-6 md:my-10">
      {/* Headline */}
      <h1 className="font-serif text-3xl sm:text-4xl md:text-5xl font-bold text-slate-900 dark:text-slate-100 mb-2 tracking-tight">
        Good Evening, Alex 👋
      </h1>
      <p className="text-base sm:text-lg text-slate-600 dark:text-slate-300 opacity-80 mb-8 max-w-lg mx-auto font-sans">
        What are you craving today?
      </p>

      {/* Conversational Input */}
      <form onSubmit={handleSubmit} className="w-full max-w-2xl relative mb-6 group">
        <div className="absolute inset-0 bg-white/40 rounded-full blur-md opacity-0 group-focus-within:opacity-100 transition-opacity duration-500 pointer-events-none" />
        <div className="glass-panel ambient-shadow rounded-full p-2 flex items-center relative z-10 subtle-glow transition-all duration-300 border border-slate-200/60 dark:border-slate-800">
          <Sparkles className="h-5 w-5 text-swiggy-500 ml-4 mr-2 shrink-0" />
          <input
            type="text"
            value={inputValue}
            onChange={(e) => onChangeInput(e.target.value)}
            placeholder="Tell me what you're hungry for..."
            className="w-full bg-transparent border-none focus:outline-none text-base text-slate-900 dark:text-slate-100 placeholder:text-slate-400 h-12 outline-none px-2"
          />
          <button
            type="submit"
            className="bg-swiggy-500 text-white h-11 w-11 rounded-full flex items-center justify-center hover:bg-swiggy-600 transition-colors shadow-sm ml-2 shrink-0"
          >
            <ArrowUp className="h-5 w-5" />
          </button>
        </div>
      </form>

      {/* Quick Suggestion Chips */}
      <div className="flex flex-wrap justify-center gap-3 w-full max-w-3xl">
        {suggestionChips.map((chip) => (
          <button
            key={chip.label}
            type="button"
            onClick={() => onSelectPrompt(chip.label)}
            className="glass-panel px-5 py-2.5 rounded-full text-sm font-medium text-slate-700 dark:text-slate-200 hover:text-swiggy-600 hover:bg-white hover:border-swiggy-300 dark:hover:bg-slate-800 transition-all ambient-shadow flex items-center gap-2"
          >
            <span>{chip.icon}</span>
            <span>{chip.label}</span>
          </button>
        ))}
      </div>
    </section>
  )
}

export default LandingHero
