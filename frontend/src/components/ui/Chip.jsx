import React from 'react'

export function Chip({
  children,
  active = false,
  onClick,
  icon: Icon = null,
  variant = 'default',
  size = 'md',
  className = '',
  ...props
}) {
  const baseClasses = 'inline-flex items-center gap-1.5 rounded-full font-medium transition-all duration-200 select-none cursor-pointer whitespace-nowrap'

  const sizeClasses = {
    sm: 'px-3 py-1 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-5 py-2.5 text-base',
  }

  const variantClasses = active
    ? 'bg-swiggy-500 text-white shadow-sm font-semibold'
    : {
        default: 'bg-white border border-slate-200/80 text-slate-700 hover:border-swiggy-300 hover:bg-swiggy-50/50 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-200 dark:hover:border-swiggy-500',
        glass: 'bg-white/70 backdrop-blur-md border border-white/60 text-slate-700 hover:bg-white/90 dark:bg-slate-800/70 dark:border-slate-700/60 dark:text-slate-200',
        filled: 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-200',
        veg: 'bg-veg-bg border border-veg-border text-veg-dark font-medium dark:bg-veg-dark/20 dark:text-veg-container',
      }[variant] || 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'

  return (
    <button
      type="button"
      onClick={onClick}
      className={`${baseClasses} ${sizeClasses[size]} ${variantClasses} ${className}`}
      {...props}
    >
      {Icon && <Icon className="h-3.5 w-3.5" />}
      <span>{children}</span>
    </button>
  )
}

export default Chip
