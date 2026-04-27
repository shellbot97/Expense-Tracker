import React from 'react'
import { useUIStore } from '@/store/uiStore'
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react'

const Toast: React.FC = () => {
  const { toasts, removeToast } = useUIStore()

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5" />
      case 'error':
        return <AlertCircle className="w-5 h-5" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5" />
      case 'info':
        return <Info className="w-5 h-5" />
      default:
        return null
    }
  }

  const getColors = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-success text-white'
      case 'error':
        return 'bg-error text-white'
      case 'warning':
        return 'bg-warning text-white'
      case 'info':
        return 'bg-info text-white'
      default:
        return 'bg-neutral-800 text-white'
    }
  }

  if (toasts.length === 0) return null

  return (
    <div className="fixed top-6 right-6 z-50 flex flex-col gap-2 min-w-[300px] max-w-[440px]">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`${getColors(toast.type)} rounded-lg shadow-lg py-3.5 px-5 flex items-center gap-3 animate-slide-in`}
        >
          {getIcon(toast.type)}
          <p className="flex-1 text-sm">{toast.message}</p>
          <button
            type="button"
            onClick={() => removeToast(toast.id)}
            className="p-1 hover:bg-white/10 rounded transition-colors"
            aria-label="Close notification"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ))}
    </div>
  )
}

export default Toast
