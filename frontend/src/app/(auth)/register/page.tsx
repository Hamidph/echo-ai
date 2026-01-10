'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Button from '@/components/ui/Button';

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Use relative path if proxy is set up or rely on global configured API URL
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://echo-ai-production.up.railway.app';

      const response = await fetch(`${apiUrl}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Registration failed');
      }

      // Auto-login after registration
      const loginResponse = await fetch(`${apiUrl}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: formData.email, password: formData.password }),
      });

      const loginData = await loginResponse.json();
      localStorage.setItem('token', loginData.access_token);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FDFCF8] flex items-center justify-center px-6 relative overflow-hidden">
      {/* Background gradients aligned with Login page */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-blue-100/40 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-100/40 rounded-full blur-[120px]"></div>
      </div>

      <div className="max-w-md w-full relative z-10">
        {/* Logo */}
        <Link href="/" className="flex items-center justify-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs tracking-tight shadow-md">
            ECHO
          </div>
          <span className="font-heading font-bold text-2xl text-slate-900">Echo AI</span>
        </Link>

        {/* Register Card */}
        <div className="bg-white rounded-2xl border border-stone-200 shadow-xl p-8">
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Create an account</h1>
          <p className="text-slate-500 mb-8">Start tracking your brand&apos;s AI visibility today</p>

          {error && (
            <div className="bg-rose-50 border border-rose-100 text-rose-600 px-4 py-3 rounded-lg mb-6 flex items-start gap-2 text-sm">
              <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Full Name</label>
              <input
                type="text"
                className="w-full px-4 py-2.5 rounded-lg border border-stone-200 bg-stone-50 text-slate-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
                placeholder="John Doe"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Email</label>
              <input
                type="email"
                className="w-full px-4 py-2.5 rounded-lg border border-stone-200 bg-stone-50 text-slate-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
                placeholder="you@example.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Password</label>
              <input
                type="password"
                className="w-full px-4 py-2.5 rounded-lg border border-stone-200 bg-stone-50 text-slate-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
                minLength={8}
              />
              <p className="mt-1 text-xs text-slate-400">Must be at least 8 characters</p>
            </div>

            <div className="flex items-start">
              <input
                type="checkbox"
                id="terms"
                className="w-4 h-4 mt-0.5 rounded border-stone-300 text-blue-600 focus:ring-blue-500 bg-stone-50"
                required
              />
              <label htmlFor="terms" className="ml-2 text-sm text-slate-500">
                I agree to the{' '}
                <Link href="/terms" className="text-blue-600 hover:text-blue-700 transition font-medium">
                  Terms
                </Link>{' '}
                and{' '}
                <Link href="/privacy" className="text-blue-600 hover:text-blue-700 transition font-medium">
                  Privacy Policy
                </Link>
              </label>
            </div>

            <Button
              type="submit"
              className="w-full py-3 px-4 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl transition-all shadow-md hover:shadow-lg"
              isLoading={loading}
            >
              Create Account
            </Button>
          </form>

          <div className="mt-6 relative">
            <div className="absolute inset-x-0 top-1/2 h-px bg-stone-200"></div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-slate-500">Already have an account?</span>
            </div>
            <p className="text-center text-slate-500 text-sm mt-4">
              <Link href="/login" className="text-blue-600 hover:text-blue-700 font-bold transition">
                Sign in
              </Link>
            </p>
          </div>
        </div>

        {/* Benefits text below card */}
        <div className="mt-8 grid grid-cols-1 gap-2 text-center">
          <p className="text-sm text-slate-400 font-medium tracking-wide">
            <span className="text-emerald-500 text-lg mr-1.5">✓</span> No credit card required
          </p>
          <p className="text-sm text-slate-400 font-medium tracking-wide">
            <span className="text-emerald-500 text-lg mr-1.5">✓</span> 14-day free trial
          </p>
        </div>
      </div>
    </div>
  );
}
