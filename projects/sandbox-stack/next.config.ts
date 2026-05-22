import type { NextConfig } from "next";

const isDev = process.env.NODE_ENV === "development";

/**
 * Build the Content-Security-Policy header value.
 * 'unsafe-eval' is required by Next.js HMR in development only.
 * Production CSP deliberately omits it (GGA security fix).
 *
 * DEFERRED RISK — style-src 'unsafe-inline':
 * Tailwind CSS v3 with @apply rules and Next.js inline critical styles both
 * require 'unsafe-inline' in style-src. Removing it requires either:
 *   (a) nonce injection via Next.js middleware + CSP header per-request, or
 *   (b) switching to hash-based allowlisting for each inline style.
 * Both approaches require non-trivial Next.js middleware changes.
 * Tracked as pre-production risk in docs/SECURITY.md § Pre-production Risks.
 * Formal exception: decisions/ADR-SB-001-csp-unsafe-inline-deferred.md
 */
function buildCsp(): string {
  const scriptSrc = isDev
    ? "script-src 'self' 'unsafe-eval' 'unsafe-inline'"
    : "script-src 'self' 'unsafe-inline'";

  return [
    "default-src 'self'",
    scriptSrc,
    "style-src 'self' 'unsafe-inline'", // ADR-SB-001: deferred exception
    "img-src 'self' data: blob:",
    "font-src 'self'",
    "connect-src 'self' https://*.supabase.co wss://*.supabase.co",
  ].join("; ");
}

const nextConfig: NextConfig = {
  // A22: ensure server-only env vars are never bundled into client
  serverExternalPackages: ["pino"],

  // Security headers
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
          {
            key: "Content-Security-Policy",
            value: buildCsp(),
          },
        ],
      },
    ];
  },
};

export default nextConfig;
