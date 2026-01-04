'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/store/auth-store'
import { Button } from '@/components/ui/button'
import { BarChart3, Home, Package, TrendingUp, LogOut, User } from 'lucide-react'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { isAuthenticated, user, logout, fetchUser } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
    } else {
      fetchUser()
    }
  }, [isAuthenticated, router, fetchUser])

  const handleLogout = () => {
    logout()
    router.push('/')
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-slate-900">Commerce Intelligence</span>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-slate-600">{user?.email}</span>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="flex gap-8">
          <aside className="w-64 flex-shrink-0">
            <nav className="space-y-2">
              <Link href="/dashboard">
                <Button variant="ghost" className="w-full justify-start">
                  <Home className="h-4 w-4 mr-2" />
                  Dashboard
                </Button>
              </Link>
              <Link href="/products">
                <Button variant="ghost" className="w-full justify-start">
                  <Package className="h-4 w-4 mr-2" />
                  Products
                </Button>
              </Link>
              <Link href="/forecast">
                <Button variant="ghost" className="w-full justify-start">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Forecasts
                </Button>
              </Link>
            </nav>
          </aside>

          <main className="flex-1">{children}</main>
        </div>
      </div>
    </div>
  )
}
