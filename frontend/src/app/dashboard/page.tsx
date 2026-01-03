"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { Navbar } from "@/components/Navbar";
import { experimentsApi } from "@/lib/api";
import { useState } from "react";
import { InfoTooltip } from "@/components/ui/Tooltip";
import Card from "@/components/ui/Card";
import Badge, { StatusBadge } from "@/components/ui/Badge";

export default function DashboardPage() {
  const { user, isLoading: authLoading } = useAuth();

  const { data: experiments, isLoading: experimentsLoading } = useQuery({
    queryKey: ["experiments"],
    queryFn: () => experimentsApi.list(100, 0),
    enabled: !!user,
  });

  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#030712] flex items-center justify-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-cyan-500/20 rounded-full" />
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
        </div>
      </div>
    );
  }

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };

  const completedExperiments = experiments?.experiments?.filter((e: any) => e.status === "completed") || [];
  const runningExperiments = experiments?.experiments?.filter((e: any) => e.status === "running") || [];
  const totalExperiments = experiments?.total || 0;

  // Calculate real metrics from experiments
  const calculateMetrics = () => {
    if (completedExperiments.length === 0) {
      return null;
    }

    // TODO: Calculate real visibility, sentiment, position from experiment results
    // For now, return null to show empty state
    return null;
  };

  const metrics = calculateMetrics();
  const hasExperiments = totalExperiments > 0;

  return (
    <div className="min-h-screen bg-[#030712]">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-white mb-1">
              {getGreeting()}, {user?.full_name?.split(" ")[0] || "there"}!
            </h1>
            <p className="text-gray-400">
              {hasExperiments
                ? `You have ${totalExperiments} experiment${totalExperiments === 1 ? '' : 's'}`
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
          <>
            {/* Usage Stats */}
            <div className="grid md:grid-cols-3 gap-6 mb-8">
              <Card className="border-cyan-500/20">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                    <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <InfoTooltip content="Total number of experiments you've run" />
                </div>
                <p className="text-sm text-gray-400 mb-1">Total Experiments</p>
                <p className="text-3xl font-bold text-cyan-400">{totalExperiments}</p>
              </Card>

              <Card className="border-violet-500/20">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
                    <svg className="w-6 h-6 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <InfoTooltip content="Experiments that have finished running" />
                </div>
                <p className="text-sm text-gray-400 mb-1">Completed</p>
                <p className="text-3xl font-bold text-violet-400">{completedExperiments.length}</p>
              </Card>

              <Card className="border-amber-500/20">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
                    <svg className="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <InfoTooltip content="Experiments currently being processed" />
                </div>
                <p className="text-sm text-gray-400 mb-1">Running</p>
                <p className="text-3xl font-bold text-amber-400">{runningExperiments.length}</p>
              </Card>
            </div>

            {/* Recent Experiments */}
            <Card>
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
                {experiments?.experiments?.slice(0, 5).map((exp: any) => (
                  <Link
                    key={exp.experiment_id}
                    href={`/experiments/${exp.experiment_id}`}
                    className="block p-4 bg-white/60 rounded-xl border border-stone-200 hover:border-blue-200 hover:bg-white shadow-sm hover:shadow-md transition-all group"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <p className="text-slate-900 font-medium truncate group-hover:text-blue-600 transition">
                          {exp.prompt || "Untitled Experiment"}
                        </p>
                        <div className="flex items-center gap-3 mt-2 text-sm text-slate-500">
                          <span>Target: {exp.target_brand}</span>
                          <span>•</span>
                          <span>{exp.provider || "openai"}</span>
                          <span>•</span>
                          <span>{new Date(exp.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <StatusBadge status={exp.status} />
                    </div>
                  </Link>
                ))}
              </div>

              {experiments?.experiments?.length === 0 && (
                <div className="text-center py-12">
                  <svg className="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-gray-400 mb-4">No experiments yet</p>
                  <Link
                    href="/experiments/new"
                    className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-cyan-500 to-violet-500 rounded-lg hover:scale-105 transition-all"
                  >
                    Create Your First Experiment
                  </Link>
                </div>
              )}
            </Card>

            {/* Quota Information */}
            <div className="mt-8">
              <Card className="border-emerald-500/20 bg-emerald-500/5">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-white font-semibold mb-1">Testing Mode Enabled</h3>
                    <p className="text-sm text-gray-300">
                      Unlimited prompts available for testing. Each experiment uses 1 prompt credit and runs 10 iterations (max 10 AI API calls) using gpt-4o.
                    </p>
                  </div>
                </div>
              </Card>
            </div>
          </>
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
