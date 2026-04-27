import React, { ButtonHTMLAttributes } from 'react'
import { Loader2 } from 'lucide-react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  icon?: React.ReactNode
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', loading = false, icon, children, className = '', disabled, ...props }, ref) => {
    const baseClasses = 'inline-flex items-center justify-center gap-2 font-medium rounded transition-all duration-150 cursor-pointer disabled:cursor-not-allowed disabled:opacity-50'
    
    const variantClasses = {
      primary: 'bg-primary text-white hover:bg-primary-hover disabled:bg-neutral-200 disabled:text-neutral-400',
      secondary: 'bg-transparent text-secondary border border-secondary hover:bg-secondary-light disabled:border-neutral-200 disabled:text-neutral-400',
      ghost: 'bg-transparent text-neutral-800 hover:bg-neutral-100 disabled:text-neutral-400',
      destructive: 'bg-error text-white hover:bg-error/90 disabled:bg-neutral-200 disabled:text-neutral-400',
    }
    
    const sizeClasses = {
      sm: 'h-7 px-2.5 text-xs',
      md: 'h-9 px-4 text-sm',
      lg: 'h-10 px-5 text-sm',
    }
    
    return (
      <button
        ref={ref}
        className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : icon ? (
          <span className="flex items-center">{icon}</span>
        ) : null}
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

export default Button
