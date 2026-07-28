import React from 'react'

export function ScaleIn({ children, className = '' }) {
  return (
    <div className={`transition-transform duration-200 active:scale-95 ${className}`}>
      {children}
    </div>
  )
}

export default ScaleIn
