"use client";

import Link from "next/link";
import { Navbar } from "@/components/Navbar";

export default function PrivacyPage() {
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
                    <h1 className="text-3xl font-bold text-slate-900 mb-4">Privacy Policy</h1>
                    <p className="text-slate-500 mb-8">Last updated: January 10, 2026</p>

                    <section className="mb-8">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">1. Information We Collect</h2>
                        <p className="text-slate-600 mb-4">
                            Echo AI collects information to provide and improve our visibility intelligence service:
                        </p>
                        <ul className="list-disc list-inside text-slate-600 space-y-2 mb-4">
                            <li><strong>Account Information</strong>: Email address, name, password (hashed)</li>
                            <li><strong>Brand Profile</strong>: Company name, website, industry, competitors</li>
                            <li><strong>Experiment Data</strong>: Prompts, target brands, visibility metrics</li>
                            <li><strong>Usage Data</strong>: Login activity, API usage, feature interactions</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">2. How We Use Your Information</h2>
                        <ul className="list-disc list-inside text-slate-600 space-y-2 mb-4">
                            <li>To provide AI visibility analysis through our Monte Carlo simulation engine</li>
                            <li>To track your brand mentions across OpenAI, Anthropic, and Perplexity</li>
                            <li>To generate visibility reports and competitive benchmarks</li>
                            <li>To process payments via Stripe (we do not store payment card details)</li>
                            <li>To send service notifications and product updates</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">3. Data Storage and Security</h2>
                        <p className="text-slate-600 mb-4">
                            Your data is stored securely using:
                        </p>
                        <ul className="list-disc list-inside text-slate-600 space-y-2 mb-4">
                            <li>PostgreSQL database hosted on Railway with encrypted connections</li>
                            <li>Redis for session caching with TLS encryption</li>
                            <li>JWT-based authentication with secure token rotation</li>
                            <li>HTTPS encryption for all data in transit</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">4. Third-Party Services</h2>
                        <p className="text-slate-600 mb-4">
                            Echo AI integrates with the following third-party services:
                        </p>
                        <ul className="list-disc list-inside text-slate-600 space-y-2 mb-4">
                            <li><strong>OpenAI API</strong>: For GPT-based visibility analysis</li>
                            <li><strong>Anthropic API</strong>: For Claude-based analysis</li>
                            <li><strong>Perplexity API</strong>: For search-augmented analysis</li>
                            <li><strong>Stripe</strong>: For payment processing</li>
                            <li><strong>Railway</strong>: For infrastructure hosting</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">5. Your Rights</h2>
                        <p className="text-slate-600 mb-4">
                            You have the right to:
                        </p>
                        <ul className="list-disc list-inside text-slate-600 space-y-2 mb-4">
                            <li>Access your personal data</li>
                            <li>Correct inaccurate data</li>
                            <li>Request deletion of your account</li>
                            <li>Export your experiment data</li>
                            <li>Opt out of marketing communications</li>
                        </ul>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">6. Data Retention</h2>
                        <p className="text-slate-600 mb-4">
                            We retain your data for as long as your account is active. Experiment results are
                            stored for 12 months for historical analysis. Upon account deletion, personal data
                            is removed within 30 days.
                        </p>
                    </section>

                    <section className="mb-8">
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">7. Contact Us</h2>
                        <p className="text-slate-600">
                            For privacy inquiries, contact our Data Protection Officer at{" "}
                            <a href="mailto:privacy@echoai.com" className="text-blue-600 hover:underline">
                                privacy@echoai.com
                            </a>
                        </p>
                    </section>
                </article>
            </div>
        </div>
    );
}
