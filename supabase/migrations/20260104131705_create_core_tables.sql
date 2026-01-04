/*
  # Commerce Intelligence Platform - Core Database Schema

  ## Overview
  Creates the foundational database schema for the AI-Commerce Intelligence Platform,
  including user management, product catalog, forecasting system, city data, and audit logs.

  ## Tables Created

  ### 1. users
  - Core user account information
  - Subscription tier tracking (basic/pro/master)
  - Email verification and authentication
  - Created/updated timestamps

  ### 2. products
  - User-submitted product information
  - Product categorization and pricing
  - Production method tracking
  - Links to user accounts

  ### 3. cities
  - Global city database for market analysis
  - Demographic and economic indicators
  - E-commerce penetration metrics
  - Purchasing power indices

  ### 4. forecasts
  - AI-generated market forecasts
  - City-product demand predictions
  - Competition and profitability scores
  - Processing status tracking

  ### 5. agent_logs
  - AI agent execution tracking
  - Performance metrics and token usage
  - Input/output data for debugging
  - Execution time monitoring

  ### 6. subscriptions
  - Stripe subscription management
  - Plan tier tracking
  - Billing period management
  - Subscription status monitoring

  ### 7. payments
  - Transaction history
  - Stripe payment tracking
  - Deep report purchases
  - Invoice management

  ### 8. deep_reports
  - Premium report purchases
  - Detailed forecast analysis
  - Report data storage
  - Payment linkage

  ### 9. api_keys
  - API access credentials
  - Rate limiting tracking
  - Key permissions management
  - Usage monitoring

  ## Security
  - Row Level Security (RLS) enabled on all tables
  - Users can only access their own data
  - Admin access controlled via role checks
  - API keys secured with proper policies
*/

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- USERS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  full_name TEXT NOT NULL,
  is_active BOOLEAN DEFAULT true NOT NULL,
  is_verified BOOLEAN DEFAULT false NOT NULL,
  subscription_tier TEXT DEFAULT 'basic' NOT NULL CHECK (subscription_tier IN ('basic', 'pro', 'master')),
  subscription_status TEXT DEFAULT 'inactive' NOT NULL CHECK (subscription_status IN ('active', 'inactive', 'cancelled', 'past_due')),
  stripe_customer_id TEXT,
  forecast_credits_remaining INTEGER DEFAULT 50 NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own profile"
  ON users FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- =============================================================================
-- PRODUCTS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS products (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL,
  base_price DECIMAL(10, 2) NOT NULL,
  production_method TEXT CHECK (production_method IN ('self', 'fason', 'dropship', 'wholesale')),
  target_market TEXT,
  is_active BOOLEAN DEFAULT true NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_products_user_id ON products(user_id);
CREATE INDEX idx_products_category ON products(category);

ALTER TABLE products ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own products"
  ON products FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own products"
  ON products FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own products"
  ON products FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own products"
  ON products FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

-- =============================================================================
-- CITIES TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS cities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  country TEXT NOT NULL,
  region TEXT,
  population INTEGER NOT NULL,
  gdp_per_capita DECIMAL(12, 2),
  ecommerce_penetration DECIMAL(5, 2),
  age_distribution JSONB DEFAULT '{}' NOT NULL,
  purchasing_power_index DECIMAL(6, 2),
  internet_penetration DECIMAL(5, 2),
  mobile_penetration DECIMAL(5, 2),
  latitude DECIMAL(10, 7),
  longitude DECIMAL(10, 7),
  updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_cities_country ON cities(country);
CREATE INDEX idx_cities_population ON cities(population);
CREATE INDEX idx_cities_name ON cities(name);

-- Cities are public data
ALTER TABLE cities ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read cities"
  ON cities FOR SELECT
  TO authenticated
  USING (true);

-- =============================================================================
-- FORECASTS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS forecasts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  target_city_id UUID NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
  demand_score INTEGER CHECK (demand_score >= 0 AND demand_score <= 100),
  competition_index INTEGER CHECK (competition_index >= 0 AND competition_index <= 100),
  profitability_score INTEGER CHECK (profitability_score >= 0 AND profitability_score <= 100),
  expected_sales_volume INTEGER,
  recommended_price DECIMAL(10, 2),
  confidence_level DECIMAL(5, 2),
  status TEXT DEFAULT 'pending' NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  error_message TEXT,
  processing_started_at TIMESTAMPTZ,
  processing_completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_forecasts_user_id ON forecasts(user_id);
CREATE INDEX idx_forecasts_product_id ON forecasts(product_id);
CREATE INDEX idx_forecasts_status ON forecasts(status);
CREATE INDEX idx_forecasts_created_at ON forecasts(created_at DESC);

ALTER TABLE forecasts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own forecasts"
  ON forecasts FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own forecasts"
  ON forecasts FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own forecasts"
  ON forecasts FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- =============================================================================
-- AGENT_LOGS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS agent_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  forecast_id UUID NOT NULL REFERENCES forecasts(id) ON DELETE CASCADE,
  agent_name TEXT NOT NULL,
  input_data JSONB DEFAULT '{}' NOT NULL,
  output_data JSONB DEFAULT '{}' NOT NULL,
  execution_time_ms INTEGER NOT NULL,
  tokens_used INTEGER DEFAULT 0 NOT NULL,
  cost_usd DECIMAL(10, 4) DEFAULT 0 NOT NULL,
  status TEXT DEFAULT 'success' NOT NULL CHECK (status IN ('success', 'failed', 'timeout')),
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_agent_logs_forecast_id ON agent_logs(forecast_id);
CREATE INDEX idx_agent_logs_agent_name ON agent_logs(agent_name);
CREATE INDEX idx_agent_logs_created_at ON agent_logs(created_at DESC);

ALTER TABLE agent_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read logs for own forecasts"
  ON agent_logs FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM forecasts
      WHERE forecasts.id = agent_logs.forecast_id
      AND forecasts.user_id = auth.uid()
    )
  );

