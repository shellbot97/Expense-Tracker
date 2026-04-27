import React from 'react'
import { useUIStore } from '@/store/uiStore'
import { Loader2 } from 'lucide-react'

const LoadingOverlay: React.FC = () => {
  const isLoading = useUIStore((state) => state.isLoading)

  if (!isLoading) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="bg-white rounded-lg p-6 shadow-xl">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    </div>
  )
}

export default LoadingOverlay
