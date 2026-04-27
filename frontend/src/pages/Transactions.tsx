import React, { useEffect, useState } from 'react'
import { transactionsApi, categoriesApi, sourcesApi } from '@/lib/api'
import { Transaction, TransactionCreate, Category, Source } from '@/types/api'
import { AppUI } from '@/store/uiStore'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Select from '@/components/ui/Select'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import EmptyState from '@/components/ui/EmptyState'
import { Plus, Search, Edit2, Trash2, Receipt, X } from 'lucide-react'
import { format } from 'date-fns'

const Transactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  
  // Filters
  const [filters, setFilters] = useState({
    search: '',
    type: '',
    category: '',
    source: '',
    startDate: '',
    endDate: '',
  })

  // Form data
  const [formData, setFormData] = useState<TransactionCreate>({
    transaction_date: format(new Date(), 'yyyy-MM-dd'),
    amount: 0,
    transaction_type: 'expense',
    description: '',
    notes: '',
    category_id: null,
    source_id: null,
  })
  const [formErrors, setFormErrors] = useState<Record<string, string>>({})
  const [formLoading, setFormLoading] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [txns, cats, srcs] = await Promise.all([
        transactionsApi.getAll(),
        categoriesApi.getAll(),
        sourcesApi.getAll(),
      ])
      setTransactions(txns)
      setCategories(cats)
      setSources(srcs)
    } catch (error: any) {
      AppUI.toast(error.response?.data?.error || 'Failed to load transactions', 'error')
    } finally {
      setLoading(false)
    }
  }

  const openAddModal = () => {
    setEditingId(null)
    setFormData({
      transaction_date: format(new Date(), 'yyyy-MM-dd'),
      amount: 0,
      transaction_type: 'expense',
      description: '',
      notes: '',
      category_id: null,
      source_id: null,
    })
    setFormErrors({})
    setShowModal(true)
  }

  const openEditModal = (transaction: Transaction) => {
    setEditingId(transaction.id)
    setFormData({
      transaction_date: transaction.transaction_date,
      amount: transaction.amount / 100,
      transaction_type: transaction.transaction_type,
      description: transaction.description || '',
      notes: transaction.notes || '',
      category_id: transaction.category_id,
      source_id: transaction.source_id,
    })
    setFormErrors({})
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormErrors({})

    // Validation
    const errors: Record<string, string> = {}
    if (!formData.transaction_date) errors.transaction_date = 'Date is required'
    if (!formData.amount || formData.amount <= 0) errors.amount = 'Amount must be greater than 0'
    if (!formData.description) errors.description = 'Description is required'

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors)
      return
    }

    setFormLoading(true)
    try {
      const payload: TransactionCreate = {
        ...formData,
        amount: Math.round(formData.amount * 100), // Convert to cents
      }

      if (editingId) {
        await transactionsApi.update(editingId, payload)
        AppUI.toast('Transaction updated successfully', 'success')
      } else {
        await transactionsApi.create(payload)
        AppUI.toast('Transaction added successfully', 'success')
      }
      
      setShowModal(false)
      await loadData()
    } catch (error: any) {
      AppUI.toast(error.response?.data?.error || 'Failed to save transaction', 'error')
    } finally {
      setFormLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    const confirmed = await AppUI.confirm(
      'Delete transaction?',
      'This action cannot be undone.',
      { destructive: true, okLabel: 'Delete' }
    )

    if (!confirmed) return

    try {
      await transactionsApi.delete(id)
      AppUI.toast('Transaction deleted successfully', 'success')
      await loadData()
    } catch (error: any) {
      AppUI.toast(error.response?.data?.error || 'Failed to delete transaction', 'error')
    }
  }

  // Filter transactions
  const filteredTransactions = transactions.filter((txn) => {
    if (filters.search && !txn.description?.toLowerCase().includes(filters.search.toLowerCase())) {
      return false
    }
    if (filters.type && txn.transaction_type !== filters.type) return false
    if (filters.category && txn.category_id !== parseInt(filters.category)) return false
    if (filters.source && txn.source_id !== parseInt(filters.source)) return false
    if (filters.startDate && txn.transaction_date < filters.startDate) return false
    if (filters.endDate && txn.transaction_date > filters.endDate) return false
    return true
  })

  const formatAmount = (amount: number) => `$${(amount / 100).toFixed(2)}`

  return (
    <div className="p-8">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-neutral-200">
        <div>
          <h1 className="text-page-title text-neutral-950 mb-1">Transactions</h1>
          <p className="text-body text-neutral-600">
            Manage your income and expenses
          </p>
        </div>
        <Button
          variant="primary"
          icon={<Plus className="w-4 h-4" />}
          onClick={openAddModal}
        >
          Add Transaction
        </Button>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
          <div className="lg:col-span-2 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
            <Input
              placeholder="Search transactions..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="pl-9"
            />
          </div>
          <Select
            value={filters.type}
            onChange={(e) => setFilters({ ...filters, type: e.target.value })}
            options={[
              { value: '', label: 'All Types' },
              { value: 'income', label: 'Income' },
              { value: 'expense', label: 'Expense' },
            ]}
          />
          <Select
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
            options={[
              { value: '', label: 'All Categories' },
              ...categories.map((c) => ({ value: c.id.toString(), label: c.name })),
            ]}
          />
          <Input
            type="date"
            placeholder="Start date"
            value={filters.startDate}
            onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
          />
          <Input
            type="date"
            placeholder="End date"
            value={filters.endDate}
            onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
          />
        </div>
      </Card>

      {/* Transactions Table */}
      {loading ? (
        <Card>
          <div className="animate-pulse space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-12 bg-neutral-100 rounded" />
            ))}
          </div>
        </Card>
      ) : filteredTransactions.length === 0 ? (
        <EmptyState
          icon={<Receipt className="w-12 h-12" />}
          title="No transactions found"
          description={filters.search || filters.type ? 'Try adjusting your filters' : 'Add your first transaction to get started'}
          action={<Button variant="primary" icon={<Plus className="w-4 h-4" />} onClick={openAddModal}>Add Transaction</Button>}
        />
      ) : (
        <div className="bg-white border border-neutral-200 rounded overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-neutral-100 border-b border-neutral-200">
                <th className="text-label text-left px-4 py-3">Date</th>
                <th className="text-label text-left px-4 py-3">Description</th>
                <th className="text-label text-left px-4 py-3">Category</th>
                <th className="text-label text-left px-4 py-3">Source</th>
                <th className="text-label text-left px-4 py-3">Type</th>
                <th className="text-label text-right px-4 py-3">Amount</th>
                <th className="text-label text-right px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredTransactions.map((txn) => {
                const category = categories.find((c) => c.id === txn.category_id)
                const source = sources.find((s) => s.id === txn.source_id)
                return (
                  <tr key={txn.id} className="border-b border-neutral-200 hover:bg-neutral-50 last:border-0">
                    <td className="px-4 py-3 text-body-medium text-neutral-950">
                      {format(new Date(txn.transaction_date), 'MMM d, yyyy')}
                    </td>
                    <td className="px-4 py-3">
                      <p className="text-body-medium text-neutral-950">{txn.description}</p>
                      {txn.notes && (
                        <p className="text-caption text-neutral-600">{txn.notes}</p>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {category && <Badge variant="neutral">{category.name}</Badge>}
                    </td>
                    <td className="px-4 py-3 text-body text-neutral-600">
                      {source?.name || '-'}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={txn.transaction_type === 'income' ? 'success' : 'error'}>
                        {txn.transaction_type}
                      </Badge>
                    </td>
                    <td className={`px-4 py-3 text-right text-body-medium ${
                      txn.transaction_type === 'income' ? 'text-success' : 'text-error'
                    }`}>
                      {txn.transaction_type === 'income' ? '+' : '-'}
                      {formatAmount(txn.amount)}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          type="button"
                          onClick={() => openEditModal(txn)}
                          className="p-1.5 hover:bg-neutral-100 rounded transition-colors"
                          aria-label="Edit transaction"
                        >
                          <Edit2 className="w-4 h-4 text-neutral-600" />
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(txn.id)}
                          className="p-1.5 hover:bg-error-light rounded transition-colors"
                          aria-label="Delete transaction"
                        >
                          <Trash2 className="w-4 h-4 text-error" />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Add/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowModal(false)} />
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-5 border-b border-neutral-200">
              <h2 className="text-section-title text-neutral-950">
                {editingId ? 'Edit Transaction' : 'Add Transaction'}
              </h2>
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="p-1 hover:bg-neutral-100 rounded transition-colors"
                aria-label="Close"
              >
                <X className="w-5 h-5 text-neutral-600" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-5 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Input
                  id="transaction_date"
                  type="date"
                  label="Date"
                  value={formData.transaction_date}
                  onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                  error={formErrors.transaction_date}
                  required
                />
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  label="Amount ($)"
                  value={formData.amount || ''}
                  onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                  error={formErrors.amount}
                  required
                />
              </div>

              <Select
                id="transaction_type"
                label="Type"
                value={formData.transaction_type}
                onChange={(e) => setFormData({ ...formData, transaction_type: e.target.value as 'income' | 'expense' })}
                options={[
                  { value: 'expense', label: 'Expense' },
                  { value: 'income', label: 'Income' },
                ]}
              />

              <div className="grid grid-cols-2 gap-4">
                <Select
                  id="category_id"
                  label="Category"
                  value={formData.category_id?.toString() || ''}
                  onChange={(e) => setFormData({ ...formData, category_id: e.target.value ? parseInt(e.target.value) : null })}
                  options={[
                    { value: '', label: 'Select category' },
                    ...categories
                      .filter((c) => c.category_type === formData.transaction_type)
                      .map((c) => ({ value: c.id.toString(), label: c.name })),
                  ]}
                />
                <Select
                  id="source_id"
                  label="Source"
                  value={formData.source_id?.toString() || ''}
                  onChange={(e) => setFormData({ ...formData, source_id: e.target.value ? parseInt(e.target.value) : null })}
                  options={[
                    { value: '', label: 'Select source' },
                    ...sources.map((s) => ({ value: s.id.toString(), label: s.name })),
                  ]}
                />
              </div>

              <Input
                id="description"
                type="text"
                label="Description"
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                error={formErrors.description}
                placeholder="Enter a description"
                required
              />

              <div>
                <label htmlFor="notes" className="text-label text-neutral-800 block mb-1">
                  Notes
                </label>
                <textarea
                  id="notes"
                  value={formData.notes || ''}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full min-h-[80px] px-3 py-2 border border-neutral-200 rounded text-sm bg-white resize-vertical focus:border-accent focus:ring-2 focus:ring-accent-light transition-all duration-150"
                  placeholder="Add any additional notes"
                />
              </div>

              <div className="flex justify-end gap-2 pt-4 border-t border-neutral-200">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  loading={formLoading}
                >
                  {editingId ? 'Update' : 'Add'} Transaction
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Transactions
