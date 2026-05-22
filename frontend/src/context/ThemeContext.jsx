import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const ThemeContext = createContext(null)

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light')

  useEffect(() => {
    if (typeof window === 'undefined') return
    const storedTheme = window.localStorage.getItem('swiggy_theme')
    if (storedTheme === 'light' || storedTheme === 'dark') {
      setTheme(storedTheme)
      document.documentElement.classList.toggle('dark', storedTheme === 'dark')
      return
    }
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const preferred = prefersDark ? 'dark' : 'light'
    setTheme(preferred)
    document.documentElement.classList.toggle('dark', preferred === 'dark')
  }, [])

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    window.localStorage.setItem('swiggy_theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme((current) => (current === 'dark' ? 'light' : 'dark'))

  const value = useMemo(() => ({ theme, toggleTheme }), [theme])
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
