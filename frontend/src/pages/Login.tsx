import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { authApi } from '@/lib/api'
import { AppUI } from '@/store/uiStore'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import { LogIn } from 'lucide-react'

const Login: React.FC = () => {
  const navigate = useNavigate()
  const setToken = useAuthStore((state) => state.setToken)
  const [formData, setFormData] = useState({ username: '', password: '' })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrors({})

    // Validation
    const newErrors: Record<string, string> = {}
    if (!formData.username) newErrors.username = 'Username is required'
    if (!formData.password) newErrors.password = 'Password is required'

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    setLoading(true)
    try {
      const response = await authApi.login(formData)
      setToken(response.access_token)
      AppUI.toast('Login successful!', 'success')
      navigate('/dashboard')
    } catch (error: any) {
      const message = error.response?.data?.error || 'Login failed. Please check your credentials.'
      AppUI.toast(message, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-page-title text-neutral-950 mb-2">Expense Tracker</h1>
          <p className="text-body text-neutral-600">Sign in to manage your expenses</p>
        </div>

        <div className="bg-white border border-neutral-200 rounded-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              id="username"
              type="text"
              label="Username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              error={errors.username}
              placeholder="Enter your username"
              autoComplete="username"
            />

            <Input
              id="password"
              type="password"
              label="Password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              error={errors.password}
              placeholder="Enter your password"
              autoComplete="current-password"
            />

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              loading={loading}
              icon={<LogIn className="w-4 h-4" />}
            >
              Sign In
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-caption text-neutral-600">
              Don't have an account?{' '}
              <Link to="/register" className="text-accent hover:underline font-medium">
                Create account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
