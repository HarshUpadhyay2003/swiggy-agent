import React from 'react'

export function Badge({
  children,
  variant = 'default',
  size = 'md',
  icon: Icon = null,
  className = '',
  ...props
}) {
  const baseClasses = 'inline-flex items-center gap-1 font-semibold rounded-full select-none'

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3.5 py-1.5 text-sm',
  }

  const variantClasses = {
    default: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
    primary: 'bg-swiggy-50 text-swiggy-700 border border-swiggy-200 dark:bg-swiggy-950/40 dark:text-swiggy-400 dark:border-swiggy-800',
    accent: 'bg-amber-50 text-amber-800 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800',
    success: 'bg-emerald-50 text-emerald-800 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800',
    veg: 'bg-veg-bg text-veg-dark border border-veg-border dark:bg-veg-dark/30 dark:text-veg-container dark:border-veg-dark',
    nonveg: 'bg-nonveg-bg text-nonveg-dark border border-nonveg-border dark:bg-nonveg-dark/30 dark:text-nonveg-container dark:border-nonveg-dark',
    glass: 'bg-white/80 backdrop-blur-md text-slate-800 border border-white/60 shadow-xs dark:bg-slate-800/80 dark:text-slate-100 dark:border-slate-700',
  }

  return (
    <span className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`} {...props}>
      {Icon && <Icon className="h-3 w-3" />}
      {children}
    </span>
  )
}

export default Badge
