import React from 'react'

export function Skeleton({ className = '', variant = 'text' }) {
  const variantClasses = {
    text: 'h-4 w-full rounded-md',
    title: 'h-8 w-2/3 rounded-lg',
    avatar: 'h-12 w-12 rounded-full',
    card: 'h-48 w-full rounded-2xl',
    pill: 'h-10 w-28 rounded-full',
  }

  return (
    <div
      className={`animate-pulse bg-gradient-to-r from-slate-200 via-slate-300 to-slate-200 dark:from-slate-800 dark:via-slate-700 dark:to-slate-800 ${variantClasses[variant] || ''} ${className}`}
    />
  )
}

export default Skeleton
