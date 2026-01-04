'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, AlertCircle } from 'lucide-react'
import apiClient from '@/lib/api-client'
import { Forecast } from '@/types'
import { formatDate } from '@/lib/utils'

export default function ForecastPage() {
  const [forecasts, setForecasts] = useState<Forecast[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadForecasts()
  }, [])

  const loadForecasts = async () => {
    try {
      const response = await apiClient.get('/api/v1/forecasts')
      setForecasts(response.data.forecasts || [])
    } catch (error) {
      console.error('Failed to load forecasts:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      completed: 'default',
      processing: 'secondary',
      pending: 'outline',
      failed: 'destructive',
    }
    return variants[status] || 'default'
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Forecasts</h1>
        <p className="text-slate-600 mt-2">View and manage your market forecasts</p>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading forecasts...</div>
      ) : forecasts.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <TrendingUp className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No forecasts yet</h3>
            <p className="text-slate-600 mb-4">Create your first forecast to analyze market potential</p>
            <p className="text-sm text-slate-500">You need to add products first before creating forecasts</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {forecasts.map((forecast) => (
            <Card key={forecast.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle>Forecast Analysis</CardTitle>
                    <CardDescription>Created {formatDate(forecast.created_at)}</CardDescription>
                  </div>
                  <Badge variant={getStatusBadge(forecast.status)}>
                    {forecast.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                {forecast.status === 'completed' && (
                  <div className="grid md:grid-cols-4 gap-4">
                    <div>
                      <div className="text-sm text-slate-600">Demand Score</div>
                      <div className="text-2xl font-bold text-green-600">
                        {forecast.demand_score || 0}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-slate-600">Competition</div>
                      <div className="text-2xl font-bold text-orange-600">
                        {forecast.competition_index || 0}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-slate-600">Profitability</div>
                      <div className="text-2xl font-bold text-blue-600">
                        {forecast.profitability_score || 0}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-slate-600">Expected Sales</div>
                      <div className="text-2xl font-bold">
                        {forecast.expected_sales_volume || 0}
                      </div>
                    </div>
                  </div>
                )}
                {forecast.status === 'failed' && (
                  <div className="flex items-center gap-2 text-red-600">
                    <AlertCircle className="h-4 w-4" />
                    <span className="text-sm">{forecast.error_message || 'Forecast failed'}</span>
                  </div>
                )}
                {forecast.status === 'processing' && (
                  <div className="text-sm text-slate-600">Analysis in progress...</div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
