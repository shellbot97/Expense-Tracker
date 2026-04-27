import { create } from 'zustand'

interface AuthState {
  accessToken: string | null
  isAuthenticated: boolean
  setToken: (token: string) => void
  clearToken: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  setToken: (token: string) => {
    localStorage.setItem('access_token', token)
    set({ accessToken: token, isAuthenticated: true })
  },
  clearToken: () => {
    localStorage.removeItem('access_token')
    set({ accessToken: null, isAuthenticated: false })
  },
}))
