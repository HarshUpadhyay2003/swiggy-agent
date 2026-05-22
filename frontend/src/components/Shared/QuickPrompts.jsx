function QuickPrompts({ options, onSelect }) {
  return (
    <div className="rounded-[32px] border border-slate-200/70 bg-white/90 p-4 shadow-soft backdrop-blur-xl dark:border-slate-700/70 dark:bg-slate-900/80">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Quick actions</p>
          <p className="text-sm text-slate-600 dark:text-slate-400">Tap a suggestion to guide the AI instantly.</p>
        </div>
      </div>
      <div className="flex gap-3 overflow-x-auto pb-2">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => onSelect(option)}
            className="whitespace-nowrap rounded-full border border-slate-200/80 bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-swiggy-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:hover:border-slate-500"
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  )
}

export default QuickPrompts
