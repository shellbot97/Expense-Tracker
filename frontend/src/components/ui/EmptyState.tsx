import React from 'react'

interface EmptyStateProps {
  icon: React.ReactNode
  title: string
  description?: string
  action?: React.ReactNode
}

const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, description, action }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 max-w-sm mx-auto text-center">
      <div className="mb-4 text-neutral-300">{icon}</div>
      <h3 className="text-card-title text-neutral-800 mb-2">{title}</h3>
      {description && <p className="text-body text-neutral-600 mb-4">{description}</p>}
      {action && <div>{action}</div>}
    </div>
  )
}

export default EmptyState
