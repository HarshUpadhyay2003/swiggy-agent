import React, { useState } from 'react'
import { Moon, Sun, User, ShoppingBag, RotateCcw, Menu, X, Compass, Calendar } from 'lucide-react'
import { useAppActions, useAppState } from '../../store/AppStore'
import onlyLogo from '../../assets/only_logo.png'

export function Navbar({ currentPath = '/', onNavigate, onOpenCart }) {
  const { theme, cart } = useAppState()
  const { toggleTheme, resetGuestSession } = useAppActions()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const itemCount = cart?.items?.reduce((acc, item) => acc + (item.quantity || 1), 0) || 0

  const handleNavClick = (path, e) => {
    e?.preventDefault()
    setIsMobileMenuOpen(false)
    onNavigate && onNavigate(path)
  }

  const handleCartClick = () => {
    setIsMobileMenuOpen(false)
    onOpenCart && onOpenCart()
  }

  const handleResetSession = () => {
    setIsMobileMenuOpen(false)
    resetGuestSession()
  }

  return (
    <header className="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl top-0 sticky z-50 shadow-sm w-full max-w-[1200px] mx-auto rounded-b-2xl border-b border-white/60 dark:border-slate-800 transition-colors">
      <div className="flex justify-between items-center w-full px-4 md:px-8 h-14 md:h-16">
        {/* Brand Identity */}
        <button
          type="button"
          onClick={(e) => handleNavClick('/', e)}
          className="flex items-center gap-3 focus:outline-none transition-transform duration-300 ease-out hover:scale-105 active:scale-95 origin-left shrink-0"
        >
          <div className="h-9 w-9 rounded-xl overflow-hidden flex items-center justify-center shadow-sm shrink-0 bg-swiggy-50 dark:bg-slate-800 border border-slate-200/50 dark:border-slate-700">
            <img src={onlyLogo} alt="CraveAI Logo" className="w-full h-full object-cover" />
          </div>
          <span className="font-serif text-xl md:text-2xl font-bold text-swiggy-700 dark:text-swiggy-400 tracking-tight">
            CraveAI
          </span>
        </button>

        {/* Desktop Nav Items */}
        <nav className="hidden md:flex items-center gap-6">
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

        {/* Desktop Action Icons */}
        <div className="hidden md:flex items-center gap-2">
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

        {/* Mobile Action Controls */}
        <div className="flex md:hidden items-center gap-1">
          <button
            type="button"
            onClick={handleCartClick}
            className="p-2 text-swiggy-700 dark:text-swiggy-400 hover:bg-swiggy-50 dark:hover:bg-slate-800 transition-colors rounded-full relative"
            title="Open Cart"
            aria-label="Open Cart"
          >
            <ShoppingBag className="h-5 w-5" />
            {itemCount > 0 && (
              <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-swiggy-500 text-[9px] font-bold text-white shadow-sm">
                {itemCount}
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={toggleTheme}
            className="p-2 text-swiggy-700 dark:text-swiggy-400 hover:bg-swiggy-50 dark:hover:bg-slate-800 transition-colors rounded-full"
            title="Toggle Theme"
            aria-label="Toggle Theme"
          >
            {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>

          <button
            type="button"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 text-slate-700 dark:text-slate-200 hover:bg-swiggy-50 dark:hover:bg-slate-800 transition-colors rounded-full focus:outline-none"
            title={isMobileMenuOpen ? 'Close Menu' : 'Open Menu'}
            aria-label={isMobileMenuOpen ? 'Close Menu' : 'Open Menu'}
            aria-expanded={isMobileMenuOpen}
          >
            {isMobileMenuOpen ? <X className="h-6 w-6 text-swiggy-600 dark:text-swiggy-400" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Dropdown Menu Drawer */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200/80 dark:border-slate-800 bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl px-4 pt-3 pb-4 space-y-2 rounded-b-2xl shadow-lg animate-fadeIn">
          <button
            type="button"
            onClick={(e) => handleNavClick('/', e)}
            className={`w-full flex items-center justify-between px-4 py-2.5 rounded-xl font-medium text-sm transition-colors ${
              currentPath === '/'
                ? 'bg-swiggy-50 dark:bg-swiggy-950/40 text-swiggy-600 dark:text-swiggy-400 font-bold border-l-4 border-swiggy-500'
                : 'text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800/60'
            }`}
          >
            <div className="flex items-center gap-3">
              <Compass className="h-4 w-4" />
              <span>Crave</span>
            </div>
            {currentPath === '/' && <span className="h-2 w-2 rounded-full bg-swiggy-500" />}
          </button>

          <button
            type="button"
            onClick={(e) => handleNavClick('/planner', e)}
            className={`w-full flex items-center justify-between px-4 py-2.5 rounded-xl font-medium text-sm transition-colors ${
              currentPath === '/planner'
                ? 'bg-swiggy-50 dark:bg-swiggy-950/40 text-swiggy-600 dark:text-swiggy-400 font-bold border-l-4 border-swiggy-500'
                : 'text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800/60'
            }`}
          >
            <div className="flex items-center gap-3">
              <Calendar className="h-4 w-4" />
              <span>Planner</span>
            </div>
            {currentPath === '/planner' && <span className="h-2 w-2 rounded-full bg-swiggy-500" />}
          </button>

          <button
            type="button"
            onClick={handleCartClick}
            className="w-full flex items-center justify-between px-4 py-2.5 rounded-xl font-medium text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800/60 transition-colors"
          >
            <div className="flex items-center gap-3">
              <ShoppingBag className="h-4 w-4 text-swiggy-600 dark:text-swiggy-400" />
              <span>Cart</span>
            </div>
            {itemCount > 0 ? (
              <span className="inline-flex items-center rounded-full bg-swiggy-500 px-2 py-0.5 text-xs font-bold text-white">
                {itemCount} items
              </span>
            ) : (
              <span className="text-xs text-slate-400">Empty</span>
            )}
          </button>

          <div className="pt-2 border-t border-slate-200/60 dark:border-slate-800/80 flex items-center justify-between px-1 gap-2">
            <button
              type="button"
              onClick={handleResetSession}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200/80 dark:border-slate-700 transition-colors"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Reset Session</span>
            </button>

            <button
              type="button"
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200/80 dark:border-slate-700 transition-colors"
            >
              <User className="h-3.5 w-3.5" />
              <span>Profile</span>
            </button>
          </div>
        </div>
      )}
    </header>
  )
}

export default Navbar
