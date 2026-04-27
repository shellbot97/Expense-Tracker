import React from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { 
  LayoutDashboard, 
  Receipt, 
  FolderOpen, 
  Tag, 
  Wallet,
  LogOut 
} from 'lucide-react'
import Toast from '@/components/ui/Toast'
import ConfirmDialog from '@/components/ui/ConfirmDialog'
import LoadingOverlay from '@/components/ui/LoadingOverlay'

const Layout: React.FC = () => {
  const clearToken = useAuthStore((state) => state.clearToken)

  const handleLogout = () => {
    clearToken()
  }

  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/transactions', icon: Receipt, label: 'Transactions' },
    { to: '/categories', icon: Tag, label: 'Categories' },
    { to: '/sources', icon: FolderOpen, label: 'Sources' },
    { to: '/budgets', icon: Wallet, label: 'Budgets' },
  ]

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation Bar */}
      <nav className="bg-secondary h-14 sticky top-0 z-40 border-b border-secondary-hover">
        <div className="h-full px-8 flex items-center">
          <div className="flex items-center gap-8">
            <h1 className="text-white font-headline text-lg font-semibold">
              Expense Tracker
            </h1>
            <div className="flex items-center gap-1">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-3 h-14 text-sm font-medium text-white/90 hover:bg-white/10 transition-colors relative ${
                      isActive ? 'text-white' : ''
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      <item.icon className="w-4 h-4" />
                      <span>{item.label}</span>
                      {isActive && (
                        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
                      )}
                    </>
                  )}
                </NavLink>
              ))}
            </div>
          </div>
          <div className="ml-auto">
            <button
              type="button"
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 h-9 text-sm font-medium text-white/90 hover:bg-white/10 rounded transition-colors"
              aria-label="Logout"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 bg-white">
        <Outlet />
      </main>

      {/* Global UI Components */}
      <Toast />
      <ConfirmDialog />
      <LoadingOverlay />
    </div>
  )
}

export default Layout
