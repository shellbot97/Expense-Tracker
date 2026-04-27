import React, { SelectHTMLAttributes, forwardRef } from 'react'
import { ChevronDown } from 'lucide-react'

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  helperText?: string
  options: { value: string | number; label: string }[]
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, helperText, options, className = '', ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1">
        {label && (
          <label htmlFor={props.id} className="text-label text-neutral-800">
            {label}
          </label>
        )}
        <div className="relative">
          <select
            ref={ref}
            className={`h-9 w-full px-3 pr-8 border rounded text-sm bg-white appearance-none cursor-pointer transition-all duration-150 ${
              error
                ? 'border-error focus:border-error focus:ring-2 focus:ring-error-light'
                : 'border-neutral-200 focus:border-accent focus:ring-2 focus:ring-accent-light'
            } ${className}`}
            {...props}
          >
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-600 pointer-events-none" />
        </div>
        {error && <p className="text-caption text-error">{error}</p>}
        {helperText && !error && (
          <p className="text-caption text-neutral-600">{helperText}</p>
        )}
      </div>
    )
  }
)

Select.displayName = 'Select'

export default Select
