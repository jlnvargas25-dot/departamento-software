# ADR-SB-002: console.log(JSON.stringify) as Structured Logger in Deno Edge Function
**Status**: ACCEPTED v1 (sandbox-stack)
**Date**: 2026-05-21
**Scope**: sandbox-stack only — Framework-level review pending

## Context
`supabase/functions/purge-expired-todos/index.ts` runs in the Supabase Edge runtime (Deno), which has no Node.js module support. Pino and other Node-based structured loggers cannot be imported. A21 requires structured observability on every outcome. The function uses `console.log(JSON.stringify({ level, msg, context }))` as its log transport, which Supabase's Edge runtime forwards to its log drain as newline-delimited JSON — the same structured contract that Pino satisfies in the Next.js layer.

## Decision
Accept `console.log(JSON.stringify(...))` as the A21-compliant structured log transport for Deno Edge Functions. This is the idiomatic pattern for Deno/Supabase Edge (analogous to how AWS Lambda treats stdout as its log transport). The JSON envelope with explicit `level`, `msg`, and `context` fields satisfies the structured-log contract. A Deno-native logger (e.g. `std/log` with JSON handler) is a drop-in replacement when it stabilises; migrate in a follow-up PR.

## Consequences
Positive: zero dependencies, works identically in local and deployed Edge runtimes, log drain captures structured JSON automatically. Negative: no log-level filtering at the logger layer (filtering happens at the drain); slightly verbose compared to a proper logger API. Revisit trigger: if a stable Deno-native JSON logger ships in `@std/log`, or if the project adds more Edge Functions that need consistent log config.
