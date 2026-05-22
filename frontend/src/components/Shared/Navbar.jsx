import { Moon, Sun, Sparkles } from 'lucide-react'
import { useAppActions, useAppState } from '../../store/AppStore'

function Navbar() {
  const { theme } = useAppState()
  const { toggleTheme } = useAppActions()

  return (
    <header className="flex flex-col gap-4 rounded-[32px] border border-slate-200/70 bg-white/85 px-5 py-4 shadow-soft backdrop-blur-xl transition-colors duration-300 dark:border-slate-700/70 dark:bg-slate-950/80">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-swiggy-500 text-white shadow-glow">
            <Sparkles className="h-6 w-6" />
          </div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">AI Commerce</p>
            <h1 className="text-2xl font-semibold text-slate-950 dark:text-slate-50">Swiggy-style ordering copilot</h1>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={toggleTheme}
            className="inline-flex items-center gap-2 rounded-3xl border border-slate-200 bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-200 dark:hover:border-slate-500"
          >
            {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            {theme === 'dark' ? 'Light mode' : 'Dark mode'}
          </button>
          <span className="rounded-3xl bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 dark:bg-slate-900 dark:text-slate-200">
            Session ready
          </span>
        </div>
      </div>
    </header>
  )
}

export default Navbar
