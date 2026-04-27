import React, { useEffect, useState } from 'react'
import { sourcesApi } from '@/lib/api'
import { Source, SourceCreate } from '@/types/api'
import { AppUI } from '@/store/uiStore'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Select from '@/components/ui/Select'
import Card from '@/components/ui/Card'
import EmptyState from '@/components/ui/EmptyState'
import { Plus, FolderOpen, Edit2, Trash2, X } from 'lucide-react'
import { format } from 'date-fns'

const Sources: React.FC = () => {
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  
  const [formData, setFormData] = useState<SourceCreate>({
    name: '',
    source_type: 'bank',
    description: '',
  })
  const [formErrors, setFormErrors] = useState<Record<string, string>>({})
  const [formLoading, setFormLoading] = useState(false)

  useEffect(() => {
    loadSources()
  }, [])

  const loadSources = async () => {
    try {
      setLoading(true)
      const data = await sourcesApi.getAll()
      setSources(data)
    } catch (error: any) {
      AppUI.toast(error.response?.data?.error || 'Failed to load sources', 'error')
    } finally {
      setLoading(false)
    }
  }

  const openAddModal = () => {
    setEditingId(null)
    setFormData({
      name: '',
      source_type: 'bank',
      description: '',
    })
    setFormErrors({})
    setShowModal(true)
  }

  const openEditModal = (source: Source) => {
    setEditingId(source.id)
    setFormData({
      name: source.name,
      source_type: source.source_type,
      description: source.description || '',
    })
    setFormErrors({})
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormErrors({})

    const errors: Record<string, string> = {}
    if (!formData.name.trim()) errors.name = 'Name is required'
    if (!formData.source_type.trim()) errors.source_type = 'Type is required'

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors)
      return
    }

    setFormLoading(true)
    try {
      if (editingId) {
        await sourcesApi.update(editingId, formData)
        AppUI.toast('Source updated successfully', 'success')
      } else {
        await sourcesApi.create(formData)
        AppUI.toast('Source created successfully', 'success')
      }
      
      setShowModal(false)
      await loadSources()
    } catch (error: any) {
      AppUI.toast(error.response?.data?.error || 'Failed to save source', 'error')
    } finally {
      setFormLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    const confirmed = await AppUI.confirm(
      'Delete source?',
      'This action cannot be undone. Transactions using this source will not be deleted.',
      { destructive: true, okLabel: 'Delete' }
    )

    if (!confirmed) return

    try {
      await sourcesApi.delete(id)
      AppUI.toast('Source deleted successfully', 'success')
      await loadSources()
    } catch (error: any) {
      AppUI.toast(error.response?.data?.error || 'Failed to delete source', 'error')
    }
  }

  const sourceTypes = [
    { value: 'bank', label: 'Bank Account' },
    { value: 'credit_card', label: 'Credit Card' },
    { value: 'cash', label: 'Cash' },
    { value: 'investment', label: 'Investment' },
    { value: 'other', label: 'Other' },
  ]

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-neutral-200">
        <div>
          <h1 className="text-page-title text-neutral-950 mb-1">Sources</h1>
          <p className="text-body text-neutral-600">
            Manage your financial accounts and sources
          </p>
        </div>
        <Button
          variant="primary"
          icon={<Plus className="w-4 h-4" />}
          onClick={openAddModal}
        >
          Add Source
        </Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 bg-neutral-100 rounded animate-pulse" />
          ))}
        </div>
      ) : sources.length === 0 ? (
        <EmptyState
          icon={<FolderOpen className="w-12 h-12" />}
          title="No sources yet"
          description="Add sources like bank accounts, credit cards, or cash"
          action={<Button variant="primary" icon={<Plus className="w-4 h-4" />} onClick={openAddModal}>Add Source</Button>}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sources.map((source) => (
            <Card key={source.id} hover>
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded bg-info-light flex items-center justify-center">
                    <FolderOpen className="w-4 h-4 text-info" />
                  </div>
                  <h3 className="text-card-title text-neutral-950">{source.name}</h3>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => openEditModal(source)}
                    className="p-1.5 hover:bg-neutral-100 rounded transition-colors"
                    aria-label="Edit source"
                  >
                    <Edit2 className="w-4 h-4 text-neutral-600" />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDelete(source.id)}
                    className="p-1.5 hover:bg-error-light rounded transition-colors"
                    aria-label="Delete source"
                  >
                    <Trash2 className="w-4 h-4 text-error" />
                  </button>
                </div>
              </div>
              <p className="text-caption text-neutral-600 mb-2">
                {sourceTypes.find((t) => t.value === source.source_type)?.label || source.source_type}
              </p>
              {source.description && (
                <p className="text-caption text-neutral-600 mb-2">{source.description}</p>
              )}
              <p className="text-caption text-neutral-400">
                Added {format(new Date(source.created_at), 'MMM d, yyyy')}
              </p>
            </Card>
          ))}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowModal(false)} />
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-md">
            <div className="flex items-center justify-between p-5 border-b border-neutral-200">
              <h2 className="text-section-title text-neutral-950">
                {editingId ? 'Edit Source' : 'Add Source'}
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
              <Input
                id="name"
                type="text"
                label="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                error={formErrors.name}
                placeholder="e.g., Chase Checking, Amex Card"
                required
              />

              <Select
                id="source_type"
                label="Type"
                value={formData.source_type}
                onChange={(e) => setFormData({ ...formData, source_type: e.target.value })}
                error={formErrors.source_type}
                options={sourceTypes}
              />

              <div>
                <label htmlFor="description" className="text-label text-neutral-800 block mb-1">
                  Description
                </label>
                <textarea
                  id="description"
                  value={formData.description || ''}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full min-h-[80px] px-3 py-2 border border-neutral-200 rounded text-sm bg-white resize-vertical focus:border-accent focus:ring-2 focus:ring-accent-light transition-all duration-150"
                  placeholder="Optional description"
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
                  {editingId ? 'Update' : 'Create'} Source
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Sources
