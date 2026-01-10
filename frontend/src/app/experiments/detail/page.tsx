"use client";

import { useState, useEffect, Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";
import { experimentsApi } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";

function ExperimentDetailContent() {
    const searchParams = useSearchParams();
    const experimentId = searchParams.get("id");
    const { user, isLoading: authLoading } = useAuth();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    const { data: experimentData, isLoading, refetch } = useQuery({
        queryKey: ["experiment", experimentId],
        queryFn: () => (experimentId ? experimentsApi.getDetails(experimentId) : Promise.reject("No ID")),
        enabled: !!user && !!experimentId,
        refetchInterval: (query) => ((query.state.data as any)?.status === "running" ? 3000 : false),
    });

    const experiment = experimentData as any;

    if (authLoading || isLoading) {
        return (
            <div className="min-h-screen bg-[#FDFCF8] flex items-center justify-center">
                <div className="relative">
                    <div className="w-16 h-16 border-4 border-blue-500/20 rounded-full" />
                    <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
                </div>
            </div>
        );
    }

    if (!experiment || !experimentId) {
        return (
            <div className="min-h-screen bg-[#FDFCF8]">
                <Navbar />
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 pt-24 text-center">
                    <h1 className="text-2xl font-bold text-slate-900 mb-4">
                        {!experimentId ? "Invalid Experiment ID" : "Analysis not found"}
                    </h1>
                    <Link href="/experiments" className="text-blue-600 hover:text-blue-500">
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
        <div className="min-h-screen bg-[#FDFCF8]">
            <Navbar />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-28">
                {/* Header */}
                <div className="mb-8">
                    <Link href="/experiments" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 transition-colors mb-4">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                        Back to analyses
                    </Link>

                    <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                            <h1 className="font-display text-2xl md:text-3xl font-bold text-slate-900 mb-2 truncate">
                                {experiment.prompt}
                            </h1>
                            <div className="flex items-center gap-4 text-sm text-slate-500">
                                <span>Target: <span className="text-slate-900 font-medium">{experiment.target_brand}</span></span>
                                <span>•</span>
                                <span className="capitalize">{experiment.config?.llm_provider || "openai"}</span>
                                <span>•</span>
                                <span>{experiment.config?.iterations || 10} iterations</span>
                            </div>
                        </div>
                        <span className={`px-3 py-1.5 text-sm font-medium rounded-full border ${isCompleted ? "bg-emerald-50 text-emerald-700 border-emerald-200" :
                            isRunning ? "bg-blue-50 text-blue-700 border-blue-200 animate-pulse" :
                                isFailed ? "bg-rose-50 text-rose-700 border-rose-200" :
                                    "bg-amber-50 text-amber-700 border-amber-200"
                            }`}>
                            {experiment.status}
                        </span>
                    </div>
                </div>

                {/* Running State */}
                {isRunning && (
                    <div className="bg-white border border-stone-200 rounded-2xl p-12 text-center mb-8 shadow-sm">
                        <div className="relative w-20 h-20 mx-auto mb-6">
                            <div className="absolute inset-0 border-4 border-blue-500/20 rounded-full" />
                            <div className="absolute inset-0 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                            <div className="absolute inset-3 bg-gradient-to-br from-blue-500/20 to-violet-500/20 rounded-full" />
                        </div>
                        <h2 className="text-xl font-semibold text-slate-900 mb-2">Running Analysis</h2>
                        <p className="text-slate-500 mb-6">
                            Monte Carlo simulation in progress. This usually takes 30-60 seconds.
                        </p>
                        <button
                            onClick={() => refetch()}
                            className="inline-flex items-center gap-2 px-4 py-2 text-sm text-blue-600 hover:text-blue-700 transition-colors"
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
                    <div className="bg-rose-50 border border-rose-200 rounded-2xl p-8 text-center mb-8">
                        <div className="w-16 h-16 rounded-full bg-rose-100 flex items-center justify-center mx-auto mb-4">
                            <svg className="w-8 h-8 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </div>
                        <h2 className="text-xl font-semibold text-slate-900 mb-2">Analysis Failed</h2>
                        <p className="text-slate-600 mb-6">
                            Something went wrong during the analysis. Please try again.
                        </p>
                        <Link
                            href="/experiments/new"
                            className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-all"
                        >
                            Try Again
                        </Link>
                    </div>
                )}

                {/* Results */}
                {isCompleted && (
                    <>
                        {/* Main Metrics */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                            {/* Visibility Score */}
                            <div className="bg-white border border-stone-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
                                        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                        </svg>
                                    </div>
                                    <div className="group relative">
                                        <div className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center cursor-help">
                                            <span className="text-xs text-slate-500 font-medium">i</span>
                                        </div>
                                        <div className="absolute right-0 top-6 w-64 p-3 bg-slate-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 shadow-lg">
                                            <strong>Visibility Score</strong><br />How often your brand appears in AI responses for this query. Higher is better.
                                        </div>
                                    </div>
                                </div>
                                <p className="text-sm text-slate-500 mb-1">Visibility</p>
                                <p className="text-3xl font-bold text-slate-900">
                                    {metrics.visibility_score?.toFixed(0) || 0}%
                                </p>
                            </div>

                            {/* Share of Voice */}
                            <div className="bg-white border border-stone-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="w-10 h-10 rounded-xl bg-violet-100 flex items-center justify-center">
                                        <svg className="w-5 h-5 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
                                        </svg>
                                    </div>
                                    <div className="group relative">
                                        <div className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center cursor-help">
                                            <span className="text-xs text-slate-500 font-medium">i</span>
                                        </div>
                                        <div className="absolute right-0 top-6 w-64 p-3 bg-slate-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 shadow-lg">
                                            <strong>Share of Voice</strong><br />Your brand&apos;s mention share compared to competitors. Indicates market dominance in AI responses.
                                        </div>
                                    </div>
                                </div>
                                <p className="text-sm text-slate-500 mb-1">Share of Voice</p>
                                <p className="text-3xl font-bold text-slate-900">
                                    {metrics.share_of_voice?.toFixed(0) || 0}%
                                </p>
                            </div>

                            {/* Consistency */}
                            <div className="bg-white border border-stone-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="w-10 h-10 rounded-xl bg-fuchsia-100 flex items-center justify-center">
                                        <svg className="w-5 h-5 text-fuchsia-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                        </svg>
                                    </div>
                                    <div className="group relative">
                                        <div className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center cursor-help">
                                            <span className="text-xs text-slate-500 font-medium">i</span>
                                        </div>
                                        <div className="absolute right-0 top-6 w-64 p-3 bg-slate-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 shadow-lg">
                                            <strong>Consistency</strong><br />How consistently AI describes your brand across multiple queries. Higher means more stable messaging.
                                        </div>
                                    </div>
                                </div>
                                <p className="text-sm text-slate-500 mb-1">Consistency</p>
                                <p className="text-3xl font-bold text-slate-900">
                                    {metrics.consistency_score?.toFixed(0) || 0}%
                                </p>
                            </div>

                            {/* Hallucination Check */}
                            <div className="bg-white border border-stone-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-4">
                                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${metrics.has_hallucinations ? "bg-rose-100" : "bg-emerald-100"
                                        }`}>
                                        {metrics.has_hallucinations ? (
                                            <svg className="w-5 h-5 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                            </svg>
                                        ) : (
                                            <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                        )}
                                    </div>
                                    <div className="group relative">
                                        <div className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center cursor-help">
                                            <span className="text-xs text-slate-500 font-medium">i</span>
                                        </div>
                                        <div className="absolute right-0 top-6 w-64 p-3 bg-slate-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 shadow-lg">
                                            <strong>Hallucinations</strong><br />Whether AI makes false claims about your brand. None detected is ideal.
                                        </div>
                                    </div>
                                </div>
                                <p className="text-sm text-slate-500 mb-1">Hallucinations</p>
                                <p className={`text-3xl font-bold ${metrics.has_hallucinations ? "text-rose-600" : "text-emerald-600"}`}>
                                    {metrics.has_hallucinations ? "Detected" : "None"}
                                </p>
                            </div>
                        </div>

                        {/* Detailed Results */}
                        <div className="grid lg:grid-cols-2 gap-6">
                            {/* Insights */}
                            <div className="bg-white border border-stone-200 rounded-2xl p-6 shadow-sm">
                                <h3 className="text-lg font-semibold text-slate-900 mb-4">Insights</h3>
                                <div className="space-y-4">
                                    {metrics.visibility_score >= 70 && (
                                        <div className="flex items-start gap-3 p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
                                            <svg className="w-5 h-5 text-emerald-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            <div>
                                                <p className="text-sm font-medium text-slate-900">Strong Visibility</p>
                                                <p className="text-xs text-slate-600 mt-1">
                                                    Your brand appears in {metrics.visibility_score?.toFixed(0)}% of AI responses for this query.
                                                </p>
                                            </div>
                                        </div>
                                    )}

                                    {metrics.visibility_score < 50 && (
                                        <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-xl">
                                            <svg className="w-5 h-5 text-amber-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                            </svg>
                                            <div>
                                                <p className="text-sm font-medium text-slate-900">Low Visibility</p>
                                                <p className="text-xs text-slate-600 mt-1">
                                                    Your brand appears in only {metrics.visibility_score?.toFixed(0)}% of responses. Consider improving your online presence.
                                                </p>
                                            </div>
                                        </div>
                                    )}

                                    {metrics.consistency_score < 60 && (
                                        <div className="flex items-start gap-3 p-4 bg-violet-50 border border-violet-200 rounded-xl">
                                            <svg className="w-5 h-5 text-violet-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            <div>
                                                <p className="text-sm font-medium text-slate-900">Inconsistent Responses</p>
                                                <p className="text-xs text-slate-600 mt-1">
                                                    AI models are giving varied descriptions of your brand. Consider standardizing your brand messaging.
                                                </p>
                                            </div>
                                        </div>
                                    )}

                                    {metrics.has_hallucinations && (
                                        <div className="flex items-start gap-3 p-4 bg-rose-50 border border-rose-200 rounded-xl">
                                            <svg className="w-5 h-5 text-rose-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                            </svg>
                                            <div>
                                                <p className="text-sm font-medium text-slate-900">Hallucinations Detected</p>
                                                <p className="text-xs text-slate-600 mt-1">
                                                    AI models are making unverified claims about your brand. Review and correct misinformation.
                                                </p>
                                            </div>
                                        </div>
                                    )}

                                    {!metrics.has_hallucinations && metrics.visibility_score >= 50 && metrics.consistency_score >= 60 && (
                                        <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-xl">
                                            <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                            </svg>
                                            <div>
                                                <p className="text-sm font-medium text-slate-900">Good Standing</p>
                                                <p className="text-xs text-slate-600 mt-1">
                                                    Your brand is performing well in AI responses with consistent and accurate information.
                                                </p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Recommendations */}
                            <div className="bg-white border border-stone-200 rounded-2xl p-6 shadow-sm">
                                <h3 className="text-lg font-semibold text-slate-900 mb-4">Recommendations</h3>
                                <div className="space-y-3">
                                    <div className="flex items-start gap-3 p-3 bg-slate-50 rounded-xl">
                                        <div className="w-6 h-6 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                                            <span className="text-xs text-blue-600 font-medium">1</span>
                                        </div>
                                        <div>
                                            <p className="text-sm text-slate-900">Improve content on review sites</p>
                                            <p className="text-xs text-slate-500 mt-1">G2, Capterra, and TrustRadius are frequently cited by AI models.</p>
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-3 p-3 bg-slate-50 rounded-xl">
                                        <div className="w-6 h-6 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                                            <span className="text-xs text-blue-600 font-medium">2</span>
                                        </div>
                                        <div>
                                            <p className="text-sm text-slate-900">Update Wikipedia presence</p>
                                            <p className="text-xs text-slate-500 mt-1">Ensure your Wikipedia article is accurate and up-to-date.</p>
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-3 p-3 bg-slate-50 rounded-xl">
                                        <div className="w-6 h-6 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                                            <span className="text-xs text-blue-600 font-medium">3</span>
                                        </div>
                                        <div>
                                            <p className="text-sm text-slate-900">Create comparison content</p>
                                            <p className="text-xs text-slate-500 mt-1">Publish detailed comparisons with competitors on your blog.</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Raw Analysis Data */}
                        <div className="mt-8 bg-white border border-stone-200 rounded-2xl overflow-hidden shadow-sm">
                            <div className="p-6 border-b border-stone-200">
                                <h3 className="text-lg font-semibold text-slate-900">Raw Analysis Data</h3>
                                <p className="text-sm text-slate-500 mt-1">
                                    Review the actual responses from the AI model to verify why they were scored this way.
                                </p>
                            </div>
                            <div className="max-h-[600px] overflow-y-auto p-4 space-y-4 bg-slate-50">
                                {(experiment.iterations || []).map((iter: any) => (
                                    <div key={iter.iteration_index} className="bg-white rounded-xl p-4 border border-stone-200">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-xs font-mono text-blue-600">Iteration #{iter.iteration_index + 1}</span>
                                            <span className={`text-xs px-2 py-0.5 rounded-full ${iter.is_success ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700"
                                                }`}>
                                                {iter.status}
                                            </span>
                                        </div>
                                        <div className="prose prose-sm max-w-none">
                                            <pre className="whitespace-pre-wrap text-xs text-slate-700 font-mono bg-slate-100 p-3 rounded-lg">
                                                {iter.raw_response ? iter.raw_response : "(No response content)"}
                                            </pre>
                                        </div>
                                        {iter.error_message && (
                                            <div className="mt-2 text-xs text-rose-600">
                                                Error: {iter.error_message}
                                            </div>
                                        )}
                                    </div>
                                ))}
                                {(!experiment.iterations || experiment.iterations.length === 0) && (
                                    <div className="text-center py-8 text-slate-500">
                                        No iteration data available.
                                    </div>
                                )}
                            </div>
                        </div>
                    </>
                )}

                {/* Actions */}
                <div className="flex items-center justify-between mt-8 pt-8 border-t border-stone-200">
                    <div className="text-sm text-slate-500">
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
                        className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-all shadow-md hover:shadow-lg"
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

export default function ExperimentDetailPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen bg-[#FDFCF8] flex items-center justify-center">
                <div className="relative">
                    <div className="w-16 h-16 border-4 border-blue-500/20 rounded-full" />
                    <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
                </div>
            </div>
        }>
            <ExperimentDetailContent />
        </Suspense>
    );
}
