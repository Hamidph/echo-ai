'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  email: string;
  pricing_tier: string;
  monthly_iteration_quota: number;
  stripe_customer_id: string | null;
}

interface Usage {
  current_period_iterations: number;
  quota_remaining: number;
  quota_percentage_used: number;
}

const PRICING_TIERS = [
  {
    name: 'FREE',
    price: 0,
    iterations: 3,
    features: [
      '3 prompts/month',
      '10 iterations per prompt',
      'All AI providers',
      'Basic analytics',
      'Community support',
    ],
    description: 'Perfect for testing',
  },
  {
    name: 'STARTER',
    price: 35,
    iterations: 10,
    features: [
      '10 prompts/month',
      '10 iterations per prompt',
      'All AI providers',
      'Advanced analytics',
      'Competitor tracking',
      'Email support',
    ],
    description: 'For small teams',
  },
  {
    name: 'PRO',
    price: 55,
    iterations: 15,
    features: [
      '15 prompts/month',
      '10 iterations per prompt',
      'All AI providers',
      'Priority API access',
      'Advanced analytics',
      'Custom integrations',
      'Advanced reporting & exports',
    ],
    description: 'For growing businesses',
    popular: true,
  },
  {
    name: 'ENTERPRISE',
    price: 169,
    iterations: 50,
    features: [
      '50 prompts/month',
      '10 iterations per prompt',
      'All AI providers',
      'Unlimited users',
      'White-label options',
      '24/7 priority support',
      'Custom SLA',
    ],
    description: 'Custom solutions',
  },
];

export default function BillingPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [usage, setUsage] = useState<Usage | null>(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        router.push('/login');
        return;
      }

      try {
        // Fetch user
        const userRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/me`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        const userData = await userRes.json();
        setUser(userData);

        // Fetch usage
        const usageRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/billing/usage`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        const usageData = await usageRes.json();
        setUsage(usageData);
      } catch (error) {
        console.error('Failed to fetch billing data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router]);

  const handleUpgrade = async (tier: string) => {
    if (tier === 'ENTERPRISE') {
      window.location.href = 'mailto:sales@aivisibility.com?subject=Enterprise Plan Inquiry';
      return;
    }

    setUpgrading(tier);
    const token = localStorage.getItem('access_token');

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/billing/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          pricing_tier: tier,
          success_url: `${window.location.origin}/dashboard/billing?success=true`,
          cancel_url: `${window.location.origin}/dashboard/billing?canceled=true`,
        }),
      });

      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      setUpgrading(null);
    }
  };

  const handleManageSubscription = async () => {
    const token = localStorage.getItem('access_token');

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/billing/portal`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          return_url: window.location.href,
        }),
      });

      const data = await res.json();
      if (data.portal_url) {
        window.location.href = data.portal_url;
      }
    } catch (error) {
      console.error('Failed to open billing portal:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Billing & Subscription</h1>
        <p className="text-gray-600 mt-1">Manage your subscription and usage</p>
      </div>

      {/* Current Plan */}
      <div className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl p-8 text-white">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">Current Plan: {user?.pricing_tier}</h2>
            <p className="text-purple-100 mb-4">
              {usage && `${usage.current_period_iterations} of ${user?.monthly_iteration_quota} iterations used this month`}
            </p>
            {usage && (
              <div className="bg-white/20 rounded-lg h-3 w-64 overflow-hidden">
                <div
                  className="bg-white h-full transition-all"
                  style={{ width: `${Math.min(usage.quota_percentage_used, 100)}%` }}
                />
              </div>
            )}
          </div>
          {user?.stripe_customer_id && (
            <button
              onClick={handleManageSubscription}
              className="px-6 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-purple-50 transition"
            >
              Manage Subscription
            </button>
          )}
        </div>
      </div>

      {/* Pricing Tiers */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Choose Your Plan</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {PRICING_TIERS.map((tier) => (
            <div
              key={tier.name}
              className={`bg-white rounded-xl border-2 p-6 transition ${
                tier.popular
                  ? 'border-purple-500 shadow-lg scale-105'
                  : 'border-gray-200 hover:border-purple-300'
              } ${user?.pricing_tier === tier.name ? 'ring-2 ring-purple-500' : ''}`}
            >
              {tier.popular && (
                <span className="inline-block px-3 py-1 bg-purple-500 text-white text-xs font-semibold rounded-full mb-3">
                  POPULAR
                </span>
              )}
              {user?.pricing_tier === tier.name && (
                <span className="inline-block px-3 py-1 bg-green-500 text-white text-xs font-semibold rounded-full mb-3">
                  CURRENT PLAN
                </span>
              )}

              <h3 className="text-xl font-bold text-gray-900 mb-1">{tier.name}</h3>
              <p className="text-sm text-gray-600 mb-4">{tier.description}</p>

              <div className="mb-6">
                {tier.price === null ? (
                  <span className="text-3xl font-bold text-gray-900">Custom</span>
                ) : tier.price === 0 ? (
                  <span className="text-3xl font-bold text-gray-900">Free</span>
                ) : (
                  <>
                    <span className="text-3xl font-bold text-gray-900">${tier.price}</span>
                    <span className="text-gray-600">/month</span>
                  </>
                )}
              </div>

              <ul className="space-y-3 mb-6">
                {tier.features.map((feature, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                    <span className="text-green-500 mt-0.5">✓</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleUpgrade(tier.name)}
                disabled={user?.pricing_tier === tier.name || upgrading === tier.name}
                className={`w-full px-4 py-3 rounded-lg font-semibold transition ${
                  user?.pricing_tier === tier.name
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : tier.popular
                    ? 'bg-purple-600 text-white hover:bg-purple-700'
                    : 'bg-white border-2 border-purple-600 text-purple-600 hover:bg-purple-50'
                }`}
              >
                {upgrading === tier.name
                  ? 'Processing...'
                  : user?.pricing_tier === tier.name
                  ? 'Current Plan'
                  : tier.name === 'ENTERPRISE'
                  ? 'Contact Sales'
                  : tier.price === 0
                  ? 'Current Plan'
                  : 'Upgrade'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* FAQ */}
      <div className="bg-white rounded-xl border border-gray-200 p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h2>
        <div className="space-y-4">
          <FAQItem
            question="Can I change my plan anytime?"
            answer="Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately for upgrades, or at the end of your billing period for downgrades."
          />
          <FAQItem
            question="What happens if I exceed my quota?"
            answer="If you exceed your monthly iteration quota, new experiments will be queued until the next billing cycle or you can upgrade your plan."
          />
          <FAQItem
            question="Do you offer refunds?"
            answer="We offer a 30-day money-back guarantee for all paid plans. Contact support@aivisibility.com for refund requests."
          />
          <FAQItem
            question="How is usage calculated?"
            answer="Each query to an AI provider counts as one iteration. If you query 3 providers with 100 iterations, that's 300 total iterations."
          />
        </div>
      </div>
    </div>
  );
}

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="border-b border-gray-200 last:border-0 pb-4">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between text-left font-semibold text-gray-900 hover:text-purple-600 transition"
      >
        <span>{question}</span>
        <span className="text-xl">{open ? '−' : '+'}</span>
      </button>
      {open && <p className="mt-2 text-gray-600 text-sm">{answer}</p>}
    </div>
  );
}
