export interface User {
  id: number
  username: string
  email: string
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface Category {
  id: number
  user_id: number
  name: string
  category_type: 'income' | 'expense'
  parent_id?: number | null
  description?: string | null
  created_at: string
  updated_at: string
}

export interface CategoryCreate {
  name: string
  category_type: 'income' | 'expense'
  parent_id?: number | null
  description?: string | null
}

export interface Source {
  id: number
  user_id: number
  name: string
  source_type: string
  description?: string | null
  created_at: string
  updated_at: string
}

export interface SourceCreate {
  name: string
  source_type: string
  description?: string | null
}

export interface Transaction {
  id: number
  user_id: number
  source_id?: number | null
  category_id?: number | null
  transaction_date: string
  amount: number
  transaction_type: 'income' | 'expense'
  description?: string | null
  notes?: string | null
  created_at: string
  updated_at: string
}

export interface TransactionCreate {
  source_id?: number | null
  category_id?: number | null
  transaction_date: string
  amount: number
  transaction_type: 'income' | 'expense'
  description?: string | null
  notes?: string | null
}

export interface Budget {
  id: number
  user_id: number
  category_id: number
  amount: number
  period: string
  start_date: string
  end_date?: string | null
  created_at: string
  updated_at: string
}

export interface BudgetCreate {
  category_id: number
  amount: number
  period: string
  start_date: string
  end_date?: string | null
}

export interface TransactionFilters {
  start_date?: string
  end_date?: string
  category_id?: number
  source_id?: number
  transaction_type?: 'income' | 'expense'
  min_amount?: number
  max_amount?: number
  skip?: number
  limit?: number
}

export interface ApiError {
  error: string
}
