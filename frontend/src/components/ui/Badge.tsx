import React from 'react'

type BadgeVariant = 'success' | 'warning' | 'error' | 'info' | 'neutral'

interface BadgeProps {
  children: React.ReactNode
  variant?: BadgeVariant
  className?: string
}

const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral', className = '' }) => {
  const variantClasses = {
    success: 'bg-success-light text-success',
    warning: 'bg-warning-light text-warning',
    error: 'bg-error-light text-error',
    info: 'bg-info-light text-info',
    neutral: 'bg-neutral-100 text-neutral-600',
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-caption font-medium ${variantClasses[variant]} ${className}`}
    >
      {children}
    </span>
  )
}

export default Badge
