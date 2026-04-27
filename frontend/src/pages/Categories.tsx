import React, { useEffect, useState } from 'react'
import { categoriesApi } from '@/lib/api'
import { Category, CategoryCreate } from '@/types/api'
import { AppUI } from '@/store/uiStore'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Select from '@/components/ui/Select'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import EmptyState from '@/components/ui/EmptyState'
import { Plus, Tag, Edit2, Trash2, X } from 'lucide-react'

const Categories: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  
  const [formData, setFormData] = useState<CategoryCreate>({
    name: '',
    category_type: 'expense',
    description: '',
    parent_id: null,
  })
  const [formErrors, setFormErrors] = useState<Record<string, string>>({})
  const [formLoading, setFormLoading] = useState(false)

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    try {
      setLoading(true)
      const data = await categoriesApi.getAll()
      setCategories(data)
    } catch (error: any) {
      AppUI.toast(error.response?.data?.error || 'Failed to load categories', 'error')
    } finally {
      setLoading(false)
    }
  }

  const openAddModal = () => {
    setEditingId(null)
    setFormData({
      name: '',
      category_type: 'expense',
      description: '',
      parent_id: null,
    })
    setFormErrors({})
    setShowModal(true)
  }

  const openEditModal = (category: Category) => {
    setEditingId(category.id)
    setFormData({
      name: category.name,
      category_type: category.category_type,
      description: category.description || '',
      parent_id: category.parent_id,
    })
    setFormErrors({})
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormErrors({})

    const errors: Record<string, string> = {}
    if (!formData.name.trim()) errors.name = 'Name is required'

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors)
      return
    }

    setFormLoading(true)
    try {
      if (editingId) {
        await categoriesApi.update(editingId, formData)
        AppUI.toast('Category updated successfully', 'success')
      } else {
        await categoriesApi.create(formData)
        AppUI.toast('Category created successfully', 'success')
      }
      
      setShowModal(false)
      await loadCategories()
    } catch (error: any) {
      AppUI.toast(error.response?.data?.error || 'Failed to save category', 'error')
    } finally {
      setFormLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    const confirmed = await AppUI.confirm(
      'Delete category?',
      'This action cannot be undone. Transactions using this category will not be deleted.',
      { destructive: true, okLabel: 'Delete' }
    )

    if (!confirmed) return

    try {
      await categoriesApi.delete(id)
      AppUI.toast('Category deleted successfully', 'success')
      await loadCategories()
    } catch (error: any) {
      AppUI.toast(error.response?.data?.error || 'Failed to delete category', 'error')
    }
  }

  const expenseCategories = categories.filter((c) => c.category_type === 'expense')
  const incomeCategories = categories.filter((c) => c.category_type === 'income')

  const CategorySection = ({ title, items, type }: { title: string; items: Category[]; type: 'income' | 'expense' }) => (
    <div>
      <h2 className="text-section-title text-neutral-950 mb-4">{title}</h2>
      {items.length === 0 ? (
        <Card>
          <p className="text-body text-neutral-600 text-center py-8">
            No {type} categories yet
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((category) => (
            <Card key={category.id} hover>
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={`w-8 h-8 rounded flex items-center justify-center ${
                    type === 'income' ? 'bg-success-light' : 'bg-error-light'
                  }`}>
                    <Tag className={`w-4 h-4 ${type === 'income' ? 'text-success' : 'text-error'}`} />
                  </div>
                  <h3 className="text-card-title text-neutral-950">{category.name}</h3>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => openEditModal(category)}
                    className="p-1.5 hover:bg-neutral-100 rounded transition-colors"
                    aria-label="Edit category"
                  >
                    <Edit2 className="w-4 h-4 text-neutral-600" />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDelete(category.id)}
                    className="p-1.5 hover:bg-error-light rounded transition-colors"
                    aria-label="Delete category"
                  >
                    <Trash2 className="w-4 h-4 text-error" />
                  </button>
                </div>
              </div>
              {category.description && (
                <p className="text-caption text-neutral-600 mb-2">{category.description}</p>
              )}
              <Badge variant={type === 'income' ? 'success' : 'error'}>
                {type}
              </Badge>
            </Card>
          ))}
        </div>
      )}
    </div>
  )

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-neutral-200">
        <div>
          <h1 className="text-page-title text-neutral-950 mb-1">Categories</h1>
          <p className="text-body text-neutral-600">
            Organize your transactions into categories
          </p>
        </div>
        <Button
          variant="primary"
          icon={<Plus className="w-4 h-4" />}
          onClick={openAddModal}
        >
          Add Category
        </Button>
      </div>

      {loading ? (
        <div className="space-y-8">
          {[1, 2].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-6 bg-neutral-100 rounded w-32 mb-4" />
              <div className="grid grid-cols-3 gap-4">
                {[1, 2, 3].map((j) => (
                  <div key={j} className="h-32 bg-neutral-100 rounded" />
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : categories.length === 0 ? (
        <EmptyState
          icon={<Tag className="w-12 h-12" />}
          title="No categories yet"
          description="Create categories to organize your transactions"
          action={<Button variant="primary" icon={<Plus className="w-4 h-4" />} onClick={openAddModal}>Add Category</Button>}
        />
      ) : (
        <div className="space-y-8">
          <CategorySection title="Expense Categories" items={expenseCategories} type="expense" />
          <CategorySection title="Income Categories" items={incomeCategories} type="income" />
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowModal(false)} />
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-md">
            <div className="flex items-center justify-between p-5 border-b border-neutral-200">
              <h2 className="text-section-title text-neutral-950">
                {editingId ? 'Edit Category' : 'Add Category'}
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
                placeholder="e.g., Groceries, Salary"
                required
              />

              <Select
                id="category_type"
                label="Type"
                value={formData.category_type}
                onChange={(e) => setFormData({ ...formData, category_type: e.target.value as 'income' | 'expense' })}
                options={[
                  { value: 'expense', label: 'Expense' },
                  { value: 'income', label: 'Income' },
                ]}
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
                  {editingId ? 'Update' : 'Create'} Category
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Categories
