/**
 * Result<T, E> — explicit failure type (A14).
 * All server actions return Result<T, DomainError>.
 * Never throw across server-action boundaries.
 *
 * Usage:
 *   const r = await createTodo(input);
 *   if (!r.ok) { // r.error.code is ErrorCode }
 *   else { // r.value is T }
 */

import type { DomainError } from "@/domain/errors";

export type Ok<T> = { readonly ok: true; readonly value: T };
export type Err<E = DomainError> = { readonly ok: false; readonly error: E };
export type Result<T, E = DomainError> = Ok<T> | Err<E>;

// -------------------------------------------------------
// Constructors
// -------------------------------------------------------

export function ok<T>(value: T): Ok<T> {
  return { ok: true, value };
}

export function err<E = DomainError>(error: E): Err<E> {
  return { ok: false, error };
}

// -------------------------------------------------------
// Type guards
// -------------------------------------------------------

export function isOk<T, E>(result: Result<T, E>): result is Ok<T> {
  return result.ok === true;
}

export function isErr<T, E>(result: Result<T, E>): result is Err<E> {
  return result.ok === false;
}

// -------------------------------------------------------
// Combinators
// -------------------------------------------------------

/** Map over the success value; pass through errors. */
export function mapOk<T, U, E>(
  result: Result<T, E>,
  fn: (value: T) => U,
): Result<U, E> {
  return result.ok ? ok(fn(result.value)) : result;
}

/** Unwrap for use in server actions that need to propagate errors early. */
export function unwrapOr<T, E>(result: Result<T, E>, fallback: T): T {
  return result.ok ? result.value : fallback;
}
