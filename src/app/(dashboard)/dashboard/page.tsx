'use client'

import { useEffect, useState } from 'react'
import { useAuthStore } from '@/store/auth-store'
import { supabase } from '@/lib/supabase'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Package, TrendingUp, CreditCard, BarChart3 } from 'lucide-react'
import { Product, Forecast } from '@/types'

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [products, setProducts] = useState<Product[]>([])
  const [forecasts, setForecasts] = useState<Forecast[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user) {
      loadDashboardData()
    }
  }, [user])

  const loadDashboardData = async () => {
    try {
      const [productsRes, forecastsRes] = await Promise.all([
        supabase.from('products').select('*').eq('user_id', user?.id).limit(5),
        supabase.from('forecasts').select('*').eq('user_id', user?.id).limit(5),
      ])

      if (productsRes.data) setProducts(productsRes.data as Product[])
      if (forecastsRes.data) setForecasts(forecastsRes.data as Forecast[])
    } catch (error) {
      console.error('Error loading dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-600">Loading...</div>
      </div>
    )
  }

  const completedForecasts = forecasts.filter(f => f.status === 'completed').length
  const averageConfidence = forecasts.length > 0
    ? Math.round(forecasts.reduce((sum, f) => sum + (f.confidence_level || 0), 0) / forecasts.length)
    : 0

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Welcome back, {user?.full_name}!</h1>
        <p className="text-slate-600 mt-2">Here is your commerce intelligence overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Total Products</CardTitle>
            <Package className="h-4 w-4 text-slate-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{products.length}</div>
            <p className="text-xs text-slate-600 mt-1">Active in catalog</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Forecasts</CardTitle>
            <TrendingUp className="h-4 w-4 text-slate-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completedForecasts}</div>
            <p className="text-xs text-slate-600 mt-1">Completed analyses</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Credits Remaining</CardTitle>
            <CreditCard className="h-4 w-4 text-slate-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{user?.forecast_credits_remaining || 0}</div>
            <p className="text-xs text-slate-600 mt-1">Forecast credits</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Avg Confidence</CardTitle>
            <BarChart3 className="h-4 w-4 text-slate-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{averageConfidence}%</div>
            <p className="text-xs text-slate-600 mt-1">Forecast accuracy</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Products</CardTitle>
          </CardHeader>
          <CardContent>
            {products.length === 0 ? (
              <p className="text-slate-600 text-sm">No products yet. Create your first product to get started!</p>
            ) : (
              <div className="space-y-4">
                {products.map((product) => (
                  <div key={product.id} className="flex items-center justify-between border-b pb-3 last:border-0">
                    <div>
                      <div className="font-medium">{product.name}</div>
                      <div className="text-sm text-slate-600">{product.category}</div>
                    </div>
                    <Badge variant={product.is_active ? 'default' : 'secondary'}>
                      {product.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Forecasts</CardTitle>
          </CardHeader>
          <CardContent>
            {forecasts.length === 0 ? (
              <p className="text-slate-600 text-sm">No forecasts yet. Create a forecast to see AI insights!</p>
            ) : (
              <div className="space-y-4">
                {forecasts.map((forecast) => (
                  <div key={forecast.id} className="flex items-center justify-between border-b pb-3 last:border-0">
                    <div>
                      <div className="font-medium">Forecast Analysis</div>
                      <div className="text-sm text-slate-600">
                        {forecast.status === 'completed' && forecast.confidence_level
                          ? `Confidence: ${forecast.confidence_level}%`
                          : 'Processing...'}
                      </div>
                    </div>
                    <Badge
                      variant={
                        forecast.status === 'completed' ? 'default' :
                        forecast.status === 'failed' ? 'destructive' : 'secondary'
                      }
                    >
                      {forecast.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex items-start space-x-4">
            <div className="bg-blue-100 rounded-full p-3">
              <BarChart3 className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-blue-900">Current Plan: {user?.subscription_tier?.toUpperCase()}</h3>
              <p className="text-blue-800 text-sm mt-1">
                You have {user?.forecast_credits_remaining || 0} forecast credits remaining this month.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
