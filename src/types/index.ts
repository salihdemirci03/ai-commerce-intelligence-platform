export interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
  is_verified: boolean
  subscription_tier: 'basic' | 'pro' | 'master'
  subscription_status: 'active' | 'inactive' | 'cancelled' | 'past_due'
  forecast_credits_remaining: number
  created_at: string
}

export interface Product {
  id: string
  user_id: string
  name: string
  description?: string
  category: string
  base_price: number
  production_method?: 'self' | 'fason' | 'dropship' | 'wholesale'
  target_market?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Forecast {
  id: string
  user_id: string
  product_id: string
  target_city_id?: string
  demand_score?: number
  competition_index?: number
  profitability_score?: number
  expected_sales_volume?: number
  recommended_price?: number
  confidence_level?: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error_message?: string
  processing_started_at?: string
  processing_completed_at?: string
  created_at: string
}

export interface City {
  id: string
  name: string
  country: string
  region?: string
  population: number
  gdp_per_capita?: number
  ecommerce_penetration?: number
  purchasing_power_index?: number
}

export interface Subscription {
  id: string
  user_id: string
  stripe_subscription_id?: string
  plan_type: 'basic' | 'pro' | 'master'
  status: 'active' | 'cancelled' | 'past_due' | 'trialing' | 'incomplete'
  current_period_start: string
  current_period_end: string
  cancel_at_period_end: boolean
  cancelled_at?: string
  created_at: string
  updated_at: string
}

export interface SubscriptionPlan {
  id: string
  name: string
  price: number
  currency: string
  interval: string
  features: string[]
}
