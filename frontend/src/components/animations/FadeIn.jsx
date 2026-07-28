import React from 'react'

export function FadeIn({ children, delay = 0, duration = 300, className = '' }) {
  return (
    <div
      className={`transition-opacity ease-out ${className}`}
      style={{
        transitionDuration: `${duration}ms`,
        transitionDelay: `${delay}ms`,
      }}
    >
      {children}
    </div>
  )
}

export default FadeIn
