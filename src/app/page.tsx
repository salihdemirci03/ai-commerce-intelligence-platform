'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, Globe2, TrendingUp, Zap, Target, ShoppingBag } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-slate-900">Commerce Intelligence</span>
          </div>
          <nav className="flex items-center space-x-4">
            <Link href="/login">
              <Button variant="ghost">Login</Button>
            </Link>
            <Link href="/register">
              <Button>Get Started</Button>
            </Link>
          </nav>
        </div>
      </header>

      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-3xl mx-auto space-y-6">
          <h1 className="text-5xl font-bold text-slate-900 leading-tight">
            AI-Powered Market Intelligence for Your E-Commerce Success
          </h1>
          <p className="text-xl text-slate-600 leading-relaxed">
            Predict sales potential, analyze markets, and optimize your strategy with our advanced AI-driven platform.
            Make data-driven decisions for every city and product.
          </p>
          <div className="flex justify-center gap-4 pt-4">
            <Link href="/register">
              <Button size="lg" className="text-lg px-8">
                Start Free Trial
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="text-lg px-8">
              Watch Demo
            </Button>
          </div>
        </div>
      </section>

      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <Target className="h-12 w-12 text-blue-600 mb-4" />
              <CardTitle>City-Based Forecasting</CardTitle>
              <CardDescription>
                Predict which cities offer the highest sales potential for your products with AI-powered analysis
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <Globe2 className="h-12 w-12 text-green-600 mb-4" />
              <CardTitle>Market Intelligence</CardTitle>
              <CardDescription>
                Real-time trend detection, competitor analysis, and demographic insights across global markets
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <Zap className="h-12 w-12 text-orange-600 mb-4" />
              <CardTitle>5 AI Agents</CardTitle>
              <CardDescription>
                Specialized agents for product analysis, market profiling, advertising, supply chain, and sales strategy
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      <section className="bg-slate-50 py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">
              How It Works
            </h2>
            <p className="text-slate-600">
              Our platform combines cutting-edge AI with market data to deliver actionable insights
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: '1', title: 'Add Your Product', desc: 'Enter product details and specifications' },
              { step: '2', title: 'AI Analysis', desc: 'Our 5 specialized agents analyze your product' },
              { step: '3', title: 'Get Insights', desc: 'Receive comprehensive market forecasts' },
              { step: '4', title: 'Take Action', desc: 'Implement data-driven strategies' },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                  {item.step}
                </div>
                <h3 className="font-semibold text-lg mb-2">{item.title}</h3>
                <p className="text-slate-600 text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Subscription Plans</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: 'Basic',
                price: 29,
                features: ['50 forecasts/month', 'Top 10 cities', 'Summary reports', 'Email support'],
              },
              {
                name: 'Pro',
                price: 79,
                popular: true,
                features: ['250 forecasts/month', 'Top 50 cities', 'Detailed reports', 'API access', 'Priority support'],
              },
              {
                name: 'Master',
                price: 149,
                features: ['Unlimited forecasts', 'All cities', 'Full analysis', 'Custom reports', 'Dedicated support'],
              },
            ].map((plan) => (
              <Card key={plan.name} className={plan.popular ? 'border-blue-600 border-2' : ''}>
                <CardHeader>
                  {plan.popular && (
                    <div className="text-blue-600 text-sm font-semibold mb-2">MOST POPULAR</div>
                  )}
                  <CardTitle>{plan.name}</CardTitle>
                  <div className="text-3xl font-bold mt-4">
                    ${plan.price}<span className="text-lg text-slate-600">/mo</span>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start">
                        <span className="text-green-600 mr-2">✓</span>
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Link href="/register">
                    <Button className="w-full mt-6" variant={plan.popular ? 'default' : 'outline'}>
                      Get Started
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t bg-slate-50 py-12">
        <div className="container mx-auto px-4 text-center text-slate-600">
          <p>&copy; 2025 Commerce Intelligence Platform. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
