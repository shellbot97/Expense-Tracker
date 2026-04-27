import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { authApi } from '@/lib/api'
import { AppUI } from '@/store/uiStore'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import { UserPlus } from 'lucide-react'

const Register: React.FC = () => {
  const navigate = useNavigate()
  const setToken = useAuthStore((state) => state.setToken)
  const [formData, setFormData] = useState({ username: '', email: '', password: '', confirmPassword: '' })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrors({})

    // Validation
    const newErrors: Record<string, string> = {}
    if (!formData.username) newErrors.username = 'Username is required'
    if (!formData.email) newErrors.email = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Email is invalid'
    if (!formData.password) newErrors.password = 'Password is required'
    else if (formData.password.length < 8) newErrors.password = 'Password must be at least 8 characters'
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    setLoading(true)
    try {
      const { confirmPassword, ...registerData } = formData
      const response = await authApi.register(registerData)
      setToken(response.access_token)
      AppUI.toast('Account created successfully!', 'success')
      navigate('/dashboard')
    } catch (error: any) {
      const message = error.response?.data?.error || 'Registration failed. Please try again.'
      AppUI.toast(message, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-page-title text-neutral-950 mb-2">Create Account</h1>
          <p className="text-body text-neutral-600">Start tracking your expenses today</p>
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
              placeholder="Choose a username"
              autoComplete="username"
            />

            <Input
              id="email"
              type="email"
              label="Email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              error={errors.email}
              placeholder="your@email.com"
              autoComplete="email"
            />

            <Input
              id="password"
              type="password"
              label="Password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              error={errors.password}
              placeholder="Minimum 8 characters"
              autoComplete="new-password"
              helperText="Use at least 8 characters"
            />

            <Input
              id="confirmPassword"
              type="password"
              label="Confirm Password"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              error={errors.confirmPassword}
              placeholder="Re-enter your password"
              autoComplete="new-password"
            />

            <Button
              type="submit"
              variant="primary"
              className="w-full"
              loading={loading}
              icon={<UserPlus className="w-4 h-4" />}
            >
              Create Account
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-caption text-neutral-600">
              Already have an account?{' '}
              <Link to="/login" className="text-accent hover:underline font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Register
