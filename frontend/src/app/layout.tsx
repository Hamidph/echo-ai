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
  title: "Echo AI | AI Search Analytics for Marketing Teams",
  description:
    "Track, analyze, and improve your brand visibility on ChatGPT, Perplexity, and Claude.",
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
