import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, icon, className = "", ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-300 mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            className={`w-full px-4 py-3 ${
              icon ? "pl-10" : ""
            } bg-white/5 border ${
              error
                ? "border-rose-500/50 focus:border-rose-500"
                : "border-white/10 focus:border-cyan-500/50"
            } rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 ${
              error ? "focus:ring-rose-500/20" : "focus:ring-cyan-500/20"
            } transition-all ${className}`}
            {...props}
          />
        </div>
        {error && (
          <p className="mt-2 text-sm text-rose-400 flex items-center gap-1">
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            {error}
          </p>
        )}
        {helperText && !error && (
          <p className="mt-2 text-sm text-gray-400">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;

// Textarea variant
interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, helperText, className = "", ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-300 mb-2">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          className={`w-full px-4 py-3 bg-white/5 border ${
            error
              ? "border-rose-500/50 focus:border-rose-500"
              : "border-white/10 focus:border-cyan-500/50"
          } rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 ${
            error ? "focus:ring-rose-500/20" : "focus:ring-cyan-500/20"
          } transition-all resize-vertical ${className}`}
          {...props}
        />
        {error && (
          <p className="mt-2 text-sm text-rose-400 flex items-center gap-1">
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            {error}
          </p>
        )}
        {helperText && !error && (
          <p className="mt-2 text-sm text-gray-400">{helperText}</p>
        )}
      </div>
    );
  }
);

Textarea.displayName = "Textarea";
