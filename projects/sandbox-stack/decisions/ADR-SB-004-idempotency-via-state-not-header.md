# ADR-SB-004: Idempotency via State Guard, Not Idempotency-Key Header
**Status**: ACCEPTED v1 (sandbox-stack)
**Date**: 2026-05-21
**Scope**: sandbox-stack only — Framework-level review pending

## Context
`src/app/actions/todos.ts` exposes `completeTodo`, `uncompleteTodo`, and `deleteTodo` — all of which must be idempotent (A8). The standard REST pattern for distributed idempotency is an `Idempotency-Key` header with a server-side key registry (per RFC 9110). However, these actions are Next.js Server Actions invoked over an implicit POST from a single authenticated browser session; they are not callable by third parties or background jobs in v1.

## Decision
Satisfy A8 via a fetch-then-skip state guard in the repository layer: `completeTodo` skips if already completed, `uncompleteTodo` skips if already not completed, `deleteTodo` returns the existing `deleted_at` if already soft-deleted. This makes duplicate invocations from the same session naturally idempotent without a key registry or distributed lock. `Idempotency-Key` header support is explicitly deferred: if a public REST or GraphQL API surface is added (callable by third parties or background jobs), implement key-based idempotency per RFC 9110 — the state guard alone is insufficient for distributed callers.

## Consequences
Positive: zero infrastructure overhead, correct for the current single-session invocation model, no distributed lock contention. Negative: does not protect against concurrent duplicate calls from different sessions or external callers. Revisit trigger: any addition of a public API surface or background job that invokes these mutations outside of a user session.
