import { create } from 'zustand'

type ToastType = 'success' | 'error' | 'warning' | 'info'

interface Toast {
  id: string
  message: string
  type: ToastType
}

interface ConfirmOptions {
  destructive?: boolean
  okLabel?: string
  cancelLabel?: string
}

interface UIState {
  toasts: Toast[]
  isLoading: boolean
  confirmDialog: {
    isOpen: boolean
    title: string
    message: string
    options: ConfirmOptions
    resolve?: (value: boolean) => void
  }
  showToast: (message: string, type?: ToastType) => void
  removeToast: (id: string) => void
  showLoader: () => void
  hideLoader: () => void
  confirm: (title: string, message: string, options?: ConfirmOptions) => Promise<boolean>
}

export const useUIStore = create<UIState>((set, get) => ({
  toasts: [],
  isLoading: false,
  confirmDialog: {
    isOpen: false,
    title: '',
    message: '',
    options: {},
  },

  showToast: (message: string, type: ToastType = 'info') => {
    const id = Math.random().toString(36).substr(2, 9)
    const toast = { id, message, type }
    set((state) => ({ toasts: [...state.toasts, toast] }))
    
    const duration = type === 'error' ? 8000 : 5000
    setTimeout(() => {
      get().removeToast(id)
    }, duration)
  },

  removeToast: (id: string) => {
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }))
  },

  showLoader: () => set({ isLoading: true }),
  hideLoader: () => set({ isLoading: false }),

  confirm: (title: string, message: string, options: ConfirmOptions = {}) => {
    return new Promise<boolean>((resolve) => {
      set({
        confirmDialog: {
          isOpen: true,
          title,
          message,
          options: {
            okLabel: options.okLabel || 'Confirm',
            cancelLabel: options.cancelLabel || 'Cancel',
            destructive: options.destructive || false,
          },
          resolve,
        },
      })
    })
  },
}))

// Helper functions
export const AppUI = {
  toast: (message: string, type?: ToastType) => useUIStore.getState().showToast(message, type),
  loader: {
    show: () => useUIStore.getState().showLoader(),
    hide: () => useUIStore.getState().hideLoader(),
  },
  confirm: (title: string, message: string, options?: ConfirmOptions) =>
    useUIStore.getState().confirm(title, message, options),
}
