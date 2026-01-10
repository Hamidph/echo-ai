"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";
import { experimentsApi } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { useState } from "react";

export default function ExperimentsPage() {
  const { user, isLoading: authLoading } = useAuth();
  const [page, setPage] = useState(0);
  const pageSize = 10;

  const { data: experiments, isLoading: experimentsLoading } = useQuery({
    queryKey: ["experiments", page],
    queryFn: () => experimentsApi.list(pageSize, page * pageSize),
    enabled: !!user,
  });

  const totalPages = experiments ? Math.ceil(experiments.total / pageSize) : 0;

  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#FDFCF8] flex items-center justify-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-blue-500/20 rounded-full" />
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
        </div>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    const styles = {
      completed: "bg-emerald-100 text-emerald-700 border-emerald-200",
      running: "bg-blue-100 text-blue-700 border-blue-200 animate-pulse",
      failed: "bg-rose-100 text-rose-700 border-rose-200",
      pending: "bg-amber-100 text-amber-700 border-amber-200",
    };
    return styles[status as keyof typeof styles] || styles.pending;
  };

  return (
    <div className="min-h-screen bg-[#FDFCF8]">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-28">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-slate-900 mb-1">
              Analyses
            </h1>
            <p className="text-slate-500">
              Track your brand visibility across AI platforms
            </p>
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

        {/* Filters */}
        <div className="flex items-center gap-4 mb-6">
          <div className="flex items-center gap-2 bg-white border border-stone-200 rounded-xl p-1 shadow-sm">
            <button className="px-3 py-1.5 text-sm text-slate-900 bg-slate-100 rounded-lg font-medium">All</button>
            <button className="px-3 py-1.5 text-sm text-slate-500 hover:text-slate-900 transition-colors">Completed</button>
            <button className="px-3 py-1.5 text-sm text-slate-500 hover:text-slate-900 transition-colors">Running</button>
            <button className="px-3 py-1.5 text-sm text-slate-500 hover:text-slate-900 transition-colors">Failed</button>
          </div>
          <div className="flex-1" />
          <div className="relative">
            <svg className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Search analyses..."
              className="w-64 pl-10 pr-4 py-2 bg-white border border-stone-200 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 shadow-sm"
            />
          </div>
        </div>

        {/* Content */}
        <div className="bg-white border border-stone-200 rounded-2xl overflow-hidden shadow-sm">
          {experimentsLoading ? (
            <div className="flex justify-center py-16">
              <div className="relative">
                <div className="w-10 h-10 border-4 border-blue-500/20 rounded-full" />
                <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
              </div>
            </div>
          ) : experiments?.experiments?.length > 0 ? (
            <>
              {/* Table Header */}
              <div className="grid grid-cols-12 gap-4 px-6 py-4 border-b border-stone-200 text-xs font-medium text-slate-500 uppercase tracking-wider bg-slate-50">
                <div className="col-span-5">Prompt</div>
                <div className="col-span-2">Target Brand</div>
                <div className="col-span-2">Provider</div>
                <div className="col-span-2">Status</div>
                <div className="col-span-1"></div>
              </div>

              {/* Table Body */}
              <div className="divide-y divide-stone-100">
                {experiments.experiments.map((exp: {
                  experiment_id: string;
                  prompt: string;
                  target_brand: string;
                  config: { llm_provider: string };
                  status: string;
                  created_at: string;
                }) => (
                  <Link
                    key={exp.experiment_id}
                    href={`/experiments/detail?id=${exp.experiment_id}`}
                    className="grid grid-cols-12 gap-4 px-6 py-4 hover:bg-slate-50 transition-colors group"
                  >
                    <div className="col-span-5">
                      <p className="text-sm text-slate-900 truncate group-hover:text-blue-600 transition-colors font-medium">
                        {exp.prompt}
                      </p>
                      <p className="text-xs text-slate-400 mt-1">
                        {new Date(exp.created_at).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                          hour: "numeric",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                    <div className="col-span-2 flex items-center">
                      <span className="text-sm text-slate-600">{exp.target_brand}</span>
                    </div>
                    <div className="col-span-2 flex items-center">
                      <span className="text-sm text-slate-600 capitalize">{exp.config?.llm_provider || "openai"}</span>
                    </div>
                    <div className="col-span-2 flex items-center">
                      <span className={`text-xs px-2.5 py-1 rounded-full border ${getStatusBadge(exp.status)}`}>
                        {exp.status}
                      </span>
                    </div>
                    <div className="col-span-1 flex items-center justify-end">
                      <svg className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </Link>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between px-6 py-4 border-t border-stone-200 bg-slate-50">
                  <p className="text-sm text-slate-500">
                    Showing {page * pageSize + 1} to {Math.min((page + 1) * pageSize, experiments.total)} of {experiments.total}
                  </p>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setPage((p) => Math.max(0, p - 1))}
                      disabled={page === 0}
                      className="px-3 py-1.5 text-sm text-slate-600 hover:text-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Previous
                    </button>
                    <div className="flex items-center gap-1">
                      {[...Array(Math.min(5, totalPages))].map((_, i) => (
                        <button
                          key={i}
                          onClick={() => setPage(i)}
                          className={`w-8 h-8 text-sm rounded-lg transition-colors ${page === i ? "bg-blue-600 text-white" : "text-slate-500 hover:text-slate-900 hover:bg-slate-100"
                            }`}
                        >
                          {i + 1}
                        </button>
                      ))}
                    </div>
                    <button
                      onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                      disabled={page >= totalPages - 1}
                      className="px-3 py-1.5 text-sm text-slate-600 hover:text-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-16">
              <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">No analyses yet</h3>
              <p className="text-slate-500 mb-6 max-w-sm mx-auto">
                Run your first visibility analysis to see how AI perceives your brand.
              </p>
              <Link
                href="/experiments/new"
                className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-all shadow-md"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Create First Analysis
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
