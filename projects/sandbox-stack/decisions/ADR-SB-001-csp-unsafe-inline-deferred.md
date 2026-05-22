# ADR-SB-001: CSP style-src 'unsafe-inline' Deferred to Pre-production
**Status**: ACCEPTED v1 (sandbox-stack)
**Date**: 2026-05-21
**Scope**: sandbox-stack only — Framework-level review pending

## Context
`next.config.ts` sets `style-src 'self' 'unsafe-inline'` in the Content-Security-Policy header for all environments, including production. Tailwind CSS v3 with `@apply` directives and Next.js inline critical styles both inject inline `<style>` blocks that the browser would block under a strict CSP. Removing `'unsafe-inline'` requires either per-request nonce injection via Next.js middleware + CSP header rewrite, or hash-based allowlisting of every inline style block — both are non-trivial changes tracked in `docs/SECURITY.md § Pre-production Risks`.

## Decision
Keep `'unsafe-inline'` in `style-src` for the v1 sandbox. The risk surface is limited to CSS injection (no script execution), the application has no user-controlled style input, and Tailwind's CSS is compiled at build time (no runtime injection from external sources). This is an acceptable sandbox trade-off. Before public launch, resolve via nonce injection or CSP hash allowlisting and remove this ADR's exception.

## Consequences
Positive: unblocks v1 delivery without refactoring the entire styling pipeline. Negative: browsers cannot enforce style-source integrity in production; a XSS that reaches a `<style>` tag could inject visual phishing. Revisit trigger: any addition of user-controlled content rendered inside `<style>`, or before marking the project production-ready.
