'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, isLoading, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#030712] flex items-center justify-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-cyan-500/20 rounded-full" />
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  // No sidebar - just render children (Navbar is in each page)
  return <>{children}</>;
}
