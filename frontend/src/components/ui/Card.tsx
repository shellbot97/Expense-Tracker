import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
}

const Card: React.FC<CardProps> = ({ children, className = '', hover = false }) => {
  return (
    <div
      className={`bg-white border border-neutral-200 rounded p-4 ${
        hover ? 'hover:shadow-sm transition-shadow duration-150' : ''
      } ${className}`}
    >
      {children}
    </div>
  )
}

export default Card
