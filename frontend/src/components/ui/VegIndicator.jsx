import React from 'react'

export function VegIndicator({ isVeg = true, size = 'md', className = '' }) {
  const sizeMap = {
    sm: { box: 'h-3.5 w-3.5 border', dot: 'h-1.5 w-1.5' },
    md: { box: 'h-4 w-4 border-2', dot: 'h-2 w-2' },
    lg: { box: 'h-5 w-5 border-2', dot: 'h-2.5 w-2.5' },
  }

  const { box, dot } = sizeMap[size] || sizeMap.md

  if (isVeg) {
    return (
      <div
        className={`inline-flex items-center justify-center border-veg-container bg-white dark:bg-slate-900 rounded-xs ${box} ${className}`}
        title="Pure Vegetarian"
      >
        <div className={`rounded-full bg-veg-container ${dot}`} />
      </div>
    )
  }

  return (
    <div
      className={`inline-flex items-center justify-center border-nonveg-container bg-white dark:bg-slate-900 rounded-xs ${box} ${className}`}
      title="Non-Vegetarian"
    >
      <div className={`bg-nonveg-container clip-triangle ${dot}`} style={{ clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)' }} />
    </div>
  )
}

export default VegIndicator
