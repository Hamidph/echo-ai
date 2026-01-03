import React from "react";

export type BadgeVariant =
  | "success"
  | "warning"
  | "error"
  | "info"
  | "running"
  | "pending"
  | "completed"
  | "failed";

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  pulse?: boolean;
  className?: string;
}

export default function Badge({
  children,
  variant = "info",
  pulse = false,
  className = "",
}: BadgeProps) {
  const variantStyles = {
    success: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    error: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    info: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    running: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    pending: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    completed: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    failed: "bg-rose-500/10 text-rose-400 border-rose-500/20",
  };

  const pulseAnimation = pulse ? "animate-pulse" : "";

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full border ${variantStyles[variant]} ${pulseAnimation} ${className}`}
    >
      {pulse && (
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-current opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-current"></span>
        </span>
      )}
      {children}
    </span>
  );
}

// Status badge specifically for experiment statuses
export function StatusBadge({ status }: { status: string }) {
  const normalizedStatus = status.toLowerCase();

  const variantMap: Record<string, BadgeVariant> = {
    completed: "completed",
    success: "success",
    running: "running",
    pending: "pending",
    failed: "failed",
    error: "error",
  };

  const variant = variantMap[normalizedStatus] || "info";
  const shouldPulse = normalizedStatus === "running";

  return (
    <Badge variant={variant} pulse={shouldPulse}>
      {status}
    </Badge>
  );
}
