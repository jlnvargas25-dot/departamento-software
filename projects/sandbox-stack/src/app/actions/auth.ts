/**
 * Auth server actions + structured logging
 *
 * Exports: signUp, signInWithPassword, requestMagicLink, signOut, deleteAccount
 *
 * Every action follows the same 5-step pattern (Principio II — 3 capas):
 *   1. PREVENTIVA  — zod input validation (via adapter)
 *   2. VERIFICABLE — rate-limit check (A16)
 *   3. VERIFICABLE — zero-trust session assertion where required (A12)
 *   4. Execute     — delegate to AuthProvider adapter (A20)
 *   5. CORRECTIVA  — write auth_events row + structured log (A21)
 *
 * A12: getUser() called at every boundary that requires authentication.
 * A14: all paths return Result<T, DomainError>; nothing thrown.
 * A16: sign-up rate-limited at 10/h/IP; magic-link at 5/h/IP.
 * A21: every outcome logged via logActionResult; email redacted by pino.
 * A22: no real keys in source; env vars validated at client creation time.
 * A25: authorization model — deleteAccount asserts identity via getUser().
 */

"use server";

import { cookies, headers } from "next/headers";
import { redirect } from "next/navigation";

import type { Result } from "@/lib/result";
import { err } from "@/lib/result";
import { Errors } from "@/domain/errors";
import { checkSignUpRateLimit, checkMagicLinkRateLimit } from "@/lib/rate-limit";
import { logActionResult, logger } from "@/adapters/logging/pino";
import { createServerClient, createServiceRoleClient } from "@/adapters/supabase/client";
import { SupabaseAuthProvider } from "@/adapters/supabase/auth-provider";

import type {
  SignUpResult,
  SignInResult,
  RequestMagicLinkResult,
  DeleteAccountResult,
} from "@/domain/ports/auth-provider";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Extract best-effort client IP from request headers (A16). */
async function getClientIp(): Promise<string> {
  const hdrs = await headers();
  return hdrs.get("x-forwarded-for")?.split(",")[0]?.trim() ?? hdrs.get("x-real-ip") ?? "unknown";
}

/** Read the correlation ID injected by middleware (OBS-3). */
async function getRequestId(): Promise<string | undefined> {
  const hdrs = await headers();
  return hdrs.get("x-request-id") ?? undefined;
}

/** Build an AuthProvider instance bound to the current request's cookies. */
async function makeProvider(): Promise<SupabaseAuthProvider> {
  const cookieStore = await cookies();
  return new SupabaseAuthProvider(cookieStore);
}

/**
 * Insert a row into auth_events via service-role client.
 * Uses service-role so the insert bypasses RLS (per data-model.md).
 * actor_user_id is nullable (null on failed sign-ins where user is unresolved).
 *
 * A6: append-only; no update or delete.
 * A21: outcome never contains raw PII — only codes and 'ok'/'fail'.
 * A22: service-role client never reaches the browser.
 */
async function writeAuthEvent(params: {
  kind:
    | "signup"
    | "signin_success"
    | "signin_fail"
    | "magic_link_sent"
    | "magic_link_redeemed"
    | "signout"
    | "session_expired";
  outcome: string;
  actorUserId?: string | null;
  ipHash?: string;
}): Promise<void> {
  try {
    const serviceClient = createServiceRoleClient();
    await serviceClient.from("auth_events").insert({
      kind: params.kind,
      outcome: params.outcome,
      actor_user_id: params.actorUserId ?? null,
      ip_hash: params.ipHash ?? null,
    });
  } catch (e) {
    // Non-fatal — event write must never break the primary flow (A14)
    // G-3/G-6: structured log so infra has visibility without alarming callers
    logger.warn(
      {
        action: "writeAuthEvent",
        errorCode: "AUTH_EVENT_WRITE_FAILED",
        error: e instanceof Error ? e.message : String(e),
      },
      "writeAuthEvent: failed to insert auth_events row (non-fatal)",
    );
  }
}

