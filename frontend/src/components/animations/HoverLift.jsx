import React from 'react'

export function HoverLift({ children, className = '' }) {
  return (
    <div className={`transition-all duration-300 hover:-translate-y-1.5 hover:shadow-gourmet-hover ${className}`}>
      {children}
    </div>
  )
}

export default HoverLift
