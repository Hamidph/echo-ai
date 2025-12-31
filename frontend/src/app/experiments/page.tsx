"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { Navbar } from "@/components/Navbar";
import { experimentsApi } from "@/lib/api";
import { useState } from "react";

export default function ExperimentsPage() {
  const { user, isLoading: authLoading } = useAuth();
  const [page, setPage] = useState(0);
  const limit = 10;

  const { data: experiments, isLoading } = useQuery({
    queryKey: ["experiments", page],
    queryFn: () => experimentsApi.list(limit, page * limit),
    enabled: !!user,
  });

  if (authLoading) {
    return (
      <div className="min-h-screen mesh-bg flex items-center justify-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-cyan-500/20 rounded-full" />
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
        </div>
      </div>
    );
  }

  const totalPages = experiments ? Math.ceil(experiments.total / limit) : 0;

  return (
    <div className="min-h-screen mesh-bg">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8 animate-fade-in">
          <div>
            <h1 className="font-display text-display-xs md:text-display-sm font-bold text-white mb-2">
              Analyses
            </h1>
            <p className="text-gray-400">
              View and manage all your brand visibility analyses
            </p>
          </div>
          <Link
            href="/experiments/new"
            className="btn-primary inline-flex items-center gap-2 text-sm self-start"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>New Analysis</span>
          </Link>
        </div>

        {/* Experiments Table */}
        <div className="glass-card rounded-2xl overflow-hidden animate-fade-in-up">
          {isLoading ? (
            <div className="p-12 flex justify-center">
              <div className="relative">
                <div className="w-12 h-12 border-4 border-cyan-500/20 rounded-full" />
                <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
              </div>
            </div>
          ) : experiments?.experiments?.length > 0 ? (
            <>
              {/* Table Header */}
              <div className="hidden md:grid grid-cols-12 gap-4 px-6 py-4 border-b border-white/5 text-sm font-medium text-gray-500 uppercase tracking-wider">
                <div className="col-span-5">Prompt</div>
                <div className="col-span-2">Target Brand</div>
                <div className="col-span-2">Status</div>
                <div className="col-span-2">Created</div>
                <div className="col-span-1"></div>
              </div>

              {/* Table Body */}
              <div className="divide-y divide-white/5">
                {experiments.experiments.map((exp: {
                  experiment_id: string;
                  prompt: string;
                  target_brand: string;
                  status: string;
                  created_at: string;
                }, index: number) => (
                  <Link
                    key={exp.experiment_id}
                    href={`/experiments/${exp.experiment_id}`}
                    className="block md:grid md:grid-cols-12 gap-4 px-6 py-5 hover:bg-white/5 transition-colors group"
                    style={{ animationDelay: `${index * 0.05}s` }}
                  >
                    {/* Mobile View */}
                    <div className="md:hidden space-y-3">
                      <div className="flex items-start justify-between gap-4">
                        <p className="font-medium text-white group-hover:text-cyan-400 transition-colors">
                          {exp.prompt.length > 80 ? exp.prompt.substring(0, 80) + "..." : exp.prompt}
                        </p>
                        <span className={`badge flex-shrink-0 ${
                          exp.status === "completed" ? "badge-completed" :
                          exp.status === "running" ? "badge-running" :
                          exp.status === "failed" ? "badge-failed" :
                          "badge-pending"
                        }`}>
                          {exp.status}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-400">Target: <span className="text-gray-300">{exp.target_brand}</span></span>
                        <span className="text-gray-600">{new Date(exp.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    {/* Desktop View */}
                    <div className="hidden md:block col-span-5">
                      <p className="font-medium text-white group-hover:text-cyan-400 transition-colors truncate">
                        {exp.prompt.length > 60 ? exp.prompt.substring(0, 60) + "..." : exp.prompt}
                      </p>
                    </div>
                    <div className="hidden md:flex col-span-2 items-center">
                      <span className="text-gray-300 font-medium">{exp.target_brand}</span>
                    </div>
                    <div className="hidden md:flex col-span-2 items-center">
                      <span className={`badge ${
                        exp.status === "completed" ? "badge-completed" :
                        exp.status === "running" ? "badge-running" :
                        exp.status === "failed" ? "badge-failed" :
                        "badge-pending"
                      }`}>
                        {exp.status}
                      </span>
                    </div>
                    <div className="hidden md:flex col-span-2 items-center text-gray-500 text-sm">
                      {new Date(exp.created_at).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        year: "numeric"
                      })}
                    </div>
                    <div className="hidden md:flex col-span-1 items-center justify-end">
                      <svg className="w-5 h-5 text-gray-600 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </Link>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="px-6 py-4 border-t border-white/5 flex items-center justify-between">
                  <p className="text-sm text-gray-500">
                    Showing {page * limit + 1} to {Math.min((page + 1) * limit, experiments.total)} of {experiments.total} results
                  </p>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setPage(p => Math.max(0, p - 1))}
                      disabled={page === 0}
                      className="btn-secondary px-3 py-1.5 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    <button
                      onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
                      disabled={page >= totalPages - 1}
                      className="btn-secondary px-3 py-1.5 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="p-16 text-center">
              <div className="w-20 h-20 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mx-auto mb-6">
                <svg className="w-10 h-10 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">No analyses yet</h3>
              <p className="text-gray-500 mb-8 max-w-md mx-auto">
                Run your first visibility analysis to see how AI models perceive and represent your brand.
              </p>
              <Link
                href="/experiments/new"
                className="btn-primary inline-flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span>Create Your First Analysis</span>
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
