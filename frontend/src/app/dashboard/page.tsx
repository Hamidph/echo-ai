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

  // Fetch Recent Experiments
  const { data: experiments, isLoading: experimentsLoading } = useQuery({
    queryKey: ["recentExperiments"],
    queryFn: () => experimentsApi.list(5, 0),
    enabled: !!user,
  });

  // Fix hydration mismatch for time-based greeting
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good morning");
    else if (hour < 18) setGreeting("Good afternoon");
    else setGreeting("Good evening");
  }, []);

  if (authLoading || statsLoading) {
    return (
      <div className="min-h-screen bg-[#030712] flex items-center justify-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-cyan-500/20 rounded-full" />
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
        </div>
      </div>
    );
  }

  const hasExperiments = (stats?.total_experiments || 0) > 0;

  return (
    <div className="min-h-screen bg-[#030712]">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-24">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-white mb-1">
              {greeting}, {(user as any)?.full_name?.split(" ")[0] || "there"}!
            </h1>
            <p className="text-gray-400">
              {hasExperiments
                ? `You've run ${stats?.total_experiments} experiments. Here's your visibility impact.`
                : "Get started by running your first experiment"}
            </p>
          </div>
          <Link
            href="/experiments/new"
            className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-cyan-500 to-violet-500 rounded-lg hover:scale-105 transition-all shadow-lg hover:shadow-cyan-500/50"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Analysis
          </Link>
        </div>

        {hasExperiments ? (
          <div className="space-y-8 animate-fade-in">
            {/* Top Stats Cards */}
            <div className="grid md:grid-cols-3 gap-6">
              <Card className="border-cyan-500/20">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                    <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </div>
                  <InfoTooltip content="Average unweighted brand visibility across your experiments" />
                </div>
                <p className="text-sm text-gray-400 mb-1">Avg Visibility Score</p>
                <div className="flex items-baseline gap-2">
                  <p className="text-3xl font-bold text-white">{stats?.avg_visibility_score}%</p>
                  <span className="text-xs text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">High</span>
                </div>
              </Card>

              <Card className="border-violet-500/20">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
                    <svg className="w-6 h-6 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <InfoTooltip content="Completed experiments" />
                </div>
                <p className="text-sm text-gray-400 mb-1">Completed Runs</p>
                <p className="text-3xl font-bold text-white">{stats?.completed_experiments}</p>
              </Card>

              <Card className="border-amber-500/20">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
                    <svg className="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <InfoTooltip content="Experiments currently executing" />
                </div>
                <p className="text-sm text-gray-400 mb-1">Total Experiments</p>
                <p className="text-3xl font-bold text-white">{stats?.total_experiments}</p>
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

            {/* Bottom Section: Recent & Recommendations */}
            <div className="grid lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <Card className="h-full">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-bold text-white">Recent Experiments</h2>
                    <Link
                      href="/experiments"
                      className="text-sm text-cyan-400 hover:text-cyan-300 transition"
                    >
                      View all →
                    </Link>
                  </div>

                  <div className="space-y-3">
                    {experiments?.experiments?.map((exp: any) => (
                      <Link
                        key={exp.experiment_id}
                        href={`/experiments/detail?id=${exp.experiment_id}`}
                        className="block p-4 bg-white/5 rounded-xl border border-white/5 hover:border-cyan-500/50 hover:bg-cyan-500/5 transition-all group"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <p className="text-gray-200 font-medium truncate group-hover:text-cyan-400 transition">
                              {exp.prompt || "Untitled Experiment"}
                            </p>
                            <div className="flex items-center gap-3 mt-2 text-sm text-gray-500">
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
            <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-violet-500/20 border border-cyan-500/20 flex items-center justify-center mb-6">
              <svg className="w-12 h-12 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Welcome to Echo AI</h2>
            <p className="text-gray-400 text-center max-w-md mb-8">
              Start analyzing your brand's visibility across AI platforms. Run your first experiment to see how AI search engines respond to prompts about your brand.
            </p>
            <Link
              href="/experiments/new"
              className="inline-flex items-center gap-2 px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-cyan-500 to-violet-500 rounded-xl hover:scale-105 transition-all shadow-lg hover:shadow-cyan-500/50"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Create Your First Experiment
            </Link>

            {/* Quick Guide */}
            <div className="grid md:grid-cols-3 gap-6 mt-12 max-w-4xl">
              <Card className="text-center">
                <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">1️⃣</span>
                </div>
                <h3 className="text-white font-semibold mb-2">Enter Your Prompt</h3>
                <p className="text-sm text-gray-400">
                  Write a question users might ask AI assistants about your industry
                </p>
              </Card>

              <Card className="text-center">
                <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">2️⃣</span>
                </div>
                <h3 className="text-white font-semibold mb-2">Choose AI Provider</h3>
                <p className="text-sm text-gray-400">
                  Select ChatGPT, Perplexity, or Claude to test against
                </p>
              </Card>

              <Card className="text-center">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">3️⃣</span>
                </div>
                <h3 className="text-white font-semibold mb-2">Get Insights</h3>
                <p className="text-sm text-gray-400">
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
