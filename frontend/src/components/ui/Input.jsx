import React from 'react'

export function Input({
  value,
  onChange,
  placeholder = '',
  type = 'text',
  icon: Icon = null,
  rightElement = null,
  disabled = false,
  className = '',
  variant = 'pill',
  ...props
}) {
  const shapeClasses = variant === 'pill' ? 'rounded-full px-5 py-3.5' : 'rounded-2xl px-4 py-3'

  return (
    <div className={`relative flex items-center w-full ${className}`}>
      {Icon && (
        <div className="absolute left-4 text-slate-400 dark:text-slate-500 pointer-events-none">
          <Icon className="h-5 w-5" />
        </div>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        className={`w-full bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-700/80 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 text-sm md:text-base focus:outline-none focus:border-swiggy-500 focus:ring-4 focus:ring-swiggy-500/15 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${shapeClasses} ${
          Icon ? 'pl-12' : ''
        } ${rightElement ? 'pr-14' : ''}`}
        {...props}
      />
      {rightElement && (
        <div className="absolute right-2 flex items-center">
          {rightElement}
        </div>
      )}
    </div>
  )
}

export default Input
