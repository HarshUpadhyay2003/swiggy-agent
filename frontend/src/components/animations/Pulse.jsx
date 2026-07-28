import React from 'react'

export function Pulse({ children, className = '' }) {
  return (
    <div className={`animate-pulsefast ${className}`}>
      {children}
    </div>
  )
}

export default Pulse
