"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { useState, useRef, useEffect } from "react";
import { usePathname } from "next/navigation";

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const navLinks = [
    { name: "Features", href: "#features" },
    { name: "Pricing", href: "#pricing" },
    { name: "Methodology", href: "#demo" },
  ];

  return (
    <nav className="fixed w-full z-50 top-0 start-0 border-b border-stone-200/60 bg-[#FDFCF8]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3">
            <div className="w-11 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-[10px] tracking-wide shadow-md">
              ECHO
            </div>
            <span className="self-center text-xl font-heading font-bold whitespace-nowrap text-slate-900">
              Echo AI
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            {!isAuthenticated && navLinks.map(link => (
              <Link
                key={link.name}
                href={link.href}
                className="text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors"
              >
                {link.name}
              </Link>
            ))}
          </div>

          {/* Right Side / Auth */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-stone-200 bg-white hover:bg-stone-50 transition-all shadow-sm"
                >
                  <div className="w-6 h-6 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 flex items-center justify-center text-xs font-bold text-blue-700">
                    {(user as any)?.full_name?.charAt(0) || "U"}
                  </div>
                  <span className="text-sm font-medium text-slate-700 max-w-[100px] truncate">
                    {(user as any)?.full_name || "User"}
                  </span>
                  <svg className="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
                </button>

                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white border border-stone-100 rounded-xl shadow-xl py-2 animate-fade-in ring-1 ring-black/5">
                    <Link href="/dashboard" className="block px-4 py-2 text-sm text-slate-700 hover:bg-stone-50">
                      <div className="flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                        </svg>
                        Dashboard
                      </div>
                    </Link>
                    <Link href="/experiments" className="block px-4 py-2 text-sm text-slate-700 hover:bg-stone-50">
                      <div className="flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        All Analyses
                      </div>
                    </Link>
                    {(user as any)?.role === 'admin' && (
                      <Link href="/admin" className="block px-4 py-2 text-sm text-slate-700 hover:bg-stone-50">
                        <div className="flex items-center gap-2">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                          Admin Panel
                        </div>
                      </Link>
                    )}
                    <Link href="/settings" className="block px-4 py-2 text-sm text-slate-700 hover:bg-stone-50">
                      <div className="flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        Settings
                      </div>
                    </Link>
                    <div className="border-t border-stone-100 my-1"></div>
                    <button onClick={logout} className="block w-full text-left px-4 py-2 text-sm text-rose-600 hover:bg-stone-50">
                      <div className="flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        Sign out
                      </div>
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <>
                <Link href="/login" className="text-sm font-medium text-slate-600 hover:text-slate-900 px-4">Sign in</Link>
                <Link href="/register" className="text-sm font-bold text-white bg-slate-900 px-4 py-2 rounded-lg hover:bg-slate-800 transition-all shadow-md">
                  Get Started
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-slate-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
            aria-expanded={mobileMenuOpen}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-b border-stone-200 py-4 px-4 space-y-2">
          {!isAuthenticated && navLinks.map(link => (
            <Link
              key={link.name}
              href={link.href}
              className="block py-2 text-base font-medium text-slate-600"
              onClick={() => setMobileMenuOpen(false)}
            >
              {link.name}
            </Link>
          ))}
          <div className="border-t border-stone-100 my-2 pt-2">
            {isAuthenticated ? (
              <>
                <Link href="/dashboard" className="block py-2 font-medium text-slate-900">Dashboard</Link>
                <Link href="/experiments" className="block py-2 font-medium text-slate-900">All Analyses</Link>
                {(user as any)?.role === 'admin' && (
                  <Link href="/admin" className="block py-2 font-medium text-slate-900">Admin Panel</Link>
                )}
                <Link href="/settings" className="block py-2 font-medium text-slate-900">Settings</Link>
                <button onClick={logout} className="block py-2 w-full text-left text-slate-500">Sign out</button>
              </>
            ) : (
              <>
                <Link href="/login" className="block py-2 font-medium text-slate-900">Sign in</Link>
                <Link href="/register" className="block py-2 font-bold text-blue-600">Get Started</Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
