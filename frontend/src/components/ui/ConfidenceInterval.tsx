/**
 * Confidence interval display for Monte Carlo visibility metrics.
 *
 * Uses the Wilson score interval for proportions, which handles edge cases
 * (p=0, p=1, small n) more gracefully than the normal approximation.
 */

interface CIResult {
  low: number;
  high: number;
  margin: number;
}

/**
 * Wilson score interval for a proportion p observed over n trials at 95% confidence.
 * More accurate than the normal approximation at extreme values.
 */
export function wilsonCI(p: number, n: number, z = 1.96): CIResult {
  if (n === 0) return { low: 0, high: 1, margin: 0.5 };
  const denominator = 1 + (z * z) / n;
  const centre = (p + (z * z) / (2 * n)) / denominator;
  const halfWidth = ((z / denominator) * Math.sqrt((p * (1 - p)) / n + (z * z) / (4 * n * n)));
  const low = Math.max(0, centre - halfWidth);
  const high = Math.min(1, centre + halfWidth);
  return { low, high, margin: (high - low) / 2 };
}

interface ConfidenceIntervalProps {
  /** Visibility rate as a fraction 0–1 */
  rate: number;
  /** Number of Monte Carlo iterations run */
  iterations: number;
  /** Display variant */
  variant?: "inline" | "card";
}

const pct = (v: number) => `${Math.round(v * 100)}%`;

export function ConfidenceInterval({ rate, iterations, variant = "inline" }: ConfidenceIntervalProps) {
  const ci = wilsonCI(rate, iterations);
  const reliable = iterations >= 30;

  if (variant === "card") {
    return (
      <div className="mt-3 pt-3 border-t border-stone-100">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            95% Confidence Interval
          </span>
          {reliable ? (
            <span
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold"
              title={`Statistically reliable at n=${iterations} iterations`}
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Statistically Reliable
            </span>
          ) : (
            <span
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-50 border border-amber-200 text-amber-700 text-xs font-semibold"
              title={`Run 30+ iterations for reliable statistics (current: ${iterations})`}
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Low Sample Size
            </span>
          )}
        </div>

        {/* CI bar */}
        <div className="relative h-2 bg-stone-100 rounded-full overflow-hidden mb-1">
          <div
            className="absolute h-full bg-blue-200 rounded-full"
            style={{ left: `${ci.low * 100}%`, width: `${(ci.high - ci.low) * 100}%` }}
          />
          <div
            className="absolute w-0.5 h-full bg-blue-600"
            style={{ left: `${rate * 100}%` }}
          />
        </div>

        <div className="flex justify-between text-xs text-slate-400 mt-1">
          <span>{pct(ci.low)}</span>
          <span className="text-slate-600 font-semibold">{pct(rate)} ± {pct(ci.margin)}</span>
          <span>{pct(ci.high)}</span>
        </div>
        <p className="text-xs text-slate-400 mt-2">
          Based on {iterations} Monte Carlo iterations
        </p>
      </div>
    );
  }

  // inline variant — compact, for use inside metric cards
  return (
    <div className="flex items-center gap-1.5 mt-1">
      <span className="text-sm text-slate-400 font-mono">
        ± {pct(ci.margin)}
      </span>
      {reliable ? (
        <span
          className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-md bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold"
          title={`95% CI: ${pct(ci.low)}–${pct(ci.high)}, n=${iterations}`}
        >
          <svg className="w-2.5 h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
          </svg>
          Reliable
        </span>
      ) : (
        <span
          className="px-1.5 py-0.5 rounded-md bg-amber-50 border border-amber-200 text-amber-600 text-xs font-medium"
          title={`Increase to 30+ iterations for reliable statistics (current: ${iterations})`}
        >
          n={iterations}
        </span>
      )}
    </div>
  );
}
