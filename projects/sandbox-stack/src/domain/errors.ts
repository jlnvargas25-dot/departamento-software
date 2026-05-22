/**
 * Tagged domain error codes (A14 explicit failure).
 * Used in Result<T, DomainError> discriminated unions.
 * Every server action returns one of these — never throws (A14).
 */

export type ErrorCode =
  | "UNAUTHENTICATED" // A12: session absent or expired
  | "FORBIDDEN" // A5: cross-tenant attempt
  | "NOT_FOUND" // row missing or hard-deleted
  | "STALE_VERSION" // A13: optimistic concurrency conflict
  | "INVALID_INPUT" // zod validation failed
  | "RATE_LIMITED" // A16: too many auth attempts
  | "INTERNAL"; // Supabase/Vercel transient; always logged (A14)

export interface DomainError {
  readonly code: ErrorCode;
  readonly message: string;
}

// -------------------------------------------------------
// Constructors — typed factories for each error case
// -------------------------------------------------------

export const Errors = {
  unauthenticated(message = "Session required."): DomainError {
    return { code: "UNAUTHENTICATED", message };
  },
  forbidden(message = "Access denied."): DomainError {
    return { code: "FORBIDDEN", message };
  },
  notFound(message = "Resource not found."): DomainError {
    return { code: "NOT_FOUND", message };
  },
  staleVersion(message = "This item was updated elsewhere. Refresh and try again."): DomainError {
    return { code: "STALE_VERSION", message };
  },
  invalidInput(message: string): DomainError {
    return { code: "INVALID_INPUT", message };
  },
  rateLimited(message = "Too many attempts. Please wait before trying again."): DomainError {
    return { code: "RATE_LIMITED", message };
  },
  internal(message = "An unexpected error occurred."): DomainError {
    return { code: "INTERNAL", message };
  },
} as const;
