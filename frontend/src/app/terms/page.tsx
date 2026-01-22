"use client";

import Link from "next/link";
import { Navbar } from "@/components/Navbar";

export default function TermsPage() {
    return (
        <div className="min-h-screen bg-[#FDFCF8]">
            <Navbar />

            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-24">
                {/* Breadcrumb */}
                <div className="mb-6">
                    <Link
                        href="/"
                        className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 transition-colors"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                        Back to Home
                    </Link>
                </div>

                <article className="prose prose-slate max-w-none">
                    <h1 className="text-3xl font-bold text-slate-900 mb-4">Terms of Service</h1>
                    <p className="text-slate-500 mb-8">Last updated: January 10, 2026</p>

                    <section className="mb-8">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">1. Acceptance of Terms</h2>
                        <p className="text-slate-600 mb-4">
                            By accessing or using Echo AI (&quot;Service&quot;), you agree to be bound by these Terms of Service.
                            If you do not agree to these terms, please do not use our Service.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">2. Description of Service</h2>
                        <p className="text-slate-600 mb-4">
                            Echo AI is a visibility intelligence platform that tracks brand presence across AI-powered
                            search engines including OpenAI, Anthropic Claude, and Perplexity. Our service provides:
                        </p>
                        <ul className="list-disc list-inside text-slate-600 space-y-2 mb-4">
                            <li>Monte Carlo simulations for brand visibility analysis (10-100 iterations per prompt)</li>
                            <li>Citation tracking and sentiment analysis</li>
                            <li>Competitor benchmarking and share of voice metrics</li>
                            <li>Recurring experiment scheduling (daily, weekly, monthly)</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">3. Pricing and Plans</h2>
                        <p className="text-slate-600 mb-4">
                            Echo AI offers the following pricing tiers (each prompt runs 10 iterations):
                        </p>
                        <ul className="list-disc list-inside text-slate-600 space-y-2 mb-4">
                            <li><strong>Free</strong>: £0/month - 3 prompts per month</li>
                            <li><strong>Starter</strong>: £35/month - 10 prompts per month</li>
                            <li><strong>Pro</strong>: £55/month - 15 prompts per month</li>
                            <li><strong>Enterprise</strong>: £169/month - 50 prompts per month</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">4. User Responsibilities</h2>
                        <p className="text-slate-600 mb-4">
                            You agree to use the Service in compliance with all applicable laws and regulations.
                            You are responsible for maintaining the confidentiality of your account credentials.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">5. Intellectual Property</h2>
                        <p className="text-slate-600 mb-4">
                            All content, features, and functionality of Echo AI are owned by Echo AI and are
                            protected by international copyright, trademark, and other intellectual property laws.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">6. Limitation of Liability</h2>
                        <p className="text-slate-600 mb-4">
                            Echo AI shall not be liable for any indirect, incidental, special, consequential,
                            or punitive damages resulting from your use of the Service.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">7. Contact Information</h2>
                        <p className="text-slate-600">
                            For questions about these Terms, please contact us at{" "}
                            <a href="mailto:support@echoai.com" className="text-blue-600 hover:underline">
                                support@echoai.com
                            </a>
                        </p>
                    </section>
                </article>
            </div>
        </div>
    );
}