-- =============================================================================
-- SUBSCRIPTIONS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  stripe_subscription_id TEXT UNIQUE,
  plan_type TEXT NOT NULL CHECK (plan_type IN ('basic', 'pro', 'master')),
  status TEXT DEFAULT 'active' NOT NULL CHECK (status IN ('active', 'cancelled', 'past_due', 'trialing', 'incomplete')),
  current_period_start TIMESTAMPTZ NOT NULL,
  current_period_end TIMESTAMPTZ NOT NULL,
  cancel_at_period_end BOOLEAN DEFAULT false NOT NULL,
  cancelled_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);

ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own subscription"
  ON subscriptions FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

-- =============================================================================
-- PAYMENTS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS payments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  stripe_payment_intent_id TEXT UNIQUE,
  amount_cents INTEGER NOT NULL,
  currency TEXT DEFAULT 'usd' NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('succeeded', 'pending', 'failed', 'refunded')),
  payment_type TEXT NOT NULL CHECK (payment_type IN ('subscription', 'deep_report', 'addon', 'custom')),
  description TEXT,
  metadata JSONB DEFAULT '{}' NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_created_at ON payments(created_at DESC);

ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own payments"
  ON payments FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

-- =============================================================================
-- DEEP_REPORTS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS deep_reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  forecast_id UUID NOT NULL REFERENCES forecasts(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  payment_id UUID REFERENCES payments(id) ON DELETE SET NULL,
  report_type TEXT NOT NULL CHECK (report_type IN ('standard', 'premium', 'enterprise')),
  price_paid_cents INTEGER NOT NULL,
  report_data JSONB DEFAULT '{}' NOT NULL,
  status TEXT DEFAULT 'generating' NOT NULL CHECK (status IN ('generating', 'completed', 'failed')),
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_deep_reports_forecast_id ON deep_reports(forecast_id);
CREATE INDEX idx_deep_reports_user_id ON deep_reports(user_id);

ALTER TABLE deep_reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own deep reports"
  ON deep_reports FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

-- =============================================================================
-- API_KEYS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS api_keys (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  key_hash TEXT UNIQUE NOT NULL,
  key_prefix TEXT NOT NULL,
  name TEXT NOT NULL,
  permissions JSONB DEFAULT '[]' NOT NULL,
  is_active BOOLEAN DEFAULT true NOT NULL,
  last_used_at TIMESTAMPTZ,
  rate_limit_per_minute INTEGER DEFAULT 60 NOT NULL,
  requests_made_today INTEGER DEFAULT 0 NOT NULL,
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);

ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own API keys"
  ON api_keys FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own API keys"
  ON api_keys FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own API keys"
  ON api_keys FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own API keys"
  ON api_keys FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
  BEFORE UPDATE ON products
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cities_updated_at
  BEFORE UPDATE ON cities
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at
  BEFORE UPDATE ON subscriptions
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();