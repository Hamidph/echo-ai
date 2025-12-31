"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { Navbar } from "@/components/Navbar";
import { experimentsApi, billingApi } from "@/lib/api";

const providers = [
  {
    id: "openai",
    name: "OpenAI",
    description: "GPT-4o and GPT-4 Turbo",
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
        <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z" />
      </svg>
    ),
    color: "cyan",
  },
  {
    id: "perplexity",
    name: "Perplexity",
    description: "Search-augmented with citations",
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
      </svg>
    ),
    color: "violet",
  },
  {
    id: "anthropic",
    name: "Anthropic",
    description: "Claude 3.5 Sonnet",
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
      </svg>
    ),
    color: "pink",
  },
];

export default function NewExperimentPage() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const [prompt, setPrompt] = useState("");
  const [targetBrand, setTargetBrand] = useState("");
  const [competitors, setCompetitors] = useState("");
  const [selectedProvider, setSelectedProvider] = useState("openai");
  const [iterations, setIterations] = useState(10);
  const [error, setError] = useState("");

  const { data: usage } = useQuery({
    queryKey: ["usage"],
    queryFn: billingApi.getUsage,
    enabled: !!user,
  });

  const createMutation = useMutation({
    mutationFn: experimentsApi.create,
    onSuccess: (data) => {
      router.push(`/experiments/${data.experiment_id}`);
    },
    onError: (err) => {
      setError(err instanceof Error ? err.message : "Failed to create experiment");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!prompt.trim()) {
      setError("Please enter a prompt");
      return;
    }

    if (!targetBrand.trim()) {
      setError("Please enter a target brand");
      return;
    }

    createMutation.mutate({
      prompt: prompt.trim(),
      target_brand: targetBrand.trim(),
      competitor_brands: competitors ? competitors.split(",").map((c) => c.trim()).filter(Boolean) : [],
      provider: selectedProvider,
      iterations,
    });
  };

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

  const remainingQuota = usage?.remaining || 0;
  const canSubmit = prompt.trim() && targetBrand.trim() && iterations <= remainingQuota;

  return (
    <div className="min-h-screen mesh-bg">
      <Navbar />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
          <h1 className="font-display text-display-xs md:text-display-sm font-bold text-white mb-2">
            New Visibility Analysis
          </h1>
          <p className="text-gray-400">
            Configure and run a new AI visibility analysis for your brand
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm animate-fade-in">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error}
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Prompt Section */}
          <div className="glass-card rounded-2xl p-6 animate-fade-in-up stagger-1">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-sm text-cyan-400">1</span>
              Query Configuration
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Prompt
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="input-field min-h-[120px] resize-none"
                  placeholder="What is the best CRM software for small businesses?"
                  rows={4}
                />
                <p className="mt-2 text-xs text-gray-600">
                  Enter the question users might ask where your brand could appear in the response.
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Target Brand
                  </label>
                  <input
                    type="text"
                    value={targetBrand}
                    onChange={(e) => setTargetBrand(e.target.value)}
                    className="input-field"
                    placeholder="Salesforce"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Competitor Brands <span className="text-gray-600">(optional)</span>
                  </label>
                  <input
                    type="text"
                    value={competitors}
                    onChange={(e) => setCompetitors(e.target.value)}
                    className="input-field"
                    placeholder="HubSpot, Zoho, Pipedrive"
                  />
                  <p className="mt-1 text-xs text-gray-600">Comma-separated list</p>
                </div>
              </div>
            </div>
          </div>

          {/* Provider Section */}
          <div className="glass-card rounded-2xl p-6 animate-fade-in-up stagger-2">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span className="w-8 h-8 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-sm text-violet-400">2</span>
              AI Provider
            </h2>
            
            <div className="grid md:grid-cols-3 gap-4">
              {providers.map((provider) => (
                <button
                  key={provider.id}
                  type="button"
                  onClick={() => setSelectedProvider(provider.id)}
                  className={`p-4 rounded-xl border text-left transition-all ${
                    selectedProvider === provider.id
                      ? `border-${provider.color}-500/50 bg-${provider.color}-500/10`
                      : "border-white/10 bg-white/5 hover:border-white/20"
                  }`}
                >
                  <div className={`w-10 h-10 rounded-lg mb-3 flex items-center justify-center ${
                    selectedProvider === provider.id
                      ? `bg-${provider.color}-500/20 text-${provider.color}-400`
                      : "bg-white/5 text-gray-400"
                  }`}>
                    {provider.icon}
                  </div>
                  <h3 className={`font-semibold mb-1 ${
                    selectedProvider === provider.id ? "text-white" : "text-gray-300"
                  }`}>
                    {provider.name}
                  </h3>
                  <p className="text-xs text-gray-500">{provider.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Iterations Section */}
          <div className="glass-card rounded-2xl p-6 animate-fade-in-up stagger-3">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span className="w-8 h-8 rounded-lg bg-pink-500/10 border border-pink-500/20 flex items-center justify-center text-sm text-pink-400">3</span>
              Iterations
            </h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Number of iterations</span>
                <span className="text-2xl font-bold text-white">{iterations}</span>
              </div>
              
              <input
                type="range"
                min="5"
                max="100"
                step="5"
                value={iterations}
                onChange={(e) => setIterations(Number(e.target.value))}
                className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-cyan-500"
              />
              
              <div className="flex justify-between text-xs text-gray-600">
                <span>5</span>
                <span>25</span>
                <span>50</span>
                <span>75</span>
                <span>100</span>
              </div>

              <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10">
                <div>
                  <p className="text-sm text-gray-300">Remaining quota</p>
                  <p className="text-xs text-gray-600">Higher iterations = more statistical significance</p>
                </div>
                <span className={`text-2xl font-bold ${remainingQuota < iterations ? "text-rose-400" : "text-emerald-400"}`}>
                  {remainingQuota}
                </span>
              </div>
            </div>
          </div>

          {/* Submit */}
          <div className="flex items-center justify-between pt-4 animate-fade-in-up stagger-4">
            <Link href="/experiments" className="btn-secondary">
              Cancel
            </Link>
            <button
              type="submit"
              disabled={!canSubmit || createMutation.isPending}
              className="btn-primary inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createMutation.isPending ? (
                <>
                  <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Running Analysis...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span>Run Analysis</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
