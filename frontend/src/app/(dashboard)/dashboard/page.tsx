'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Package, TrendingUp, Target, Plus } from 'lucide-react'
import apiClient from '@/lib/api-client'

export default function DashboardPage() {
  const [stats, setStats] = useState({
    productsCount: 0,
    forecastsCount: 0,
    creditsRemaining: 50,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const [productsRes, forecastsRes] = await Promise.all([
        apiClient.get('/api/v1/products'),
        apiClient.get('/api/v1/forecasts'),
      ])

      setStats({
        productsCount: productsRes.data.total || 0,
        forecastsCount: forecastsRes.data.total || 0,
        creditsRemaining: 50,
      })
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-slate-600 mt-2">Welcome back! Here&apos;s your overview.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Products</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.productsCount}</div>
            <p className="text-xs text-muted-foreground">Active products in your catalog</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Forecasts</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.forecastsCount}</div>
            <p className="text-xs text-muted-foreground">Market analyses completed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Credits Remaining</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.creditsRemaining}</div>
            <p className="text-xs text-muted-foreground">Forecasts available this month</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Start analyzing your products</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link href="/products">
              <Button className="w-full justify-start">
                <Plus className="h-4 w-4 mr-2" />
                Add New Product
              </Button>
            </Link>
            <Link href="/forecast">
              <Button variant="outline" className="w-full justify-start">
                <TrendingUp className="h-4 w-4 mr-2" />
                Create Forecast
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
            <CardDescription>Learn how to use the platform</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">1.</span>
                <span>Add your products with detailed descriptions</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">2.</span>
                <span>Create forecasts to analyze market potential</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">3.</span>
                <span>Review insights and implement strategies</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
