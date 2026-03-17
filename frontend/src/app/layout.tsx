import type { Metadata } from "next";
import { Inter, Manrope } from "next/font/google"; // Modern, geometric combo
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-manrope",
});

export const metadata: Metadata = {
  title: {
    template: "%s | Echo AI",
    default: "Echo AI — AI Brand Visibility, Measured with Statistical Confidence",
  },
  description:
    "Echo AI uses Monte Carlo simulation to measure your brand's real visibility across AI responses — not a single snapshot, but statistically reliable confidence intervals. Track ChatGPT, Claude, Perplexity & more.",
  keywords: [
    "AI brand visibility",
    "LLM monitoring",
    "AI search analytics",
    "GEO tracking",
    "Monte Carlo AI visibility",
    "ChatGPT brand mentions",
    "generative engine optimization",
    "AI search ranking",
  ],
  openGraph: {
    type: "website",
    siteName: "Echo AI",
    title: "Echo AI — AI Brand Visibility, Measured with Statistical Confidence",
    description:
      "The only AI visibility tool built on Monte Carlo simulation. Get confidence intervals, not guesses.",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "Echo AI Dashboard" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Echo AI — AI Brand Visibility",
    description:
      "Monte Carlo-powered AI brand tracking. Statistically reliable. Not a single snapshot.",
    images: ["/og-image.png"],
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${manrope.variable}`}>
      <body className="font-sans antialiased text-slate-900 bg-[#FDFCF8]">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
