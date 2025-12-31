"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { Navbar } from "@/components/Navbar";
import { experimentsApi } from "@/lib/api";

export default function ExperimentDetailPage() {
  const { id } = useParams();
  const { user, isLoading: authLoading } = useAuth();

  const { data: experiment, isLoading, refetch } = useQuery({
    queryKey: ["experiment", id],
    queryFn: () => experimentsApi.get(id as string),
    enabled: !!user && !!id,
    refetchInterval: (query) => {
      // Auto-refresh while running
      const data = query.state.data;
      if (data?.status === "running" || data?.status === "pending") {
        return 3000;
      }
      return false;
    },
  });

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen mesh-bg flex items-center justify-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-cyan-500/20 rounded-full" />
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
        </div>
      </div>
    );
  }

  if (!experiment) {
    return (
      <div className="min-h-screen mesh-bg">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-20">
            <h2 className="text-xl font-semibold text-white mb-2">Analysis not found</h2>
            <p className="text-gray-500 mb-6">The analysis you&apos;re looking for doesn&apos;t exist.</p>
            <Link href="/experiments" className="btn-primary inline-flex items-center gap-2">
              <span>Back to Analyses</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const metrics = experiment.metrics || {};
  const isRunning = experiment.status === "running" || experiment.status === "pending";

  return (
    <div className="min-h-screen mesh-bg">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 animate-fade-in">
          <Link
            href="/experiments"
            className="inline-flex items-center gap-2 text-gray-500 hover:text-white transition-colors mb-4"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to analyses
          </Link>
          
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="font-display text-display-xs md:text-display-sm font-bold text-white truncate">
                  Analysis Results
                </h1>
                <span className={`badge ${
                  experiment.status === "completed" ? "badge-completed" :
                  experiment.status === "running" ? "badge-running" :
                  experiment.status === "failed" ? "badge-failed" :
                  "badge-pending"
                }`}>
                  {experiment.status}
                </span>
              </div>
              <p className="text-sm text-gray-500 font-mono">ID: {experiment.experiment_id}</p>
            </div>
            
            <button
              onClick={() => refetch()}
              className="btn-secondary inline-flex items-center gap-2 text-sm self-start"
            >
              <svg className={`w-4 h-4 ${isRunning ? "animate-spin" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>

        {/* Configuration */}
        <div className="glass-card rounded-2xl p-6 mb-6 animate-fade-in-up stagger-1">
          <h2 className="text-lg font-semibold text-white mb-4">Configuration</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-gray-500 mb-1">Prompt</p>
              <p className="text-white">{experiment.prompt}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Target Brand</p>
              <p className="text-white font-medium">{experiment.target_brand}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Created</p>
              <p className="text-white">
                {new Date(experiment.created_at).toLocaleString("en-US", {
                  dateStyle: "medium",
                  timeStyle: "short",
                })}
              </p>
            </div>
          </div>
        </div>

        {/* Results */}
        {isRunning ? (
          <div className="glass-card rounded-2xl p-12 text-center animate-fade-in-up stagger-2">
            <div className="relative w-20 h-20 mx-auto mb-6">
              <div className="absolute inset-0 rounded-full border-4 border-cyan-500/20" />
              <div className="absolute inset-0 rounded-full border-4 border-cyan-500 border-t-transparent animate-spin" />
              <div className="absolute inset-2 rounded-full border-4 border-violet-500/20" />
              <div className="absolute inset-2 rounded-full border-4 border-violet-500 border-t-transparent animate-spin" style={{ animationDirection: "reverse", animationDuration: "1.5s" }} />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Analysis in Progress</h3>
            <p className="text-gray-500 max-w-md mx-auto">
              Running Monte Carlo simulations across the AI provider. Results will appear automatically when complete.
            </p>
          </div>
        ) : experiment.status === "completed" ? (
          <>
            {/* Metrics Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6 animate-fade-in-up stagger-2">
              {/* Visibility Score */}
              <div className="glass-card stat-card rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                    <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </div>
                </div>
                <p className="text-sm text-gray-500 mb-1">Visibility Score</p>
                <p className="text-3xl font-bold text-white">
                  {metrics.visibility_score !== undefined ? `${(metrics.visibility_score * 100).toFixed(0)}%` : "—"}
                </p>
              </div>

              {/* Share of Voice */}
              <div className="glass-card stat-card rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
                    <svg className="w-5 h-5 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
                    </svg>
                  </div>
                </div>
                <p className="text-sm text-gray-500 mb-1">Share of Voice</p>
                <p className="text-3xl font-bold text-white">
                  {metrics.share_of_voice !== undefined ? `${(metrics.share_of_voice * 100).toFixed(0)}%` : "—"}
                </p>
              </div>

              {/* Consistency Score */}
              <div className="glass-card stat-card rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                    <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <p className="text-sm text-gray-500 mb-1">Consistency</p>
                <p className="text-3xl font-bold text-white">
                  {metrics.consistency_score !== undefined ? `${(metrics.consistency_score * 100).toFixed(0)}%` : "—"}
                </p>
              </div>

              {/* Hallucination Rate */}
              <div className="glass-card stat-card rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center">
                    <svg className="w-5 h-5 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                </div>
                <p className="text-sm text-gray-500 mb-1">Hallucination Rate</p>
                <p className="text-3xl font-bold text-white">
                  {metrics.hallucination_rate !== undefined ? `${(metrics.hallucination_rate * 100).toFixed(0)}%` : "—"}
                </p>
              </div>
            </div>

            {/* Detailed Analysis */}
            <div className="grid lg:grid-cols-2 gap-6 animate-fade-in-up stagger-3">
              {/* Summary */}
              <div className="glass-card rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Analysis Summary</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between py-3 border-b border-white/5">
                    <span className="text-gray-400">Total Iterations</span>
                    <span className="text-white font-medium">{metrics.total_iterations || "—"}</span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-white/5">
                    <span className="text-gray-400">Successful Iterations</span>
                    <span className="text-white font-medium">{metrics.successful_iterations || "—"}</span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-white/5">
                    <span className="text-gray-400">Brand Mentions</span>
                    <span className="text-white font-medium">{metrics.brand_mentions || "—"}</span>
                  </div>
                  <div className="flex items-center justify-between py-3">
                    <span className="text-gray-400">Avg Response Time</span>
                    <span className="text-white font-medium">
                      {metrics.avg_latency ? `${metrics.avg_latency.toFixed(0)}ms` : "—"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              <div className="glass-card rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Insights</h3>
                <div className="space-y-4">
                  {metrics.visibility_score !== undefined && metrics.visibility_score < 0.5 && (
                    <div className="flex items-start gap-3 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                      <svg className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-amber-400">Low Visibility</p>
                        <p className="text-xs text-gray-500">Your brand appears in less than half of AI responses. Consider improving your online presence.</p>
                      </div>
                    </div>
                  )}
                  
                  {metrics.consistency_score !== undefined && metrics.consistency_score > 0.7 && (
                    <div className="flex items-start gap-3 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                      <svg className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-emerald-400">High Consistency</p>
                        <p className="text-xs text-gray-500">AI models consistently represent your brand in a similar way across responses.</p>
                      </div>
                    </div>
                  )}

                  {metrics.hallucination_rate !== undefined && metrics.hallucination_rate > 0.1 && (
                    <div className="flex items-start gap-3 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20">
                      <svg className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-rose-400">Hallucination Detected</p>
                        <p className="text-xs text-gray-500">Some AI responses contain inaccurate information about your brand.</p>
                      </div>
                    </div>
                  )}

                  {(!metrics.visibility_score || metrics.visibility_score >= 0.5) && 
                   (!metrics.hallucination_rate || metrics.hallucination_rate <= 0.1) && (
                    <div className="flex items-start gap-3 p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
                      <svg className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-cyan-400">Good Performance</p>
                        <p className="text-xs text-gray-500">Your brand is well-represented in AI responses with minimal issues.</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="glass-card rounded-2xl p-12 text-center animate-fade-in-up stagger-2">
            <div className="w-16 h-16 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Analysis Failed</h3>
            <p className="text-gray-500 max-w-md mx-auto mb-6">
              Something went wrong during the analysis. Please try again or contact support.
            </p>
            <Link href="/experiments/new" className="btn-primary inline-flex items-center gap-2">
              <span>Create New Analysis</span>
            </Link>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/5 animate-fade-in-up stagger-4">
          <Link href="/experiments" className="btn-secondary">
            ← All Analyses
          </Link>
          <Link href="/experiments/new" className="btn-primary inline-flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>New Analysis</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
