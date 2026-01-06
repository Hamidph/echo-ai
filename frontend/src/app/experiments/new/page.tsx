"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";
import { useAuth } from "@/hooks/useAuth";
import { useMutation, useQuery } from "@tanstack/react-query";
import { experimentsApi, billingApi } from "@/lib/api";
import { toast } from "react-hot-toast";

const providers = [
  {
    id: "openai",
    name: "OpenAI",
    description: "GPT-5.1 & GPT-4o",
    icon: (
      <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
        <path d="M22.282 9.821a5.985 5.985 0 0 0-.516-4.91 6.046 6.046 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a5.985 5.985 0 0 0-3.998 2.9 6.046 6.046 0 0 0 .743 7.097 5.98 5.98 0 0 0 .51 4.911 6.051 6.051 0 0 0 6.515 2.9A5.985 5.985 0 0 0 13.26 24a6.056 6.056 0 0 0 5.772-4.206 5.99 5.99 0 0 0 3.997-2.9 6.056 6.056 0 0 0-.747-7.073zM13.26 22.43a4.476 4.476 0 0 1-2.876-1.04l.141-.081 4.779-2.758a.795.795 0 0 0 .392-.681v-6.737l2.02 1.168a.071.071 0 0 1 .038.052v5.583a4.504 4.504 0 0 1-4.494 4.494zM3.6 18.304a4.47 4.47 0 0 1-.535-3.014l.142.085 4.783 2.759a.771.771 0 0 0 .78 0l5.843-3.369v2.332a.08.08 0 0 1-.033.062L9.74 19.95a4.5 4.5 0 0 1-6.14-1.646zM2.34 7.896a4.485 4.485 0 0 1 2.366-1.973V11.6a.766.766 0 0 0 .388.676l5.815 3.355-2.02 1.168a.076.076 0 0 1-.071 0l-4.83-2.786A4.504 4.504 0 0 1 2.34 7.872zm16.597 3.855l-5.833-3.387L15.119 7.2a.076.076 0 0 1 .071 0l4.83 2.791a4.494 4.494 0 0 1-.676 8.105v-5.678a.79.79 0 0 0-.407-.667zm2.01-3.023l-.141-.085-4.774-2.782a.776.776 0 0 0-.785 0L9.409 9.23V6.897a.066.066 0 0 1 .028-.061l4.83-2.787a4.5 4.5 0 0 1 6.68 4.66zm-12.64 4.135l-2.02-1.164a.08.08 0 0 1-.038-.057V6.075a4.5 4.5 0 0 1 7.375-3.453l-.142.08-4.778 2.758a.795.795 0 0 0-.393.681zm1.097-2.365l2.602-1.5 2.607 1.5v2.999l-2.597 1.5-2.607-1.5z" />
      </svg>
    ),
  },
  {
    id: "perplexity",
    name: "Perplexity",
    description: "Sonar Pro (Search-augmented)",
    icon: (
      <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
        <path d="M12 0L1.5 6v12L12 24l10.5-6V6L12 0zm0 2.311l8.077 4.616v9.146L12 20.689l-8.077-4.616V6.927L12 2.311z" />
        <path d="M12 5.5L6.5 8.5v7l5.5 3 5.5-3v-7L12 5.5zm0 2.311l3.077 1.766v3.846L12 15.189l-3.077-1.766V9.577L12 7.811z" />
      </svg>
    ),
  },
  {
    id: "anthropic",
    name: "Anthropic",
    description: "Claude 4.5 Sonnet",
    icon: (
      <svg viewBox="0 0 24 24" className="w-6 h-6" fill="currentColor">
        <path d="M17.304 3.541l-5.304 16.918-5.304-16.918h-3.696l7.5 19.918h3l7.5-19.918h-3.696z" />
      </svg>
    ),
  },
];

function NewExperimentForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialPrompt = searchParams.get("prompt") || "";

  const { user } = useAuth();
  const [step, setStep] = useState(1);
  const [prompt, setPrompt] = useState(initialPrompt);
  const [targetBrand, setTargetBrand] = useState("");
  const [competitorBrands, setCompetitorBrands] = useState("");
  const [provider, setProvider] = useState<string | null>(null);
  const [iterations, setIterations] = useState(10);
  const [isRecurring, setIsRecurring] = useState(false);
  const [frequency, setFrequency] = useState("daily");

  const { data: usage, isLoading: usageLoading } = useQuery({
    queryKey: ["usage"],
    queryFn: billingApi.getUsage,
    enabled: !!user,
  });

  const createExperimentMutation = useMutation({
    mutationFn: experimentsApi.create,
    onSuccess: (data) => {
      toast.success("Analysis started successfully!");
      router.push(`/experiments/detail?id=${(data as any).experiment_id}`);
    },
    onError: (error: unknown) => {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to start analysis.");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt || !targetBrand || !provider || iterations < 1) {
      toast.error("Please fill in all required fields.");
      return;
    }

    createExperimentMutation.mutate({
      prompt,
      target_brand: targetBrand,
      competitor_brands: competitorBrands.split(",").map((b) => b.trim()).filter(Boolean),
      provider: provider,
      iterations,
      is_recurring: isRecurring,
      frequency: isRecurring ? frequency : undefined,
    });
  };

  // Navigation debouncing to prevent accidental double-clicks submitting the next step
  const [isNavigating, setIsNavigating] = useState(false);

  const handleNextStep = () => {
    if (step < 3) {
      setIsNavigating(true);
      setStep(step + 1);
      // Prevent interactions with the next step's primary button for a brief moment
      setTimeout(() => setIsNavigating(false), 500);
    }
  };

  const remainingQuota = usage?.remaining ?? 100; // Default to 100 if usage not loaded yet
  const canProceed = step === 1 ? (prompt && targetBrand) : step === 2 ? provider : iterations > 0;

  return (
    <div className="min-h-screen bg-[#030712]">
      <Navbar />

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/experiments" className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-white transition-colors mb-4">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to analyses
          </Link>
          <h1 className="font-display text-2xl md:text-3xl font-bold text-white mb-2">
            New Visibility Analysis
          </h1>
          <p className="text-gray-500">
            Configure and run a new AI visibility analysis for your brand
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center gap-4 mb-8">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center gap-3">
              <button
                onClick={() => s < step && setStep(s)}
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all ${s === step
                  ? "bg-gradient-to-r from-cyan-500 to-violet-500 text-white"
                  : s < step
                    ? "bg-cyan-500/20 text-cyan-400"
                    : "bg-white/5 text-gray-500"
                  }`}
              >
                {s < step ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  s
                )}
              </button>
              {s < 3 && (
                <div className={`w-16 h-0.5 ${s < step ? "bg-cyan-500/50" : "bg-white/10"}`} />
              )}
            </div>
          ))}
        </div>

        <form onSubmit={(e) => e.preventDefault()}>
          {/* Step 1: Query Configuration */}
          {step === 1 && (
            <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6 animate-fade-in">
              <h2 className="text-lg font-semibold text-white mb-6">Query Configuration</h2>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Prompt <span className="text-rose-400">*</span>
                  </label>
                  <textarea
                    rows={3}
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 resize-none"
                    placeholder="What is the best CRM software for small businesses?"
                  />
                  <p className="mt-2 text-xs text-gray-500">
                    Enter the question users might ask where your brand could appear
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Target Brand <span className="text-rose-400">*</span>
                    </label>
                    <input
                      type="text"
                      value={targetBrand}
                      onChange={(e) => setTargetBrand(e.target.value)}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
                      placeholder="Salesforce"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Competitors <span className="text-gray-500">(optional)</span>
                    </label>
                    <input
                      type="text"
                      value={competitorBrands}
                      onChange={(e) => setCompetitorBrands(e.target.value)}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
                      placeholder="HubSpot, Zoho, Pipedrive"
                    />
                    <p className="mt-2 text-xs text-gray-500">Comma-separated list</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: AI Provider */}
          {step === 2 && (
            <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6 animate-fade-in">
              <h2 className="text-lg font-semibold text-white mb-6">Select AI Provider</h2>

              <div className="grid gap-4">
                {providers.map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => setProvider(p.id)}
                    className={`flex items-center gap-4 p-4 rounded-xl border transition-all text-left ${provider === p.id
                      ? "bg-cyan-500/10 border-cyan-500/50"
                      : "bg-white/5 border-white/10 hover:border-white/20"
                      }`}
                  >
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${provider === p.id ? "bg-cyan-500/20 text-cyan-400" : "bg-white/5 text-gray-400"
                      }`}>
                      {p.icon}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-white">{p.name}</p>
                      <p className="text-sm text-gray-500">{p.description}</p>
                    </div>
                    {provider === p.id && (
                      <div className="w-6 h-6 rounded-full bg-cyan-500 flex items-center justify-center">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 3: Configuration */}
          {step === 3 && (
            <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6 animate-fade-in">
              <h2 className="text-lg font-semibold text-white mb-6">Experiment Configuration</h2>

              <div className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-gray-400">Iterations per Experiment</span>
                    <span className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-violet-400 bg-clip-text text-transparent">
                      {iterations}
                    </span>
                  </div>
                  <input
                    type="range"
                    min={5}
                    max={100}
                    step={5}
                    value={iterations}
                    onChange={(e) => setIterations(Number(e.target.value))}
                    className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer accent-cyan-500"
                  />
                  <div className="flex justify-between mt-2 text-xs text-gray-600">
                    <span>5</span>
                    <span>25</span>
                    <span>50</span>
                    <span>75</span>
                    <span>100</span>
                  </div>
                  <p className="mt-2 text-xs text-gray-500">
                    Each experiment runs {iterations} iterations (API calls) for statistical significance
                  </p>
                </div>

                <div>
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                    <div>
                      <h3 className="text-white font-medium">Recurring Experiment</h3>
                      <p className="text-sm text-gray-500">Run this analysis periodically</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setIsRecurring(!isRecurring)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${isRecurring ? "bg-cyan-500" : "bg-white/10"
                        }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${isRecurring ? "translate-x-6" : "translate-x-1"
                          }`}
                      />
                    </button>
                  </div>

                  {isRecurring && (
                    <div className="mt-4 animate-fade-in">
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Frequency
                      </label>
                      <select
                        value={frequency}
                        onChange={(e) => setFrequency(e.target.value)}
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-cyan-500/50 appearance-none"
                      >
                        <option value="daily" className="bg-[#0a0f1a]">Daily</option>
                        <option value="weekly" className="bg-[#0a0f1a]">Weekly</option>
                        <option value="monthly" className="bg-[#0a0f1a]">Monthly</option>
                      </select>
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <span className="text-sm text-gray-400">Remaining prompts</span>
                  <span className={`text-sm font-medium ${remainingQuota >= 1 ? "text-emerald-400" : "text-rose-400"}`}>
                    {usageLoading ? "..." : remainingQuota} prompts
                  </span>
                </div>

                {remainingQuota < 1 && (
                  <div className="flex items-center gap-3 p-4 bg-rose-500/10 border border-rose-500/20 rounded-lg">
                    <svg className="w-5 h-5 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <div className="flex-1">
                      <p className="text-sm text-rose-400">No prompts remaining</p>
                      <p className="text-xs text-gray-500">Upgrade your plan to run more experiments</p>
                    </div>
                    <Link href="/billing" className="text-sm text-cyan-400 hover:text-cyan-300">
                      Upgrade
                    </Link>
                  </div>
                )}

                {/* Summary */}
                <div className="border-t border-white/5 pt-6">
                  <h3 className="text-sm font-medium text-gray-400 mb-4">Summary</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Prompt</span>
                      <span className="text-white truncate max-w-[200px]">{prompt}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Target Brand</span>
                      <span className="text-white">{targetBrand}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Provider</span>
                      <span className="text-white capitalize">{provider}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Iterations</span>
                      <span className="text-white">{iterations}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Schedule</span>
                      <span className="text-white capitalize">
                        {isRecurring ? frequency : "One-time"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between mt-6">
            {step > 1 ? (
              <button
                type="button"
                onClick={() => setStep(step - 1)}
                className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors"
              >
                Back
              </button>
            ) : (
              <div />
            )}

            {step < 3 ? (
              <button
                key={`step-btn-${step}`}
                type="button"
                onClick={handleNextStep}
                disabled={!canProceed || isNavigating}
                className="px-6 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-cyan-500 to-violet-500 rounded-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
              >
                Continue
              </button>
            ) : (
              <button
                key="submit-btn"
                type="button"
                onClick={handleSubmit}
                disabled={!canProceed || createExperimentMutation.isPending || remainingQuota < 1 || isNavigating}
                className="inline-flex items-center gap-2 px-6 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-cyan-500 to-violet-500 rounded-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
              >
                {createExperimentMutation.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                    Running...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Run Analysis
                  </>
                )}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

export default function NewExperimentPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#030712] flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-cyan-500/20 rounded-full" />
        <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
      </div>
    }>
      <NewExperimentForm />
    </Suspense>
  );
}
