import React from 'react'

export function SlideUp({ children, className = '' }) {
  return (
    <div className={`transform transition-all duration-300 ease-out hover:-translate-y-0.5 ${className}`}>
      {children}
    </div>
  )
}

export default SlideUp
