import React, { InputHTMLAttributes, forwardRef } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className = '', ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1">
        {label && (
          <label htmlFor={props.id} className="text-label text-neutral-800">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`h-9 px-3 border rounded text-sm bg-white transition-all duration-150 ${
            error
              ? 'border-error focus:border-error focus:ring-2 focus:ring-error-light'
              : 'border-neutral-200 focus:border-accent focus:ring-2 focus:ring-accent-light'
          } ${className}`}
          {...props}
        />
        {error && <p className="text-caption text-error">{error}</p>}
        {helperText && !error && (
          <p className="text-caption text-neutral-600">{helperText}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input