/** Cheap deterministic hash for IP — avoids storing raw PII (data-model.md). */
function hashIp(ip: string): string {
  // FNV-1a 32-bit — fast, non-crypto, sufficient for abuse correlation
  let hash = 2166136261;
  for (let i = 0; i < ip.length; i++) {
    hash ^= ip.charCodeAt(i);
    hash = (hash * 16777619) >>> 0;
  }
  return hash.toString(16);
}

// ---------------------------------------------------------------------------
// signUp
// A16: 10 attempts / hour / IP
// A5: duplicate email returns ok (anti-enumeration) — enforced in adapter
// ---------------------------------------------------------------------------

export async function signUp(input: unknown): Promise<Result<SignUpResult>> {
  const start = Date.now();
  const [ip, requestId] = await Promise.all([getClientIp(), getRequestId()]);
  const ipHash = hashIp(ip);

  // A16: rate limit check BEFORE any DB call
  const rl = await checkSignUpRateLimit(ip);
  if (!rl.ok) {
    const durationMs = Date.now() - start;
    logActionResult({
      action: "signUp",
      outcome: "error",
      errorCode: "RATE_LIMITED",
      durationMs,
      requestId,
    });
    await writeAuthEvent({ kind: "signup", outcome: "rate_limited", ipHash });
    return err(Errors.rateLimited());
  }

  const provider = await makeProvider();
  const result = await provider.signUp(input as Parameters<typeof provider.signUp>[0]);

  const durationMs = Date.now() - start;

  if (!result.ok) {
    logActionResult({
      action: "signUp",
      outcome: "error",
      errorCode: result.error.code,
      durationMs,
      requestId,
    });
    await writeAuthEvent({ kind: "signup", outcome: result.error.code, ipHash });
    return result;
  }

  // A21: log success WITHOUT userId (not yet known) and WITHOUT email (A22)
  logActionResult({ action: "signUp", outcome: "success", durationMs, requestId });
  await writeAuthEvent({ kind: "signup", outcome: "ok", ipHash });

  return result;
}

// ---------------------------------------------------------------------------
// signInWithPassword
// A16: inherits rate limit from upstream or Supabase built-in
// A12: UNAUTHENTICATED returned for any credential failure (anti-enum FR-005)
// ---------------------------------------------------------------------------

export async function signInWithPassword(input: unknown): Promise<Result<SignInResult>> {
  const start = Date.now();
  const [ip, requestId] = await Promise.all([getClientIp(), getRequestId()]);
  const ipHash = hashIp(ip);

  const provider = await makeProvider();
  const result = await provider.signInWithPassword(
    input as Parameters<typeof provider.signInWithPassword>[0],
  );

  const durationMs = Date.now() - start;

  if (!result.ok) {
    logActionResult({
      action: "signInWithPassword",
      outcome: "error",
      errorCode: result.error.code,
      durationMs,
      requestId,
      // A21: NO userId on failure (user may not exist — no correlation)
    });
    await writeAuthEvent({
      kind: "signin_fail",
      outcome: result.error.code,
      ipHash,
    });
    return result;
  }

  logActionResult({
    action: "signInWithPassword",
    outcome: "success",
    userId: result.value.userId,
    durationMs,
    requestId,
  });
  await writeAuthEvent({
    kind: "signin_success",
    outcome: "ok",
    actorUserId: result.value.userId,
    ipHash,
  });

  return result;
}

// ---------------------------------------------------------------------------
// requestMagicLink
// A16: 5 attempts / hour / IP (stricter than sign-up)
// A5: always returns sent:true — enforced in adapter
// ---------------------------------------------------------------------------

