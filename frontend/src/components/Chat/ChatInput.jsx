function ChatInput({ value, onChange, onSend, disabled }) {
  return (
    <div className="sticky bottom-0 z-20 rounded-[32px] border border-slate-200/70 bg-white/95 p-4 shadow-soft backdrop-blur-xl dark:border-slate-700/70 dark:bg-slate-950/95">
      <label className="mb-3 block text-sm font-semibold text-slate-700 dark:text-slate-300">Send a message</label>
      <div className="flex flex-col gap-3 sm:flex-row">
        <input
          type="text"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              event.preventDefault()
              onSend(value)
            }
          }}
          placeholder="Ask the assistant for a meal recommendation, cart update, or checkout"
          className="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-900 outline-none transition focus:border-swiggy-500 focus:ring-2 focus:ring-swiggy-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:focus:border-swiggy-400 dark:focus:ring-swiggy-400/20"
        />
        <button
          type="button"
          onClick={() => onSend(value)}
          disabled={disabled}
          className="rounded-3xl bg-swiggy-500 px-5 py-4 text-sm font-semibold text-white transition hover:bg-swiggy-600 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Send
        </button>
      </div>
      <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">Use Enter to submit. Structured cart and checkout commands also work.</p>
    </div>
  )
}

export default ChatInput
