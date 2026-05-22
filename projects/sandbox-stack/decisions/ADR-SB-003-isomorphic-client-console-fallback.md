# ADR-SB-003: console.warn Fallback in Isomorphic Supabase Client Adapter
**Status**: ACCEPTED v1 (sandbox-stack)
**Date**: 2026-05-21
**Scope**: sandbox-stack only — Framework-level review pending

## Context
`src/adapters/supabase/client.ts` is imported by both Server Components and Server Actions. When `createServerClient()` is called from a read-only Server Component context, the `setAll` cookie callback throws because Next.js does not allow cookie writes outside of Actions or Route Handlers. The catch block must log the suppressed error for observability (A21/G-6), but importing Pino here creates a circular dependency risk and is unsafe in isomorphic adapter code that may be evaluated in a browser bundle. A `typeof window === "undefined"` guard ensures the `console.warn` only fires server-side.

## Decision
Use `console.warn` (server-side only, guarded by `typeof window === "undefined"`) for this single catch path. The event is non-fatal by design — the middleware handles session refresh for read-only contexts — so a warn-level log without full structured context is proportionate. Pino is not imported in this file to avoid isomorphic bundling issues. If the adapter is ever refactored to be server-only (e.g. via `import 'server-only'`), replace the guard with a direct Pino `logger.warn` call.

## Consequences
Positive: no circular imports, no accidental browser bundle inflation, non-fatal path stays non-fatal. Negative: this one log line is not captured in the Pino structured stream (no `action` or `durationMs` fields). Revisit trigger: if `src/adapters/supabase/client.ts` is split into server-only and browser-only modules, remove the guard and use Pino directly.
