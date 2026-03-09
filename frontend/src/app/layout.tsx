import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

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
    <html lang="en">
      <body className="font-sans antialiased text-slate-900 bg-[#FDFCF8]">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
