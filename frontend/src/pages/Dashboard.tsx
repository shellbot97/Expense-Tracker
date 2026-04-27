import React, { useEffect, useState } from 'react'
import { transactionsApi, categoriesApi } from '@/lib/api'
import { Transaction, Category } from '@/types/api'
import { AppUI } from '@/store/uiStore'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import { TrendingUp, TrendingDown, Wallet, Receipt, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { format, startOfMonth, endOfMonth } from 'date-fns'

const Dashboard: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const startDate = format(startOfMonth(new Date()), 'yyyy-MM-dd')
      const endDate = format(endOfMonth(new Date()), 'yyyy-MM-dd')
      
      const [txns, cats] = await Promise.all([
        transactionsApi.getAll({ start_date: startDate, end_date: endDate }),
        categoriesApi.getAll(),
      ])
      
      setTransactions(txns)
      setCategories(cats)
    } catch (error: any) {
      AppUI.toast(error.response?.data?.error || 'Failed to load dashboard data', 'error')
    } finally {
      setLoading(false)
    }
  }

  // Calculate summary metrics
  const totalIncome = transactions
    .filter((t) => t.transaction_type === 'income')
    .reduce((sum, t) => sum + t.amount, 0)

  const totalExpenses = transactions
    .filter((t) => t.transaction_type === 'expense')
    .reduce((sum, t) => sum + t.amount, 0)

  const netBalance = totalIncome - totalExpenses

  // Group expenses by category
  const expensesByCategory = transactions
    .filter((t) => t.transaction_type === 'expense' && t.category_id)
    .reduce((acc, t) => {
      const categoryId = t.category_id!
      acc[categoryId] = (acc[categoryId] || 0) + t.amount
      return acc
    }, {} as Record<number, number>)

  const topCategories = Object.entries(expensesByCategory)
    .map(([catId, amount]) => ({
      category: categories.find((c) => c.id === parseInt(catId)),
      amount,
    }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 5)

  // Recent transactions
  const recentTransactions = [...transactions]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)

  const formatAmount = (amount: number) => {
    return `$${(amount / 100).toFixed(2)}`
  }

  if (loading) {
    return (
      <div className="animate-pulse p-8">
        <div className="h-8 bg-neutral-100 rounded w-48 mb-6"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 bg-neutral-100 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-page-title text-neutral-950 mb-1">Dashboard</h1>
        <p className="text-body text-neutral-600">
          Overview for {format(new Date(), 'MMMM yyyy')}
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className="text-label text-neutral-600 mb-1">Total Income</p>
              <p className="text-2xl font-semibold text-success">{formatAmount(totalIncome)}</p>
            </div>
            <div className="w-10 h-10 rounded bg-success-light flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-success" />
            </div>
          </div>
          <p className="text-caption text-neutral-600 mt-2">
            {transactions.filter((t) => t.transaction_type === 'income').length} transactions
          </p>
        </Card>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className="text-label text-neutral-600 mb-1">Total Expenses</p>
              <p className="text-2xl font-semibold text-error">{formatAmount(totalExpenses)}</p>
            </div>
            <div className="w-10 h-10 rounded bg-error-light flex items-center justify-center">
              <TrendingDown className="w-5 h-5 text-error" />
            </div>
          </div>
          <p className="text-caption text-neutral-600 mt-2">
            {transactions.filter((t) => t.transaction_type === 'expense').length} transactions
          </p>
        </Card>

        <Card>
          <div className="flex items-start justify-between">
            <div>
              <p className="text-label text-neutral-600 mb-1">Net Balance</p>
              <p className={`text-2xl font-semibold ${netBalance >= 0 ? 'text-success' : 'text-error'}`}>
                {formatAmount(netBalance)}
              </p>
            </div>
            <div className="w-10 h-10 rounded bg-info-light flex items-center justify-center">
              <Wallet className="w-5 h-5 text-info" />
            </div>
          </div>
          <p className="text-caption text-neutral-600 mt-2">
            Current month balance
          </p>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Spending Categories */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-section-title text-neutral-950">Top Spending Categories</h2>
          </div>

          {topCategories.length === 0 ? (
            <p className="text-body text-neutral-600 text-center py-8">
              No expense data for this month
            </p>
          ) : (
            <div className="space-y-3">
              {topCategories.map(({ category, amount }) => (
                <div key={category?.id} className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1">
                    <div className="w-10 h-10 rounded bg-primary-light flex items-center justify-center">
                      <Receipt className="w-5 h-5 text-primary" />
                    </div>
                    <div className="flex-1">
                      <p className="text-body-medium text-neutral-950">
                        {category?.name || 'Uncategorized'}
                      </p>
                      <div className="mt-1 bg-neutral-100 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-primary h-full"
                          style={{
                            width: `${(amount / totalExpenses) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                  <div className="text-right ml-4">
                    <p className="text-body-medium text-neutral-950">{formatAmount(amount)}</p>
                    <p className="text-caption text-neutral-600">
                      {((amount / totalExpenses) * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Recent Transactions */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-section-title text-neutral-950">Recent Transactions</h2>
          </div>

          {recentTransactions.length === 0 ? (
            <p className="text-body text-neutral-600 text-center py-8">
              No transactions yet
            </p>
          ) : (
            <div className="space-y-2">
              {recentTransactions.map((txn) => {
                const category = categories.find((c) => c.id === txn.category_id)
                return (
                  <div
                    key={txn.id}
                    className="flex items-center justify-between py-2 border-b border-neutral-200 last:border-0"
                  >
                    <div className="flex items-center gap-3">
                      {txn.transaction_type === 'income' ? (
                        <ArrowUpRight className="w-4 h-4 text-success" />
                      ) : (
                        <ArrowDownRight className="w-4 h-4 text-error" />
                      )}
                      <div>
                        <p className="text-body-medium text-neutral-950">
                          {txn.description || 'No description'}
                        </p>
                        <div className="flex items-center gap-2 mt-0.5">
                          {category && (
                            <Badge variant="neutral" className="text-xs">
                              {category.name}
                            </Badge>
                          )}
                          <span className="text-caption text-neutral-600">
                            {format(new Date(txn.transaction_date), 'MMM d, yyyy')}
                          </span>
                        </div>
                      </div>
                    </div>
                    <p
                      className={`text-body-medium ${
                        txn.transaction_type === 'income' ? 'text-success' : 'text-error'
                      }`}
                    >
                      {txn.transaction_type === 'income' ? '+' : '-'}
                      {formatAmount(txn.amount)}
                    </p>
                  </div>
                )
              })}
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}

export default Dashboard
