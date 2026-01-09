"use client";

import { useQuery } from "@tanstack/react-query";
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
                <h3 className="text-lg font-semibold text-white">Recommended Prompts</h3>
                <span className="text-xs text-cyan-400 bg-cyan-500/10 px-2 py-1 rounded-full border border-cyan-500/20">
                    AI Suggested
                </span>
            </div>

            <div className="space-y-3">
                {RECOMMENDATIONS.map((rec) => (
                    <div
                        key={rec.id}
                        className="p-3 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 hover:border-white/10 transition-colors group cursor-pointer"
                    >
                        <div className="flex items-center justify-between mb-1">
                            <span className="text-xs text-gray-400 uppercase tracking-wider font-medium">
                                {rec.category}
                            </span>
                            <span className={`text-xs px-1.5 py-0.5 rounded ${rec.difficulty === 'High' ? 'text-amber-400 bg-amber-500/10' :
                                rec.difficulty === 'Medium' ? 'text-blue-400 bg-blue-500/10' :
                                    'text-emerald-400 bg-emerald-500/10'
                                }`}>
                                {rec.difficulty} Difficulty
                            </span>
                        </div>
                        <p className="text-sm text-gray-200 font-medium group-hover:text-white mb-2">
                            "{rec.text}"
                        </p>
                        <Link
                            href={`/experiments/new?prompt=${encodeURIComponent(rec.text)}`}
                            className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                            Use this prompt →
                        </Link>
                    </div>
                ))}
            </div>
        </Card>
    );
}
