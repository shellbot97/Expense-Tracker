import React from 'react'
import EmptyState from '@/components/ui/EmptyState'
import { Wallet } from 'lucide-react'

const Budgets: React.FC = () => {
  return (
    <div className="p-8">
      <div className="mb-6 pb-4 border-b border-neutral-200">
        <h1 className="text-page-title text-neutral-950 mb-1">Budgets</h1>
        <p className="text-body text-neutral-600">
          Set and track your spending budgets
        </p>
      </div>

      <EmptyState
        icon={<Wallet className="w-12 h-12" />}
        title="Budgets feature coming soon"
        description="Budget management and tracking will be available in the next update"
      />
    </div>
  )
}

export default Budgets
