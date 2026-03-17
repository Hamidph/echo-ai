"use client";

import Link from "next/link";
import { Navbar } from "@/components/Navbar";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#FDFCF8] text-slate-900 selection:bg-blue-100 selection:text-blue-900">
      <Navbar />

      {/* Hero Section - Creamy, Modern, Geometric */}
      <section id="demo" className="pt-24 pb-20 border-b border-stone-200/60 overflow-hidden relative">
        <div className="max-w-5xl mx-auto px-6 text-center relative z-10">
          {/* Announcement Pill */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-stone-200 shadow-sm mb-8 animate-fade-in hover:border-blue-200 transition-colors cursor-default">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            <span className="text-sm font-semibold text-slate-600 tracking-tight">Now tracking Claude 4.5 & GPT-5.2</span>
          </div>

          <h1 className="font-heading text-6xl md:text-7xl font-bold text-slate-900 mb-6 tracking-tight leading-[1.05]">
            Your brand&apos;s AI visibility —{" "}
            <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 bg-clip-text text-transparent">statistically proven.</span>
          </h1>

          <p className="text-xl text-slate-500 max-w-2xl mx-auto mb-4 leading-relaxed font-medium">
            Single-shot AI checks are statistically worthless. Echo AI runs Monte Carlo simulations across hundreds of prompts to give you <strong className="text-slate-700">confidence intervals</strong>, not guesses.
          </p>
          <p className="text-base text-slate-400 max-w-xl mx-auto mb-10 font-medium">
            Track ChatGPT, Claude, Perplexity & more — with statistical reliability your competitors can&apos;t match.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
            <Link href="/register" className="px-8 py-4 text-base font-bold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-all shadow-lg hover:shadow-blue-500/20 hover:-translate-y-0.5">
              Start Free Trial
            </Link>
            <Link href="#pricing" className="px-8 py-4 text-base font-bold text-slate-600 bg-white border border-stone-200 rounded-xl hover:bg-stone-50 hover:border-stone-300 transition-all shadow-sm">
              View Pricing
            </Link>
          </div>

          {/* Product Visual - Clean, Creamy Dashboard */}
          <div className="relative max-w-5xl mx-auto animate-fade-in-up">
            {/* Gradient Blur Backing */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[110%] h-[110%] bg-gradient-to-tr from-blue-100/40 via-purple-100/40 to-amber-50/40 blur-[100px] -z-10 rounded-full" />

            <div className="bg-white rounded-2xl border border-stone-200 shadow-2xl shadow-stone-200/50 overflow-hidden">
              {/* Fake Browser Header */}
              <div className="flex items-center justify-between px-4 py-3 border-b border-stone-100 bg-stone-50/50">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-stone-200" />
                  <div className="w-3 h-3 rounded-full bg-stone-200" />
                </div>
                <div className="flex items-center gap-2 px-3 py-1 bg-white border border-stone-200 rounded-md shadow-sm">
                  {/* Logo Icon Tiny */}
                  <div className="w-8 h-5 rounded bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-[8px] text-white font-bold">ECHO</div>
                  <span className="text-xs font-semibold text-slate-500">app.echoai.com</span>
                </div>
                <div className="w-10" />
              </div>

              {/* Dashboard Content */}
              <div className="p-8">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                  {[
                    { label: "Visibility Score", val: "78/100", change: "+12%", color: "blue" },
                    { label: "Market Rank", val: "#2", change: "+1", color: "emerald" },
                    { label: "Sentiment", val: "Positive", change: "98%", color: "purple" },
                    { label: "Total Citations", val: "1,240", change: "+54", color: "amber" },
                  ].map((stat) => {
                    const colorVariants = {
                      blue: { text: "text-blue-600", bg: "bg-blue-50" },
                      emerald: { text: "text-emerald-600", bg: "bg-emerald-50" },
                      purple: { text: "text-purple-600", bg: "bg-purple-50" },
                      amber: { text: "text-amber-600", bg: "bg-amber-50" },
                    }[stat.color] || { text: "text-slate-600", bg: "bg-slate-50" };

                    return (
                      <div key={stat.label} className="p-4 rounded-xl border border-stone-100 bg-stone-50/50">
                        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">{stat.label}</div>
                        <div className="text-2xl font-bold text-slate-900 mb-1">{stat.val}</div>
                        <div className={`text-xs font-bold ${colorVariants.text} ${colorVariants.bg} inline-block px-1.5 py-0.5 rounded`}>{stat.change}</div>
                      </div>
                    );
                  })}
                </div>

                <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                  Live Prompt Monitoring
                </h3>
                <div className="overflow-hidden rounded-xl border border-stone-200">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-stone-50 text-xs text-slate-500 font-bold uppercase">
                      <tr>
                        <th className="px-6 py-3">Prompt / Query</th>
                        <th className="px-6 py-3">AI Model</th>
                        <th className="px-6 py-3">Your Position</th>
                        <th className="px-6 py-3">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-stone-100 bg-white">
                      {[
                        { q: "Top 5 CRM tools for startups 2026", m: "GPT-5.2", p: "#1 Recommended", s: "Winning" },
                        { q: "Best project management software", m: "Claude 4.5", p: "#3 Listed", s: "Tracking" },
                        { q: "Cheap alternatives to Salesforce", m: "Perplexity", p: "#1 Citation", s: "Winning" },
                        { q: "Marketing analytics platform comparison", m: "Gemini", p: "Not Found", s: "Critical" },
                      ].map((row, i) => (
                        <tr key={i} className="hover:bg-blue-50/30 transition-colors">
                          <td className="px-6 py-4 font-medium text-slate-900">{row.q}</td>
                          <td className="px-6 py-4 text-slate-500">{row.m}</td>
                          <td className="px-6 py-4 font-bold text-slate-700">{row.p}</td>
                          <td className="px-6 py-4">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${row.s === "Winning" ? "bg-emerald-50 text-emerald-700 border-emerald-100" :
                              row.s === "Critical" ? "bg-rose-50 text-rose-700 border-rose-100" :
                                "bg-stone-100 text-stone-600 border-stone-200"
                              }`}>
                              {row.s}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Section - Creamy Cards */}
      <section id="features" className="py-24 bg-white border-t border-stone-100">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div>
              <div className="text-blue-600 font-bold tracking-wide uppercase text-sm mb-2">Search Analytics</div>
              <h2 className="font-heading text-4xl font-bold text-slate-900 mb-6">
                Stop guessing.<br />Start measuring.
              </h2>
              <p className="text-lg text-slate-500 mb-8 leading-relaxed">
                Traditional SEO tools can&apos;t see inside the &quot;black box&quot; of LLMs. Echo AI generates thousands of probes to map exactly how, when, and why AI recommends your brand.
              </p>
              <ul className="space-y-4">
                {[
                  "Reverse-engineer ranking factors for GPT-5.2 & Claude",
                  "Track citation drift over time",
                  "Identify negative sentiment hallucinations"
                ].map(item => (
                  <li key={item} className="flex items-center gap-3 text-slate-700 font-medium">
                    <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={3}><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
                    </div>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="relative">
              {/* Abstract Visual */}
              <div className="absolute top-10 -left-10 w-24 h-24 bg-purple-200 rounded-full blur-2xl opacity-50" />
              <div className="absolute bottom-10 -right-10 w-32 h-32 bg-blue-200 rounded-full blur-2xl opacity-50" />

              <div className="grid gap-6">
                <div className="bg-[#FDFCF8] p-6 rounded-2xl border border-stone-100 shadow-xl shadow-stone-200/50">
                  <div className="flex justify-between items-center mb-4">
                    <div className="font-bold text-slate-900">Competition Analysis</div>
                    <div className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded">LIVE</div>
                  </div>
                  <div className="space-y-3">
                    <div className="w-full bg-stone-100 rounded-full h-2.5 overflow-hidden">
                      <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: '65%' }}></div>
                    </div>
                    <div className="flex justify-between text-xs text-slate-500 font-medium">
                      <span>Your Brand</span>
                      <span>65% SOV</span>
                    </div>
                    <div className="w-full bg-stone-100 rounded-full h-2.5 overflow-hidden">
                      <div className="bg-stone-300 h-2.5 rounded-full" style={{ width: '25%' }}></div>
                    </div>
                    <div className="flex justify-between text-xs text-slate-500 font-medium">
                      <span>Competitor A</span>
                      <span>25% SOV</span>
                    </div>
                  </div>
                </div>

                <div className="bg-[#FDFCF8] p-6 rounded-2xl border border-stone-100 shadow-xl shadow-stone-200/50 ml-8">
                  <div className="flex gap-4 items-start">
                    <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 font-bold shrink-0">AI</div>
                    <div>
                      <div className="text-sm font-bold text-slate-900 mb-1">Recommendation Engine</div>
                      <div className="text-sm text-slate-500 italic">&quot;The best option for enterprise scaling is [Your Brand] due to its robust API...&quot;</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 bg-[#FDFCF8] border-t border-stone-100">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-10">
            <div className="text-blue-600 font-bold tracking-wide uppercase text-sm mb-2">Pricing</div>
            <h2 className="font-heading text-4xl md:text-5xl font-bold text-slate-900 mb-4">
              Simple, transparent pricing
            </h2>
            <p className="text-lg text-slate-500 max-w-2xl mx-auto mb-2">
              Unlimited seats on all plans. Start your 14-day free trial — no credit card required.
            </p>
            {/* Annual toggle */}
            <div className="inline-flex items-center gap-3 mt-6 px-4 py-2 bg-white border border-stone-200 rounded-full shadow-sm">
              <span className="text-sm font-semibold text-slate-600">Monthly</span>
              <div className="relative">
                <input type="checkbox" id="annual-toggle" className="sr-only peer" />
                <label htmlFor="annual-toggle" className="block w-11 h-6 bg-stone-200 peer-checked:bg-blue-600 rounded-full cursor-pointer transition-colors after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-5" />
              </div>
              <span className="text-sm font-semibold text-slate-600">
                Annual <span className="text-emerald-600 font-bold">Save 20%</span>
              </span>
            </div>
          </div>

          <div className="grid md:grid-cols-5 gap-4">
            {/* Free Tier */}
            <div className="bg-white rounded-2xl border border-stone-200 p-6 hover:border-blue-200 transition-colors flex flex-col">
              <div className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Free</div>
              <div className="flex items-baseline gap-1 mb-1">
                <span className="text-4xl font-bold text-slate-900">$0</span>
                <span className="text-slate-500">/mo</span>
              </div>
              <div className="text-xs text-slate-400 mb-4">Then 5 prompts/month forever</div>
              <div className="text-sm text-slate-600 mb-6">14-day trial: 25 prompts</div>
              <ul className="space-y-3 mb-6 flex-1">
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  <strong>25</strong> prompts during trial
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Monte Carlo iterations
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Basic analytics
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Unlimited seats
                </li>
              </ul>
              <Link href="/register" className="block w-full py-3 text-center text-sm font-bold text-slate-700 bg-stone-100 rounded-xl hover:bg-stone-200 transition-colors">
                Start Free Trial
              </Link>
            </div>

            {/* Starter Tier */}
            <div className="bg-white rounded-2xl border border-stone-200 p-6 hover:border-blue-200 transition-colors flex flex-col">
              <div className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Starter</div>
              <div className="flex items-baseline gap-1 mb-1">
                <span className="text-4xl font-bold text-slate-900">$49</span>
                <span className="text-slate-500">/mo</span>
              </div>
              <div className="text-xs text-slate-400 mb-4">$1.63/prompt</div>
              <div className="text-sm text-slate-600 mb-6">For growing brands</div>
              <ul className="space-y-3 mb-6 flex-1">
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  <strong>30</strong> prompts/month
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Confidence intervals
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Competitor tracking
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Unlimited seats
                </li>
              </ul>
              <Link href="/register" className="block w-full py-3 text-center text-sm font-bold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-colors">
                Start Trial
              </Link>
            </div>

            {/* Growth Tier — Most Popular */}
            <div className="bg-white rounded-2xl border-2 border-blue-500 p-6 relative shadow-lg shadow-blue-500/10 flex flex-col">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-blue-600 text-white text-xs font-bold rounded-full whitespace-nowrap">Most Popular</div>
              <div className="text-sm font-bold text-blue-600 uppercase tracking-wider mb-2">Growth</div>
              <div className="flex items-baseline gap-1 mb-1">
                <span className="text-4xl font-bold text-slate-900">$149</span>
                <span className="text-slate-500">/mo</span>
              </div>
              <div className="text-xs text-slate-400 mb-4">$1.49/prompt</div>
              <div className="text-sm text-slate-600 mb-6">Agency entry point</div>
              <ul className="space-y-3 mb-6 flex-1">
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  <strong>100</strong> prompts/month
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Statistical significance badges
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Advanced reports & exports
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Unlimited seats
                </li>
              </ul>
              <Link href="/register" className="block w-full py-3 text-center text-sm font-bold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-colors">
                Start Trial
              </Link>
            </div>

            {/* Pro Tier */}
            <div className="bg-white rounded-2xl border border-stone-200 p-6 hover:border-blue-200 transition-colors flex flex-col">
              <div className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Pro</div>
              <div className="flex items-baseline gap-1 mb-1">
                <span className="text-4xl font-bold text-slate-900">$349</span>
                <span className="text-slate-500">/mo</span>
              </div>
              <div className="text-xs text-slate-400 mb-4">$1.16/prompt</div>
              <div className="text-sm text-slate-600 mb-6">For serious agencies</div>
              <ul className="space-y-3 mb-6 flex-1">
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  <strong>300</strong> prompts/month
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  White-label reports
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Priority support
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-600">
                  <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Unlimited seats
                </li>
              </ul>
              <Link href="/register" className="block w-full py-3 text-center text-sm font-bold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-colors">
                Start Trial
              </Link>
            </div>

            {/* Enterprise Tier */}
            <div className="bg-slate-900 rounded-2xl p-6 text-white flex flex-col">
              <div className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Enterprise</div>
              <div className="flex items-baseline gap-1 mb-1">
                <span className="text-4xl font-bold">Custom</span>
              </div>
              <div className="text-xs text-slate-400 mb-4">&lt;$1.00/prompt</div>
              <div className="text-sm text-slate-400 mb-6">500+ prompts/month</div>
              <ul className="space-y-3 mb-6 flex-1">
                <li className="flex items-center gap-2 text-sm text-slate-300">
                  <svg className="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  White-label workspace
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-300">
                  <svg className="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Custom SLA
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-300">
                  <svg className="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Dedicated support
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-300">
                  <svg className="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  Unlimited seats
                </li>
              </ul>
              <Link href="mailto:sales@echoai.uk" className="block w-full py-3 text-center text-sm font-bold text-slate-900 bg-white rounded-xl hover:bg-slate-100 transition-colors">
                Contact Sales
              </Link>
            </div>
          </div>

          {/* Annual savings note */}
          <p className="text-center text-sm text-slate-400 mt-6">
            Save 2 months with annual billing. All prices in USD.
          </p>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 bg-white border-t border-stone-100">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="font-heading text-4xl md:text-5xl font-bold text-slate-900 mb-8">
            Take control of your <br />AI Narrative.
          </h2>
          <Link href="/register" className="inline-flex px-10 py-5 text-lg font-bold text-white bg-slate-900 rounded-2xl hover:bg-slate-800 hover:scale-105 transition-all shadow-xl">
            Get Started Now
          </Link>
          <p className="mt-6 text-sm text-slate-400 font-medium">No credit card required • 14-day free trial</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-[#FDFCF8] border-t border-stone-100">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-md bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-[10px]">ECHO</div>
              <span className="font-heading font-bold text-xl text-slate-900">Echo AI</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-slate-500 font-medium">
              <Link href="/terms" className="hover:text-slate-700 transition-colors">Terms of Service</Link>
              <Link href="/privacy" className="hover:text-slate-700 transition-colors">Privacy Policy</Link>
              <a href="mailto:support@echoai.com" className="hover:text-slate-700 transition-colors">Contact</a>
            </div>
            <div className="text-sm text-slate-500 font-medium">© 2026 Echo AI</div>
          </div>
        </div>
      </footer>
    </div>
  );
}

