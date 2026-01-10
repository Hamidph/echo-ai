"use client";

import Link from "next/link";
import Card from "@/components/ui/Card";

// Static recommendations for MVP - later connect to AI suggestion API
const RECOMMENDATIONS = [
    {
        id: 1,
        category: "Comparison",
        text: "Compare [My Brand] vs [Competitor] for enterprise features",
        difficulty: "Medium",
    },
    {
        id: 2,
        category: "Buying Intent",
        text: "What is the best [Industry] software for small businesses?",
        difficulty: "High",
    },
    {
        id: 3,
        category: "Reputation",
        text: "Is [My Brand] reliable for mission-critical workloads?",
        difficulty: "Low",
    },
];

export function RecommendedPrompts() {
    return (
        <Card className="h-full">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-900">Recommended Prompts</h3>
                <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded-full border border-blue-200">
                    AI Suggested
                </span>
            </div>

            <div className="space-y-3">
                {RECOMMENDATIONS.map((rec) => (
                    <div
                        key={rec.id}
                        className="p-3 rounded-lg border border-stone-200 bg-slate-50 hover:bg-blue-50 hover:border-blue-200 transition-colors group cursor-pointer"
                    >
                        <div className="flex items-center justify-between mb-1">
                            <span className="text-xs text-slate-400 uppercase tracking-wider font-medium">
                                {rec.category}
                            </span>
                            <span className={`text-xs px-1.5 py-0.5 rounded ${rec.difficulty === 'High' ? 'text-amber-600 bg-amber-100' :
                                rec.difficulty === 'Medium' ? 'text-blue-600 bg-blue-100' :
                                    'text-emerald-600 bg-emerald-100'
                                }`}>
                                {rec.difficulty} Difficulty
                            </span>
                        </div>
                        <p className="text-sm text-slate-700 font-medium group-hover:text-slate-900 mb-2">
                            &quot;{rec.text}&quot;
                        </p>
                        <Link
                            href={`/experiments/new?prompt=${encodeURIComponent(rec.text)}`}
                            className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                            Use this prompt →
                        </Link>
                    </div>
                ))}
            </div>
        </Card>
    );
}
