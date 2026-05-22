/**
 * Root layout with Vercel Analytics + Speed Insights
 *
 * Analytics: page-view tracking + Web Vitals (A21 metrics pillar).
 * No PII is sent — Vercel Analytics uses URL path only, not query params
 * or cookies. NEXT_PUBLIC_VERCEL_ANALYTICS_ID is injected automatically
 * by Vercel at build time; no manual env var needed for production deploys.
 *
 * For local dev: analytics events are collected but not sent (dev mode).
 * For preview + production: automatically active once the package is present.
 */

import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Todo App",
  description: "Personal todo management — sandbox-stack",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>): React.JSX.Element {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
        {/* A21: page-view + Web Vitals telemetry — no PII, no cookies */}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
