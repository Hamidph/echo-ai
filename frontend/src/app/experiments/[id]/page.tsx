"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";
import { experimentsApi } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";

export default function ExperimentDetailPage() {
  const params = useParams();
  const experimentId = params.id as string;
  const { user, isLoading: authLoading } = useAuth();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data: experiment, isLoading, refetch } = useQuery({
    queryKey: ["experiment", experimentId],
    queryFn: () => experimentsApi.get(experimentId),
    enabled: !!user,
    refetchInterval: (query) => (query.state.data?.status === "running" ? 3000 : false),
  });

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-[#030712] flex items-center justify-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-cyan-500/20 rounded-full" />
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
        </div>
      </div>
    );
  }

  if (!experiment) {
    return (
      <div className="min-h-screen bg-[#030712]">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Analysis not found</h1>
          <Link href="/experiments" className="text-cyan-400 hover:text-cyan-300">
            Back to analyses
          </Link>
        </div>
      </div>
    );
  }

  const isRunning = experiment.status === "running";
  const isCompleted = experiment.status === "completed";
  const isFailed = experiment.status === "failed";

  // Get metrics from the first batch run if available
  const batchRun = experiment.batch_runs?.[0];
  const rawMetrics = batchRun?.metrics || {};

  // Map backend metrics structure to frontend expected format
  const metrics = {
    visibility_score: (rawMetrics.target_visibility?.visibility_rate || 0) * 100,
    share_of_voice: (rawMetrics.share_of_voice?.[0]?.share || 0) * 100,
    consistency_score: (rawMetrics.consistency?.consistency_score || 0) * 100,
    has_hallucinations: rawMetrics.hallucination_rate > 0,
    total_responses: rawMetrics.total_responses || 0,
  };

  return (
    <div className="min-h-screen bg-[#030712]">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/experiments" className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-white transition-colors mb-4">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to analyses
          </Link>
          
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <h1 className="font-display text-2xl md:text-3xl font-bold text-white mb-2 truncate">
                {experiment.prompt}
              </h1>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>Target: <span className="text-white">{experiment.target_brand}</span></span>
                <span>•</span>
                <span className="capitalize">{experiment.config?.llm_provider || "openai"}</span>
                <span>•</span>
                <span>{experiment.config?.iterations || 10} iterations</span>
              </div>
            </div>
            <span className={`px-3 py-1.5 text-sm font-medium rounded-full border ${
              isCompleted ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" :
              isRunning ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/20 animate-pulse" :
              isFailed ? "bg-rose-500/10 text-rose-400 border-rose-500/20" :
              "bg-amber-500/10 text-amber-400 border-amber-500/20"
            }`}>
              {experiment.status}
            </span>
          </div>
        </div>

        {/* Running State */}
        {isRunning && (
          <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-12 text-center mb-8">
            <div className="relative w-20 h-20 mx-auto mb-6">
              <div className="absolute inset-0 border-4 border-cyan-500/20 rounded-full" />
              <div className="absolute inset-0 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
              <div className="absolute inset-3 bg-gradient-to-br from-cyan-500/20 to-violet-500/20 rounded-full" />
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">Running Analysis</h2>
            <p className="text-gray-500 mb-6">
              Monte Carlo simulation in progress. This usually takes 30-60 seconds.
            </p>
            <button
              onClick={() => refetch()}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh Status
            </button>
          </div>
        )}

        {/* Failed State */}
        {isFailed && (
          <div className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-8 text-center mb-8">
            <div className="w-16 h-16 rounded-full bg-rose-500/20 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">Analysis Failed</h2>
            <p className="text-gray-400 mb-6">
              Something went wrong during the analysis. Please try again.
            </p>
            <Link
              href="/experiments/new"
              className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-cyan-500 to-violet-500 rounded-lg hover:scale-105 transition-all"
            >
              Try Again
            </Link>
          </div>
        )}

        {/* Results */}
        {isCompleted && (
          <>
            {/* Main Metrics */}
            <div className="grid grid-cols-4 gap-4 mb-8">
              {/* Visibility Score */}
              <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                    <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </div>
                </div>
                <p className="text-sm text-gray-500 mb-1">Visibility</p>
                <p className="text-3xl font-bold text-white">
                  {metrics.visibility_score?.toFixed(0) || 0}%
                </p>
              </div>

              {/* Share of Voice */}
              <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
                    <svg className="w-5 h-5 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
                    </svg>
                  </div>
                </div>
                <p className="text-sm text-gray-500 mb-1">Share of Voice</p>
                <p className="text-3xl font-bold text-white">
                  {metrics.share_of_voice?.toFixed(0) || 0}%
                </p>
              </div>

              {/* Consistency */}
              <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-fuchsia-500/10 flex items-center justify-center">
                    <svg className="w-5 h-5 text-fuchsia-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                </div>
                <p className="text-sm text-gray-500 mb-1">Consistency</p>
                <p className="text-3xl font-bold text-white">
                  {metrics.consistency_score?.toFixed(0) || 0}%
                </p>
              </div>

              {/* Hallucination Check */}
              <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    metrics.has_hallucinations ? "bg-rose-500/10" : "bg-emerald-500/10"
                  }`}>
                    {metrics.has_hallucinations ? (
                      <svg className="w-5 h-5 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    )}
                  </div>
                </div>
                <p className="text-sm text-gray-500 mb-1">Hallucinations</p>
                <p className={`text-3xl font-bold ${metrics.has_hallucinations ? "text-rose-400" : "text-emerald-400"}`}>
                  {metrics.has_hallucinations ? "Detected" : "None"}
                </p>
              </div>
            </div>

            {/* Detailed Results */}
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Insights */}
              <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Insights</h3>
                <div className="space-y-4">
                  {metrics.visibility_score >= 70 && (
                    <div className="flex items-start gap-3 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                      <svg className="w-5 h-5 text-emerald-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-white">Strong Visibility</p>
                        <p className="text-xs text-gray-400 mt-1">
                          Your brand appears in {metrics.visibility_score?.toFixed(0)}% of AI responses for this query.
                        </p>
                      </div>
                    </div>
                  )}
                  
                  {metrics.visibility_score < 50 && (
                    <div className="flex items-start gap-3 p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                      <svg className="w-5 h-5 text-amber-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-white">Low Visibility</p>
                        <p className="text-xs text-gray-400 mt-1">
                          Your brand appears in only {metrics.visibility_score?.toFixed(0)}% of responses. Consider improving your online presence.
                        </p>
                      </div>
                    </div>
                  )}

                  {metrics.consistency_score < 60 && (
                    <div className="flex items-start gap-3 p-4 bg-violet-500/10 border border-violet-500/20 rounded-lg">
                      <svg className="w-5 h-5 text-violet-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-white">Inconsistent Responses</p>
                        <p className="text-xs text-gray-400 mt-1">
                          AI models are giving varied descriptions of your brand. Consider standardizing your brand messaging.
                        </p>
                      </div>
                    </div>
                  )}

                  {metrics.has_hallucinations && (
                    <div className="flex items-start gap-3 p-4 bg-rose-500/10 border border-rose-500/20 rounded-lg">
                      <svg className="w-5 h-5 text-rose-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-white">Hallucinations Detected</p>
                        <p className="text-xs text-gray-400 mt-1">
                          AI models are making unverified claims about your brand. Review and correct misinformation.
                        </p>
                      </div>
                    </div>
                  )}

                  {!metrics.has_hallucinations && metrics.visibility_score >= 50 && metrics.consistency_score >= 60 && (
                    <div className="flex items-start gap-3 p-4 bg-cyan-500/10 border border-cyan-500/20 rounded-lg">
                      <svg className="w-5 h-5 text-cyan-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-white">Good Standing</p>
                        <p className="text-xs text-gray-400 mt-1">
                          Your brand is performing well in AI responses with consistent and accurate information.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Recommendations */}
              <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Recommendations</h3>
                <div className="space-y-3">
                  <div className="flex items-start gap-3 p-3 bg-white/5 rounded-lg">
                    <div className="w-6 h-6 rounded bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                      <span className="text-xs text-cyan-400 font-medium">1</span>
                    </div>
                    <div>
                      <p className="text-sm text-white">Improve content on review sites</p>
                      <p className="text-xs text-gray-500 mt-1">G2, Capterra, and TrustRadius are frequently cited by AI models.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 bg-white/5 rounded-lg">
                    <div className="w-6 h-6 rounded bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                      <span className="text-xs text-cyan-400 font-medium">2</span>
                    </div>
                    <div>
                      <p className="text-sm text-white">Update Wikipedia presence</p>
                      <p className="text-xs text-gray-500 mt-1">Ensure your Wikipedia article is accurate and up-to-date.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 bg-white/5 rounded-lg">
                    <div className="w-6 h-6 rounded bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                      <span className="text-xs text-cyan-400 font-medium">3</span>
                    </div>
                    <div>
                      <p className="text-sm text-white">Create comparison content</p>
                      <p className="text-xs text-gray-500 mt-1">Publish detailed comparisons with competitors on your blog.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between mt-8 pt-8 border-t border-white/5">
          <div className="text-sm text-gray-500">
            {mounted ? (
              <>Created {new Date(experiment.created_at).toLocaleDateString("en-US", {
                month: "long",
                day: "numeric",
                year: "numeric",
                hour: "numeric",
                minute: "2-digit",
              })}</>
            ) : (
              <span>&nbsp;</span>
            )}
          </div>
          <Link
            href="/experiments/new"
            className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-cyan-500 to-violet-500 rounded-lg hover:scale-105 transition-all"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Analysis
          </Link>
        </div>
      </div>
    </div>
  );
}