export async function requestMagicLink(input: unknown): Promise<Result<RequestMagicLinkResult>> {
  const start = Date.now();
  const [ip, requestId] = await Promise.all([getClientIp(), getRequestId()]);
  const ipHash = hashIp(ip);

  // A16: stricter rate limit for magic links
  const rl = await checkMagicLinkRateLimit(ip);
  if (!rl.ok) {
    const durationMs = Date.now() - start;
    logActionResult({
      action: "requestMagicLink",
      outcome: "error",
      errorCode: "RATE_LIMITED",
      durationMs,
      requestId,
    });
    await writeAuthEvent({
      kind: "magic_link_sent",
      outcome: "rate_limited",
      ipHash,
    });
    return err(Errors.rateLimited());
  }

  const provider = await makeProvider();
  const result = await provider.requestMagicLink(
    input as Parameters<typeof provider.requestMagicLink>[0],
  );

  const durationMs = Date.now() - start;

  logActionResult({
    action: "requestMagicLink",
    outcome: result.ok ? "success" : "error",
    errorCode: result.ok ? undefined : result.error.code,
    durationMs,
    requestId,
    // A21: never log the email — even on success
  });

  if (result.ok) {
    await writeAuthEvent({ kind: "magic_link_sent", outcome: "ok", ipHash });
  }

  return result;
}

// ---------------------------------------------------------------------------
// signOut
// Best-effort: clears cookies regardless of Supabase state.
// A12: session is gone after this — middleware will block further requests.
// ---------------------------------------------------------------------------

export async function signOut(): Promise<Result<null>> {
  const start = Date.now();
  const requestId = await getRequestId();

  // Resolve user before clearing session (for audit event)
  const provider = await makeProvider();
  const userResult = await provider.getUser();
  const userId = userResult.ok ? userResult.value.id : undefined;

  const result = await provider.signOut();

  const durationMs = Date.now() - start;
  logActionResult({
    action: "signOut",
    outcome: "success", // always success (best-effort)
    userId,
    durationMs,
    requestId,
  });

  await writeAuthEvent({
    kind: "signout",
    outcome: "ok",
    actorUserId: userId ?? null,
  });

  return result;
}

// ---------------------------------------------------------------------------
// signOutAndRedirect
// Thin wrapper for use as a form action in Server Components.
// Moved from todos.ts (Phase 4 risk #4 — separation of concerns: auth actions
// belong in auth.ts, not in the todos module).
// Delegates to signOut (which logs + writes auth_events), then redirects.
// redirect() must be called OUTSIDE try/catch per Next.js convention.
// ---------------------------------------------------------------------------

export async function signOutAndRedirect(): Promise<void> {
  await signOut();
  redirect("/sign-in");
}

// ---------------------------------------------------------------------------
// deleteAccount
// A25: identity asserted via getUser() inside the adapter.
// A24: cascades delete via FK ON DELETE CASCADE.
// A22: service-role key used only inside adapter's deleteAccount.
// ---------------------------------------------------------------------------

export async function deleteAccount(): Promise<Result<DeleteAccountResult>> {
  const start = Date.now();
  const requestId = await getRequestId();

  // A12: must have a valid session to delete account
  const cookieStore = await cookies();
  const supabase = createServerClient(cookieStore);
  const {
    data: { user },
    error: sessionError,
  } = await supabase.auth.getUser();

  if (sessionError || !user) {
    return err(Errors.unauthenticated());
  }

  const provider = await makeProvider();
  const result = await provider.deleteAccount();

  const durationMs = Date.now() - start;

  if (!result.ok) {
    logActionResult({
      action: "deleteAccount",
      outcome: "error",
      errorCode: result.error.code,
      userId: user.id,
      durationMs,
      requestId,
    });
    return result;
  }

  // Write final audit event BEFORE the user row is gone
  await writeAuthEvent({
    kind: "signout",
    outcome: "account_deleted",
    actorUserId: user.id,
  });

  logActionResult({
    action: "deleteAccount",
    outcome: "success",
    userId: user.id,
    durationMs,
    requestId,
  });

  // Redirect to sign-in after deletion
  redirect("/sign-in");
}
