import React from 'react'
import { Moon, Sun, User, ShoppingBag, RotateCcw } from 'lucide-react'
import { useAppActions, useAppState } from '../../store/AppStore'

export function Navbar({ currentPath = '/', onNavigate, onOpenCart }) {
  const { theme, cart } = useAppState()
  const { toggleTheme, resetGuestSession } = useAppActions()

  const itemCount = cart?.items?.reduce((acc, item) => acc + (item.quantity || 1), 0) || 0

  const handleNavClick = (path, e) => {
    e?.preventDefault()
    onNavigate && onNavigate(path)
  }

  return (
    <header className="hidden md:flex bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl top-0 sticky z-50 shadow-sm flex justify-between items-center w-full px-4 md:px-8 max-w-[1200px] mx-auto h-16 rounded-b-2xl border-b border-white/60 dark:border-slate-800 transition-colors">
      {/* Brand Identity */}
      <button
        type="button"
        onClick={(e) => handleNavClick('/', e)}
        className="flex items-center gap-3 focus:outline-none"
      >
        <div className="h-8 w-8 rounded-lg bg-swiggy-500 flex items-center justify-center text-white font-bold font-serif shadow-sm">
          C
        </div>
        <span className="font-serif text-2xl font-bold text-swiggy-700 dark:text-swiggy-400 tracking-tight">
          CraveAI
        </span>
      </button>

      {/* Desktop Nav Items */}
      <nav className="flex items-center gap-6">
        <button
          type="button"
          onClick={(e) => handleNavClick('/', e)}
          className={`${
            currentPath === '/'
              ? 'text-swiggy-600 dark:text-swiggy-400 font-bold border-b-2 border-swiggy-500'
              : 'text-slate-600 dark:text-slate-300 font-medium hover:bg-swiggy-50 dark:hover:bg-slate-800'
          } pb-1 px-2 text-sm transition-all rounded-full`}
        >
          Crave
        </button>
        <button
          type="button"
          onClick={(e) => handleNavClick('/planner', e)}
          className={`${
            currentPath === '/planner'
              ? 'text-swiggy-600 dark:text-swiggy-400 font-bold border-b-2 border-swiggy-500'
              : 'text-slate-600 dark:text-slate-300 font-medium hover:bg-swiggy-50 dark:hover:bg-slate-800'
          } pb-1 px-2 text-sm transition-all rounded-full`}
        >
          Planner
        </button>
        <button
          type="button"
          onClick={onOpenCart}
          className="text-slate-600 dark:text-slate-300 font-medium hover:bg-swiggy-50 dark:hover:bg-slate-800 transition-colors rounded-full px-3 py-1 text-sm relative flex items-center gap-1.5"
        >
          <span>Cart</span>
          {itemCount > 0 && (
            <span className="inline-flex items-center rounded-full bg-swiggy-500 px-2 py-0.5 text-[10px] font-bold text-white shadow-sm">
              {itemCount}
            </span>
          )}
        </button>
      </nav>

      {/* Action Icons */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onOpenCart}
          className="p-2 text-swiggy-700 dark:text-swiggy-400 hover:bg-swiggy-50 dark:hover:bg-slate-800 transition-colors rounded-full relative"
          title="Open Cart"
        >
          <ShoppingBag className="h-5 w-5" />
          {itemCount > 0 && (
            <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-swiggy-500 animate-pulse" />
          )}
        </button>

        <button
          type="button"
          onClick={resetGuestSession}
          className="p-2 text-slate-500 hover:text-swiggy-600 hover:bg-swiggy-50 dark:hover:bg-slate-800 transition-colors rounded-full"
          title="Reset Guest Session"
        >
          <RotateCcw className="h-4 w-4" />
        </button>

        <button
          type="button"
          onClick={toggleTheme}
          className="p-2 text-swiggy-700 dark:text-swiggy-400 hover:bg-swiggy-50 dark:hover:bg-slate-800 transition-colors rounded-full"
          title="Toggle mode"
        >
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </button>

        <button
          type="button"
          className="p-2 text-swiggy-700 dark:text-swiggy-400 hover:bg-swiggy-50 dark:hover:bg-slate-800 transition-colors rounded-full"
          title="Guest Profile"
        >
          <User className="h-5 w-5" />
        </button>
      </div>
    </header>
  )
}

export default Navbar
