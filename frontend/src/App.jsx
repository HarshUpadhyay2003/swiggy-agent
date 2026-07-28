import React, { useState, useEffect } from 'react'
import Home from './pages/Home'
import PlannerPage from './pages/PlannerPage'
import CartDrawer from './components/Cart/CartDrawer'
import { Toaster } from 'react-hot-toast'
import { AppProvider } from './store/AppStore'

function MainContent() {
  const [currentPath, setCurrentPath] = useState(window.location.pathname || '/')
  const [isCartOpen, setIsCartOpen] = useState(false)

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname || '/')
    }
    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  const navigate = (path) => {
    if (window.location.pathname !== path) {
      window.history.pushState({}, '', path)
    }
    setCurrentPath(path)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const renderPage = () => {
    switch (currentPath) {
      case '/planner':
        return <PlannerPage onNavigate={navigate} onOpenCart={() => setIsCartOpen(true)} />
      case '/':
      default:
        return <Home onNavigate={navigate} onOpenCart={() => setIsCartOpen(true)} />
    }
  }

  return (
    <div className="min-h-screen bg-gourmet-surface text-gourmet-on-surface transition-colors duration-300 dark:bg-slate-950 dark:text-slate-100 font-sans">
      {renderPage()}
      <CartDrawer isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
      <Toaster position="top-right" />
    </div>
  )
}

function App() {
  return (
    <AppProvider>
      <MainContent />
    </AppProvider>
  )
}

export default App
