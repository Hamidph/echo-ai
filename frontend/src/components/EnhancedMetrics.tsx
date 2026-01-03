"use client";

import Card, { CardHeader, CardTitle, CardContent } from "./ui/Card";
import { InfoTooltip } from "./ui/Tooltip";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  tooltip?: string;
  icon: React.ReactNode;
  color: "cyan" | "violet" | "emerald" | "amber" | "rose";
}

export function MetricCard({
  title,
  value,
  change,
  tooltip,
  icon,
  color,
}: MetricCardProps) {
  const colorStyles = {
    cyan: {
      bg: "bg-cyan-500/10",
      border: "border-cyan-500/20",
      text: "text-cyan-400",
      glow: "group-hover:shadow-[0_0_30px_rgba(34,211,238,0.2)]",
    },
    violet: {
      bg: "bg-violet-500/10",
      border: "border-violet-500/20",
      text: "text-violet-400",
      glow: "group-hover:shadow-[0_0_30px_rgba(139,92,246,0.2)]",
    },
    emerald: {
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
      text: "text-emerald-400",
      glow: "group-hover:shadow-[0_0_30px_rgba(16,185,129,0.2)]",
    },
    amber: {
      bg: "bg-amber-500/10",
      border: "border-amber-500/20",
      text: "text-amber-400",
      glow: "group-hover:shadow-[0_0_30px_rgba(245,158,11,0.2)]",
    },
    rose: {
      bg: "bg-rose-500/10",
      border: "border-rose-500/20",
      text: "text-rose-400",
      glow: "group-hover:shadow-[0_0_30px_rgba(244,63,94,0.2)]",
    },
  };

  const styles = colorStyles[color];

  return (
    <Card className={`group ${styles.glow}`} hover>
      <div className="flex items-start justify-between mb-4">
        <div
          className={`w-12 h-12 rounded-xl ${styles.bg} border ${styles.border} flex items-center justify-center ${styles.text}`}
        >
          {icon}
        </div>
        {tooltip && <InfoTooltip content={tooltip} />}
      </div>
      <h3 className="text-sm font-medium text-gray-400 mb-2">{title}</h3>
      <div className="flex items-end justify-between">
        <p className={`text-3xl font-bold ${styles.text}`}>{value}</p>
        {change !== undefined && (
          <div
            className={`flex items-center gap-1 text-sm font-medium ${
              change >= 0 ? "text-emerald-400" : "text-rose-400"
            }`}
          >
            <svg
              className={`w-4 h-4 ${change < 0 ? "rotate-180" : ""}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
              />
            </svg>
            <span>{Math.abs(change)}%</span>
          </div>
        )}
      </div>
    </Card>
  );
}

interface SentimentBreakdownProps {
  positive: number;
  neutral: number;
  negative: number;
}

export function SentimentBreakdown({
  positive,
  neutral,
  negative,
}: SentimentBreakdownProps) {
  const total = positive + neutral + negative;
  const positivePercent = (positive / total) * 100;
  const neutralPercent = (neutral / total) * 100;
  const negativePercent = (negative / total) * 100;

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          Sentiment Breakdown
          <InfoTooltip content="Distribution of positive, neutral, and negative mentions across all AI responses" />
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Progress bar */}
        <div className="h-3 bg-white/5 rounded-full overflow-hidden flex mb-6">
          <div
            className="bg-emerald-500 transition-all"
            style={{ width: `${positivePercent}%` }}
            title={`Positive: ${positivePercent.toFixed(1)}%`}
          />
          <div
            className="bg-amber-500 transition-all"
            style={{ width: `${neutralPercent}%` }}
            title={`Neutral: ${neutralPercent.toFixed(1)}%`}
          />
          <div
            className="bg-rose-500 transition-all"
            style={{ width: `${negativePercent}%`}}
            title={`Negative: ${negativePercent.toFixed(1)}%`}
          />
        </div>

        {/* Legend */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-emerald-500" />
              <span className="text-sm text-gray-300">Positive</span>
            </div>
            <span className="text-sm font-medium text-emerald-400">
              {positivePercent.toFixed(1)}% ({positive})
            </span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-amber-500" />
              <span className="text-sm text-gray-300">Neutral</span>
            </div>
            <span className="text-sm font-medium text-amber-400">
              {neutralPercent.toFixed(1)}% ({neutral})
            </span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-rose-500" />
              <span className="text-sm text-gray-300">Negative</span>
            </div>
            <span className="text-sm font-medium text-rose-400">
              {negativePercent.toFixed(1)}% ({negative})
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

interface TrendIndicatorProps {
  value: number;
  previousValue: number;
  label: string;
}

export function TrendIndicator({
  value,
  previousValue,
  label,
}: TrendIndicatorProps) {
  const change = ((value - previousValue) / previousValue) * 100;
  const isPositive = change >= 0;

  return (
    <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
      <div>
        <p className="text-sm text-gray-400">{label}</p>
        <p className="text-2xl font-bold text-white mt-1">{value}%</p>
      </div>
      <div className="text-right">
        <div
          className={`flex items-center gap-1 text-sm font-medium ${
            isPositive ? "text-emerald-400" : "text-rose-400"
          }`}
        >
          <svg
            className={`w-4 h-4 ${!isPositive ? "rotate-180" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
            />
          </svg>
          <span>{Math.abs(change).toFixed(1)}%</span>
        </div>
        <p className="text-xs text-gray-500 mt-1">vs last period</p>
      </div>
    </div>
  );
}

interface RecommendationProps {
  title: string;
  description: string;
  priority: "high" | "medium" | "low";
  action?: string;
}

export function Recommendation({
  title,
  description,
  priority,
  action,
}: RecommendationProps) {
  const priorityStyles = {
    high: "border-rose-500/30 bg-rose-500/5",
    medium: "border-amber-500/30 bg-amber-500/5",
    low: "border-cyan-500/30 bg-cyan-500/5",
  };

  const priorityColors = {
    high: "text-rose-400",
    medium: "text-amber-400",
    low: "text-cyan-400",
  };

  return (
    <div className={`p-4 rounded-xl border ${priorityStyles[priority]}`}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          <svg
            className={`w-5 h-5 ${priorityColors[priority]}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-medium text-white mb-1">{title}</h4>
          <p className="text-sm text-gray-400">{description}</p>
          {action && (
            <button className="mt-2 text-xs text-cyan-400 hover:text-cyan-300 font-medium transition">
              {action} →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
