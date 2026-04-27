import React from 'react'
import { useUIStore } from '@/store/uiStore'
import { AlertTriangle, Info } from 'lucide-react'

const ConfirmDialog: React.FC = () => {
  const { confirmDialog } = useUIStore()

  if (!confirmDialog.isOpen) return null

  const handleConfirm = () => {
    if (confirmDialog.resolve) {
      confirmDialog.resolve(true)
      useUIStore.setState({
        confirmDialog: { ...confirmDialog, isOpen: false, resolve: undefined },
      })
    }
  }

  const handleCancel = () => {
    if (confirmDialog.resolve) {
      confirmDialog.resolve(false)
      useUIStore.setState({
        confirmDialog: { ...confirmDialog, isOpen: false, resolve: undefined },
      })
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/50"
        onClick={handleCancel}
        aria-hidden="true"
      />
      <div className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4 animate-slide-up">
        <div className="p-5 flex items-start gap-4">
          {confirmDialog.options.destructive ? (
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-error-light flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-error" />
            </div>
          ) : (
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-info-light flex items-center justify-center">
              <Info className="w-5 h-5 text-info" />
            </div>
          )}
          <div className="flex-1 pt-1">
            <h3 className="text-section-title text-neutral-950 mb-2">
              {confirmDialog.title}
            </h3>
            <p className="text-body text-neutral-600">{confirmDialog.message}</p>
          </div>
        </div>
        <div className="border-t border-neutral-200 p-5 flex justify-end gap-2">
          <button
            type="button"
            onClick={handleCancel}
            className="h-9 px-4 rounded border border-secondary text-secondary text-sm font-medium hover:bg-secondary-light transition-colors"
          >
            {confirmDialog.options.cancelLabel}
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            className={`h-9 px-4 rounded text-white text-sm font-medium transition-colors ${
              confirmDialog.options.destructive
                ? 'bg-error hover:bg-error/90'
                : 'bg-primary hover:bg-primary-hover'
            }`}
          >
            {confirmDialog.options.okLabel}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConfirmDialog
