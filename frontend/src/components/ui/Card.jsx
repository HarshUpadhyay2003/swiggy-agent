import React from 'react'

export function Card({
  children,
  variant = 'surface',
  className = '',
  padding = 'md',
  hover = false,
  ...props
}) {
  const baseClasses = 'rounded-2xl transition-all duration-300 overflow-hidden'

  const paddingClasses = {
    none: 'p-0',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  }

  const variantClasses = {
    surface: 'bg-white border border-slate-200/80 shadow-gourmet dark:bg-slate-900 dark:border-slate-800',
    glass: 'bg-white/75 backdrop-blur-xl border border-white/60 shadow-gourmet dark:bg-slate-900/75 dark:border-slate-800/80',
    flat: 'bg-gourmet-surface-low border border-slate-200/60 dark:bg-slate-800/50 dark:border-slate-800',
    elevated: 'bg-white shadow-gourmet-hover border border-slate-100 dark:bg-slate-900 dark:border-slate-800',
    outline: 'border border-slate-200 bg-transparent dark:border-slate-800',
  }

  const hoverClasses = hover ? 'hover:-translate-y-1 hover:shadow-gourmet-hover cursor-pointer' : ''

  return (
    <div
      className={`${baseClasses} ${paddingClasses[padding]} ${variantClasses[variant]} ${hoverClasses} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

export default Card
