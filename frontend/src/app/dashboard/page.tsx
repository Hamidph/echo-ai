"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { Navbar } from "@/components/Navbar";
import { dashboardApi, experimentsApi } from "@/lib/api";
import { InfoTooltip } from "@/components/ui/Tooltip";
import Card from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/Badge";
import { RecommendedPrompts } from "@/components/dashboard/RecommendedPrompts";
import { useState, useEffect } from "react";
import dynamic from "next/dynamic";

const VisibilityTrendChart = dynamic(() => import("@/components/dashboard/VisibilityTrendChart").then(mod => mod.VisibilityTrendChart), { ssr: false });
const ShareOfVoiceChart = dynamic(() => import("@/components/dashboard/ShareOfVoiceChart").then(mod => mod.ShareOfVoiceChart), { ssr: false });

export default function DashboardPage() {
  const { user, isLoading: authLoading } = useAuth();
  const [greeting, setGreeting] = useState("Welcome");

  // Fetch Dashboard Stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["dashboardStats"],
    queryFn: () => dashboardApi.getStats(),
    enabled: !!user,
  });

  // Fetch All Experiments (not just recent)
  const { data: experiments, isLoading: experimentsLoading } = useQuery({
    queryKey: ["allExperiments"],
    queryFn: async () => {
      const result = await experimentsApi.list(50, 0);
      return result;
    },
    enabled: !!user,
  });

  // Fix hydration mismatch for time-based greeting
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good morning");
    else if (hour < 18) setGreeting("Good afternoon");
    else setGreeting("Good evening");
  }, []);

  if (authLoading || statsLoading || !mounted) {
    return (
      <div className="min-h-screen bg-[#FDFCF8] flex items-center justify-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-blue-500/20 rounded-full" />
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
        </div>
      </div>
    );
  }

  const hasExperiments = (stats?.total_experiments || 0) > 0;

  return (
    <div className="min-h-screen bg-[#FDFCF8]">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-28">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-slate-900 mb-1">
              {greeting}, {(user as any)?.full_name?.split(" ")[0] || "there"}!
            </h1>
            <p className="text-slate-500">
              {hasExperiments
                ? `You've run ${stats?.total_experiments} experiments. Here's your visibility impact.`
                : "Get started by running your first experiment"}
            </p>
          </div>
          <Link
            href="/experiments/new"
            className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-all shadow-md hover:shadow-lg"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Experiment
          </Link>
        </div>

        {hasExperiments ? (
          <div className="space-y-8 animate-fade-in">
            {/* Top Stats Cards */}
            <div className="grid md:grid-cols-3 gap-6">
              <Card className="border-blue-200">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-blue-100 border border-blue-200 flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </div>
                  <InfoTooltip content="Average unweighted brand visibility across your experiments" />
                </div>
                <p className="text-sm text-slate-500 mb-1">Avg Visibility Score</p>
                <div className="flex items-center gap-2 mt-1">
                  <p className="text-3xl font-bold text-slate-900">{stats?.avg_visibility_score}%</p>
                  <span className="flex items-center text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                    <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    +2.5%
                  </span>
                </div>
              </Card>

              <Card className="border-violet-200">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-violet-100 border border-violet-200 flex items-center justify-center">
                    <svg className="w-6 h-6 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <InfoTooltip content="Completed experiments" />
                </div>
                <p className="text-sm text-slate-500 mb-1">Completed Runs</p>
                <div className="flex items-center gap-2 mt-1">
                  <p className="text-3xl font-bold text-slate-900">{stats?.completed_experiments}</p>
                  <span className="flex items-center text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                    <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    +12%
                  </span>
                </div>
              </Card>

              <Card className="border-amber-200">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-amber-100 border border-amber-200 flex items-center justify-center">
                    <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <InfoTooltip content="Experiments currently executing" />
                </div>
                <p className="text-sm text-slate-500 mb-1">Total Experiments</p>
                <div className="flex items-center gap-2 mt-1">
                  <p className="text-3xl font-bold text-slate-900">{stats?.total_experiments}</p>
                  <span className="flex items-center text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                    <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
                    </svg>
                    0%
                  </span>
                </div>
              </Card>
            </div>

            {/* Charts Section */}
            <div className="grid lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <VisibilityTrendChart data={stats?.visibility_trend || []} />
              </div>
              <div>
                <ShareOfVoiceChart data={stats?.share_of_voice || []} />
              </div>
            </div>

            {/* All Experiments Section */}
            <div className="grid lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <Card className="h-full">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-bold text-slate-900">Your Experiments</h2>
                    <span className="text-sm text-slate-500">{experiments?.total || 0} total</span>
                  </div>

                  <div className="space-y-3">
                    {experiments?.experiments?.map((exp: any) => (
                      <Link
                        key={exp.experiment_id}
                        href={`/experiments/detail?id=${exp.experiment_id}`}
                        className="block p-4 bg-slate-50 rounded-xl border border-stone-200 hover:border-blue-300 hover:bg-blue-50 transition-all group"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <p className="text-slate-900 font-medium truncate group-hover:text-blue-600 transition">
                              {exp.prompt || "Untitled Experiment"}
                            </p>
                            <div className="flex items-center gap-3 mt-2 text-sm text-slate-400">
                              <span>Target: {exp.target_brand}</span>
                              <span>•</span>
                              <span className="capitalize">{exp.provider || "openai"}</span>
                              <span>•</span>
                              <span>{new Date(exp.created_at).toLocaleDateString()}</span>
                            </div>
                          </div>
                          <StatusBadge status={exp.status} />
                        </div>
                      </Link>
                    ))}
                  </div>
                </Card>
              </div>
              <div>
                <RecommendedPrompts />
              </div>
            </div>
          </div>
        ) : (
          /* Empty State - No Experiments */
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-blue-100 to-violet-100 border border-blue-200 flex items-center justify-center mb-6">
              <svg className="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Welcome to Echo AI</h2>
            <p className="text-slate-500 text-center max-w-md mb-8">
              Start analyzing your brand&apos;s visibility across AI platforms. Run your first experiment to see how AI search engines respond to prompts about your brand.
            </p>
            <Link
              href="/experiments/new"
              className="inline-flex items-center gap-2 px-8 py-4 text-lg font-semibold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-all shadow-lg hover:shadow-xl"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Create Your First Experiment
            </Link>

            {/* Quick Guide */}
            <div className="grid md:grid-cols-3 gap-6 mt-12 max-w-4xl">
              <Card className="text-center">
                <div className="w-12 h-12 rounded-xl bg-blue-100 border border-blue-200 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">1️⃣</span>
                </div>
                <h3 className="text-slate-900 font-semibold mb-2">Enter Your Prompt</h3>
                <p className="text-sm text-slate-500">
                  Write a question users might ask AI assistants about your industry
                </p>
              </Card>

              <Card className="text-center">
                <div className="w-12 h-12 rounded-xl bg-violet-100 border border-violet-200 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">2️⃣</span>
                </div>
                <h3 className="text-slate-900 font-semibold mb-2">Choose AI Provider</h3>
                <p className="text-sm text-slate-500">
                  Select ChatGPT, Perplexity, or Claude to test against
                </p>
              </Card>

              <Card className="text-center">
                <div className="w-12 h-12 rounded-xl bg-emerald-100 border border-emerald-200 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">3️⃣</span>
                </div>
                <h3 className="text-slate-900 font-semibold mb-2">Get Insights</h3>
                <p className="text-sm text-slate-500">
                  See visibility, position, and competitor analysis
                </p>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
