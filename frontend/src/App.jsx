import Home from './pages/Home'
import { Toaster } from 'react-hot-toast'
import { AppProvider } from './store/AppStore'

function App() {
  return (
    <AppProvider>
      <div className="min-h-screen bg-slate-50 text-slate-950 transition-colors duration-300 dark:bg-slate-950 dark:text-slate-100">
        <Home />
        <Toaster position="top-right" />
      </div>
    </AppProvider>
  )
}

export default App
