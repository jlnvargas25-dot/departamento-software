/**
 * Domain entity: User
 * A20: pure domain — zero IO, zero framework imports.
 * A22: email is PII — never log raw; adapters must redact before passing to pino.
 * A24: PII classification — email is sensitive; userId is non-sensitive UUID.
 */

export interface User {
  readonly id: string; // UUID — auth.users.id (Supabase managed)
  readonly email: string; // PII — redact in logs (A22)
  readonly createdAt: Date;
}

/**
 * Redacted representation safe for structured logging.
 * Use this whenever passing user context to pino (A21 + A22).
 */
export interface UserLogContext {
  readonly userId: string; // safe to log
  // email intentionally omitted
}

export function toLogContext(user: Pick<User, "id">): UserLogContext {
  return { userId: user.id };
}
