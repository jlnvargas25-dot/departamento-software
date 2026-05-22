/**
 * SupabaseAuthProvider
 * Implements the AuthProvider port using @supabase/ssr.
 *
 * A20: this file is the ONLY place that imports Supabase. The domain layer
 *      never touches Supabase directly.
 * A11: DAO pattern — adapter translates Supabase shapes to domain Result<T>.
 * A12: signInWithPassword and getUser return UNAUTHENTICATED; never expose
 *      "which field was wrong" (FR-005 anti-enumeration).
 * A14: all methods return Result<T, DomainError>; nothing throws.
 * A5:  signUp and requestMagicLink swallow duplicate/not-found errors to
 *      prevent email enumeration.
 * A21: no PII in error messages returned to callers; redaction enforced at
 *      the logger layer (pino.ts).
 * A22: service-role key only used in deleteAccount; never leaks to client.
 */

import type { SupabaseClient } from "@supabase/supabase-js";
import type { cookies } from "next/headers";

import type { AuthProvider, DeleteAccountResult, RequestMagicLinkOptions, RequestMagicLinkResult, SignInResult, SignInWithPasswordOptions, SignUpOptions, SignUpResult } from "@/domain/ports/auth-provider";
import type { User } from "@/domain/user";
import type { Result } from "@/lib/result";
import { ok, err } from "@/lib/result";
import { Errors } from "@/domain/errors";
import {
  SignUpInputSchema,
  SignInWithPasswordInputSchema,
  RequestMagicLinkInputSchema,
  safeParse,
} from "@/lib/schemas";
import { createServerClient, createServiceRoleClient } from "@/adapters/supabase/client";

// ---------------------------------------------------------------------------
// Known Supabase error substrings that map to specific domain errors
// ---------------------------------------------------------------------------

const DUPLICATE_EMAIL_PATTERNS = [
  "user already registered",
  "already been registered",
  "email address is already",
];

const AUTH_FAILURE_PATTERNS = [
  "invalid login credentials",
  "invalid credentials",
  "email not confirmed",
];

function isDuplicateEmail(msg: string): boolean {
  return DUPLICATE_EMAIL_PATTERNS.some((p) =>
    msg.toLowerCase().includes(p),
  );
}

function isAuthFailure(msg: string): boolean {
  return AUTH_FAILURE_PATTERNS.some((p) => msg.toLowerCase().includes(p));
}

// ---------------------------------------------------------------------------
// SupabaseAuthProvider
// ---------------------------------------------------------------------------

export class SupabaseAuthProvider implements AuthProvider {
  private readonly _cookieStore: Awaited<ReturnType<typeof cookies>>;

  constructor(cookieStore: Awaited<ReturnType<typeof cookies>>) {
    this._cookieStore = cookieStore;
  }

  private get client(): SupabaseClient {
    return createServerClient(this._cookieStore);
  }

  // -------------------------------------------------------------------------
  // signUp
  // A5: duplicate email returns ok (anti-enumeration).
  // A16: rate limit applied externally before this call.
  // -------------------------------------------------------------------------

  async signUp(options: SignUpOptions): Promise<Result<SignUpResult>> {
    // A14: validate input first
    const parsed = safeParse(SignUpInputSchema, options);
    if (!parsed.ok) return parsed;

    const { email, password } = parsed.value;

    const { data, error } = await this.client.auth.signUp({ email, password });

    if (error) {
      // A5: swallow duplicate-email errors — return success to avoid enumeration
      if (isDuplicateEmail(error.message)) {
        return ok({ requiresEmailConfirmation: true });
      }
      // Other errors: INTERNAL (never leak Supabase message — A21)
      return err(Errors.internal());
    }

    // session is null when email confirmation is required
    const requiresEmailConfirmation = data.session === null;
    return ok({ requiresEmailConfirmation });
  }

  // -------------------------------------------------------------------------
  // signInWithPassword
  // A12 + FR-005: wrong email and wrong password both return UNAUTHENTICATED
  //               with the same generic message (anti-enumeration).
  // -------------------------------------------------------------------------

  async signInWithPassword(
    options: SignInWithPasswordOptions,
  ): Promise<Result<SignInResult>> {
    const parsed = safeParse(SignInWithPasswordInputSchema, options);
    if (!parsed.ok) return parsed;

    const { email, password } = parsed.value;

    const { data, error } = await this.client.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      if (isAuthFailure(error.message) || error.status === 400 || error.status === 401) {
        // Generic message — no field disclosure (FR-005)
        return err(Errors.unauthenticated("Invalid credentials."));
      }
      return err(Errors.internal());
    }

    if (!data.user) {
      return err(Errors.unauthenticated("Invalid credentials."));
    }

    return ok({ userId: data.user.id });
  }

  // -------------------------------------------------------------------------
  // requestMagicLink
  // A5: always returns sent:true — even if email not found (anti-enumeration).
  // -------------------------------------------------------------------------

  async requestMagicLink(
    options: RequestMagicLinkOptions,
  ): Promise<Result<RequestMagicLinkResult>> {
    const parsed = safeParse(RequestMagicLinkInputSchema, options);
    if (!parsed.ok) return parsed;

    const { email } = parsed.value;

    // Fire-and-forget — we don't surface the Supabase error to the caller
    await this.client.auth.signInWithOtp({ email, options: { shouldCreateUser: false } });

    // Always true — anti-enumeration (A5)
    return ok({ sent: true });
  }

  // -------------------------------------------------------------------------
  // signOut
  // Best-effort: always clears cookies. Returns ok even if Supabase fails.
  // -------------------------------------------------------------------------

  async signOut(): Promise<Result<null>> {
    // Best-effort — ignore error (session may already be gone)
    await this.client.auth.signOut();
    return ok(null);
  }

  // -------------------------------------------------------------------------
  // deleteAccount
  // A22: uses service-role client for admin.deleteUser — server only.
  // A24: cascades delete on user → todos via FK ON DELETE CASCADE.
  // -------------------------------------------------------------------------

  async deleteAccount(): Promise<Result<DeleteAccountResult>> {
    // Step 1: resolve current user (A12)
    const userResult = await this.getUser();
    if (!userResult.ok) return userResult;

    const userId = userResult.value.id;

    // Step 2: count active todos for confirmation response
    const serviceClient = createServiceRoleClient();
    const { count: deletedTodos } = await serviceClient
      .from("todos")
      .select("id", { count: "exact", head: true })
      .eq("user_id", userId);

    // Step 3: delete user (cascades todos via FK)
    const { error } = await serviceClient.auth.admin.deleteUser(userId);
    if (error) {
      return err(Errors.internal());
    }

    return ok({ deletedTodos: deletedTodos ?? 0 });
  }

  // -------------------------------------------------------------------------
  // getUser
  // A12: returns UNAUTHENTICATED if session absent or expired.
  // Used as the zero-trust gate in every server action.
  // -------------------------------------------------------------------------

  async getUser(): Promise<Result<User>> {
    const { data, error } = await this.client.auth.getUser();

    if (error || !data.user) {
      return err(Errors.unauthenticated());
    }

    const user: User = {
      id: data.user.id,
      email: data.user.email ?? "",
      // Supabase returns created_at as ISO string; domain type is Date (A11 DTO coercion)
      createdAt: new Date(data.user.created_at),
    };

    return ok(user);
  }
}
