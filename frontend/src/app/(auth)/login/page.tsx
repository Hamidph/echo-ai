'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Card from '@/components/ui/Card';

export default function LoginPage() {
  const { login, loginLoading, loginError } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    login({ email, password });
  };

  return (
    <div className="min-h-screen bg-[#FDFCF8] flex items-center justify-center px-6 relative overflow-hidden">
      {/* Background gradients */}
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

        {/* Login Card */}
        <div className="bg-white rounded-2xl border border-stone-200 shadow-xl p-8">
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Welcome back</h1>
          <p className="text-slate-500 mb-8">Sign in to your account to continue</p>

          {loginError && (
            <div className="bg-rose-50 border border-rose-100 text-rose-600 px-4 py-3 rounded-lg mb-6 flex items-start gap-2 text-sm">
              <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{loginError.message}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Email</label>
              <input
                type="email"
                className="w-full px-4 py-2.5 rounded-lg border border-stone-200 bg-stone-50 text-slate-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Password</label>
              <input
                type="password"
                className="w-full px-4 py-2.5 rounded-lg border border-stone-200 bg-stone-50 text-slate-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="w-4 h-4 rounded border-stone-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-slate-500">Remember me</span>
              </label>
              <Link
                href="/forgot-password"
                className="text-sm text-blue-600 hover:text-blue-700 font-medium transition"
              >
                Forgot password?
              </Link>
            </div>

            <Button
              type="submit"
              className="w-full py-3 px-4 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl transition-all shadow-md hover:shadow-lg"
              isLoading={loginLoading}
            >
              Sign in
            </Button>
          </form>

          <div className="mt-6 relative">
            <div className="absolute inset-x-0 top-1/2 h-px bg-stone-200"></div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-slate-500">Don&apos;t have an account?</span>
            </div>
            <p className="text-center text-slate-500 text-sm mt-4">
              <Link href="/register" className="text-blue-600 hover:text-blue-700 font-bold transition">
                Create one now
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
