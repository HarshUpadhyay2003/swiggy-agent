import React from 'react'
import { Loader2 } from 'lucide-react'

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  icon: Icon = null,
  iconPosition = 'left',
  className = '',
  ...props
}) {
  const baseClasses = 'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-swiggy-500/50 disabled:cursor-not-allowed disabled:opacity-50 select-none'

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs rounded-full gap-1.5',
    md: 'px-5 py-2.5 text-sm rounded-full gap-2',
    lg: 'px-7 py-3.5 text-base rounded-full gap-2.5 font-semibold',
    icon: 'p-2.5 rounded-full',
  }

  const variantClasses = {
    primary: 'bg-swiggy-500 text-white shadow-glow hover:bg-swiggy-600 active:scale-[0.98]',
    secondary: 'bg-slate-100 text-slate-800 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700',
    outline: 'border border-slate-300/80 text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800',
    ghost: 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800',
    glass: 'bg-white/70 backdrop-blur-md border border-white/60 text-slate-800 shadow-sm hover:bg-white/90 dark:bg-slate-800/70 dark:border-slate-700/60 dark:text-slate-100 dark:hover:bg-slate-800/90',
    danger: 'bg-rose-500 text-white hover:bg-rose-600 shadow-sm',
    accent: 'bg-veg-container text-white hover:bg-veg dark:bg-veg dark:hover:bg-veg-dark',
  }

  return (
    <button
      disabled={disabled || loading}
      className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {loading && <Loader2 className="h-4 w-4 animate-spin text-current" />}
      {!loading && Icon && iconPosition === 'left' && <Icon className="h-4 w-4" />}
      {children && <span>{children}</span>}
      {!loading && Icon && iconPosition === 'right' && <Icon className="h-4 w-4" />}
    </button>
  )
}

export default Button
