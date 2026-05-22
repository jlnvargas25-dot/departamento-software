/**
 * Port: AuthProvider
 * A20: interface only — no Supabase imports, no Next.js cookies.
 * A11: DAO pattern — adapter implements this in src/adapters/supabase/auth-provider.ts
 * A12: every method that requires a session accepts it explicitly (zero trust).
 */

import type { User } from "@/domain/user";
import type { Result } from "@/lib/result";

export interface SignUpOptions {
  email: string;
  password: string;
}

export interface SignUpResult {
  requiresEmailConfirmation: boolean;
}

export interface SignInWithPasswordOptions {
  email: string;
  password: string;
}

export interface SignInResult {
  userId: string;
}

export interface RequestMagicLinkOptions {
  email: string;
}

export interface RequestMagicLinkResult {
  sent: boolean; // always true to avoid enumeration (A5 anti-enum)
}

export interface DeleteAccountResult {
  deletedTodos: number;
}

/**
 * AuthProvider port.
 * All methods return Result<T, DomainError> — never throw (A14).
 * Anti-enumeration: signUp and requestMagicLink return success even on duplicate email.
 */
export interface AuthProvider {
  /** A16: rate-limited externally before calling. */
  signUp(options: SignUpOptions): Promise<Result<SignUpResult>>;

  /**
   * A12: wrong email + wrong password both return UNAUTHENTICATED (anti-enumeration FR-005).
   * A16: rate-limited externally before calling.
   */
  signInWithPassword(options: SignInWithPasswordOptions): Promise<Result<SignInResult>>;

  /** A16: rate-limited externally before calling. Returns sent:true regardless (anti-enum). */
  requestMagicLink(options: RequestMagicLinkOptions): Promise<Result<RequestMagicLinkResult>>;

  /** Best-effort. Always clears session cookies. */
  signOut(): Promise<Result<null>>;

  /** Cascades delete on user and all todos (FK ON DELETE CASCADE). */
  deleteAccount(): Promise<Result<DeleteAccountResult>>;

  /**
   * Resolves the current session user from cookies.
   * Returns UNAUTHENTICATED if no valid session (A12).
   */
  getUser(): Promise<Result<User>>;
}
