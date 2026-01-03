import React from "react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "glass" | "gradient";
  hover?: boolean;
  padding?: "none" | "sm" | "md" | "lg";
}

export default function Card({
  children,
  className = "",
  variant = "default",
  hover = false,
  padding = "md",
}: CardProps) {
  const baseStyles = "rounded-2xl transition-all";

  const variantStyles = {
    default: "bg-[#0a0f1a] border border-white/10",
    glass: "bg-white/5 backdrop-blur-xl border border-white/10",
    gradient:
      "bg-gradient-to-br from-[#0a0f1a] to-[#0f172a] border border-white/10",
  };

  const hoverStyles = hover
    ? "hover:border-cyan-500/30 hover:shadow-[0_0_30px_rgba(34,211,238,0.1)] cursor-pointer"
    : "";

  const paddingStyles = {
    none: "",
    sm: "p-4",
    md: "p-6",
    lg: "p-8",
  };

  return (
    <div
      className={`${baseStyles} ${variantStyles[variant]} ${hoverStyles} ${paddingStyles[padding]} ${className}`}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <div className={`mb-6 ${className}`}>{children}</div>;
}

export function CardTitle({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <h3 className={`text-xl font-semibold text-white ${className}`}>
      {children}
    </h3>
  );
}

export function CardDescription({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <p className={`text-sm text-gray-400 mt-1 ${className}`}>{children}</p>;
}

export function CardContent({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <div className={className}>{children}</div>;
}

export function CardFooter({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`mt-6 pt-6 border-t border-white/5 ${className}`}>
      {children}
    </div>
  );
}
