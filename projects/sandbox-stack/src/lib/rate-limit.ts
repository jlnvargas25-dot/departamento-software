/**
 * Rate limiter wrapper — Upstash Redis (A16).
 * Decision 8: 10 req/h/IP for sign-up; 5 req/h/IP for magic-link.
 * Falls back to in-memory sliding window when Upstash env vars are absent
 * (safe for local dev; never for production).
 *
 * Returns Result<void, DomainError> so callers return RATE_LIMITED (A14).
 */

import { err, ok } from "@/lib/result";
import { Errors } from "@/domain/errors";
import type { Result } from "@/lib/result";
import { requireEnv } from "@/adapters/supabase/client"; // A22: fail-fast helper

// -------------------------------------------------------
// Lazy-init Upstash client (avoids import errors when env vars absent)
// -------------------------------------------------------

type RateLimiter = {
  limit(identifier: string): Promise<{ success: boolean; reset: number }>;
};

// In-memory fallback for local dev (not production-safe)
function makeInMemoryLimiter(maxRequests: number, windowMs: number): RateLimiter {
  const store = new Map<string, { count: number; resetAt: number }>();

  return {
    async limit(identifier: string) {
      const now = Date.now();
      const entry = store.get(identifier);

      if (!entry || now > entry.resetAt) {
        store.set(identifier, { count: 1, resetAt: now + windowMs });
        return { success: true, reset: now + windowMs };
      }

      entry.count += 1;
      const success = entry.count <= maxRequests;
      return { success, reset: entry.resetAt };
    },
  };
}

function makeUpstashLimiter(maxRequests: number, windowSeconds: number): RateLimiter {
  // Dynamic import so missing env vars don't crash the module at load time
  let limiterPromise: Promise<RateLimiter> | null = null;

  return {
    async limit(identifier: string) {
      if (!limiterPromise) {
        limiterPromise = (async () => {
          const { Ratelimit } = await import("@upstash/ratelimit");
          const { Redis } = await import("@upstash/redis");

          const redis = new Redis({
            url: requireEnv("UPSTASH_REDIS_REST_URL"),
            token: requireEnv("UPSTASH_REDIS_REST_TOKEN"),
          });

          const rl = new Ratelimit({
            redis,
            limiter: Ratelimit.slidingWindow(maxRequests, `${windowSeconds}s`),
            prefix: "todo-app",
          });

          return {
            async limit(id: string) {
              const result = await rl.limit(id);
              return { success: result.success, reset: result.reset };
            },
          };
        })();
      }
      const limiter = await limiterPromise;
      return limiter.limit(identifier);
    },
  };
}

// -------------------------------------------------------
// Named limiters per Decision 8
// -------------------------------------------------------

const HOUR_MS = 60 * 60 * 1000;
const HOUR_S = 3600;

function buildLimiter(maxRequests: number): RateLimiter {
  const hasUpstash =
    process.env["UPSTASH_REDIS_REST_URL"] && process.env["UPSTASH_REDIS_REST_TOKEN"];

  if (hasUpstash) {
    return makeUpstashLimiter(maxRequests, HOUR_S);
  }

  // Local dev fallback — log warning once
  if (process.env["NODE_ENV"] !== "test") {
    // Using process.stderr to avoid circular pino dependency
    process.stderr.write(
      "[rate-limit] UPSTASH env vars not set — using in-memory fallback. NOT for production.\n",
    );
  }
  return makeInMemoryLimiter(maxRequests, HOUR_MS);
}

// Lazily constructed per endpoint
let _signUpLimiter: RateLimiter | null = null;
let _magicLinkLimiter: RateLimiter | null = null;

function getSignUpLimiter(): RateLimiter {
  _signUpLimiter ??= buildLimiter(10); // 10/h/IP
  return _signUpLimiter;
}

function getMagicLinkLimiter(): RateLimiter {
  _magicLinkLimiter ??= buildLimiter(5); // 5/h/IP
  return _magicLinkLimiter;
}

// -------------------------------------------------------
// Public API
// -------------------------------------------------------

/** Checks rate limit for the sign-up endpoint (10/h/IP). */
export async function checkSignUpRateLimit(ipIdentifier: string): Promise<Result<void>> {
  const { success } = await getSignUpLimiter().limit(`signup:${ipIdentifier}`);
  if (!success) return err(Errors.rateLimited("Too many sign-up attempts. Try again in an hour."));
  return ok(undefined);
}

/** Checks rate limit for the magic-link endpoint (5/h/IP). */
export async function checkMagicLinkRateLimit(ipIdentifier: string): Promise<Result<void>> {
  const { success } = await getMagicLinkLimiter().limit(`magic:${ipIdentifier}`);
  if (!success) return err(Errors.rateLimited("Too many magic link requests. Try again in an hour."));
  return ok(undefined);
}
