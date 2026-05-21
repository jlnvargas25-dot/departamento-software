# Auth Session Specification

## Purpose

Defines the authentication lifecycle for the personal todo application: sign-up, sign-in (email/password and magic link), session extraction, sign-out, and anonymous redirect. Every authenticated surface MUST verify the server-side session before touching any user data. (A12 Zero Trust, A22 Secrets)

---

## Requirements

### Requirement: User Registration

A new user MUST be able to create an account with a unique email address and a password that meets minimum strength criteria. The system SHALL reject duplicate emails. (A12)

| Field | Rule |
|-------|------|
| email | MUST be a valid RFC-5322 address; MUST be unique in Supabase Auth |
| password | MUST be >= 8 characters; strength check delegated to Supabase Auth defaults |

#### Scenario: Successful registration

- GIVEN a visitor supplies a valid email and a password of >= 8 characters
- WHEN the sign-up server action is invoked
- THEN Supabase Auth creates the user record
- AND the system returns `Result<{ userId }, never>`
- AND the user is redirected to `/todos`

#### Scenario: Duplicate email registration

- GIVEN an email address already exists in Supabase Auth
- WHEN sign-up is attempted with that email
- THEN the server action returns `Result<never, { code: "EMAIL_TAKEN" }>`
- AND no new user record is created
- AND the UI surfaces a non-enumerating error message ("check your email" — MUST NOT confirm whether the address exists)

#### Scenario: Invalid email format

- GIVEN a visitor submits a malformed email (e.g. `user@`, `@domain.com`, empty string)
- WHEN the zod schema validates the input
- THEN validation fails before the Supabase call
- AND the server action returns `Result<never, { code: "VALIDATION_ERROR", field: "email" }>`

#### Scenario: Password too short

- GIVEN a visitor submits a password shorter than 8 characters
- WHEN the zod schema validates the input
- THEN validation fails before the Supabase call
- AND the server action returns `Result<never, { code: "VALIDATION_ERROR", field: "password" }>`

---

### Requirement: Email/Password Sign-In

A registered user MUST be able to sign in with their email and password. A valid session cookie MUST be set on success. (A12 ZT-3)

#### Scenario: Successful sign-in

- GIVEN a registered user provides the correct email and password
- WHEN the sign-in server action is invoked
- THEN Supabase Auth issues a JWT access token and a refresh token
- AND the server action persists the session via `@supabase/ssr` cookie helpers (httpOnly, secure, SameSite=Lax)
- AND the user is redirected to `/todos`

#### Scenario: Wrong password

- GIVEN a registered user provides an incorrect password
- WHEN sign-in is attempted
- THEN the server action returns `Result<never, { code: "INVALID_CREDENTIALS" }>`
- AND the response MUST NOT distinguish "wrong password" from "email not found" (non-enumerating)

#### Scenario: Non-existent email

- GIVEN an email address not registered in Supabase Auth
- WHEN sign-in is attempted
- THEN the server action returns `Result<never, { code: "INVALID_CREDENTIALS" }>`
- AND behavior is indistinguishable from "wrong password" (same error code, same latency — prevent timing enumeration)

#### Scenario: Empty credentials

- GIVEN either email or password field is empty or whitespace-only
- WHEN the zod schema validates
- THEN validation fails before the Supabase call
- AND the server action returns `Result<never, { code: "VALIDATION_ERROR" }>`

---

### Requirement: Magic Link Sign-In

A visitor MUST be able to request a one-time magic link sent to their email. The link MUST expire and MUST be single-use. (A12)

#### Scenario: Magic link requested

- GIVEN a visitor enters a valid email address
- WHEN the magic-link server action is invoked
- THEN Supabase Auth sends a one-time link to that address
- AND the server action returns `Result<{ sent: true }, never>` regardless of whether the email exists (no enumeration)

#### Scenario: Magic link consumed — session established

- GIVEN the user clicks the valid, unexpired magic link
- WHEN Supabase Auth exchanges the token
- THEN a session cookie is set (httpOnly, secure, SameSite=Lax)
- AND the user is redirected to `/todos`

#### Scenario: Expired or already-used magic link

- GIVEN the user clicks an expired or previously-consumed link
- WHEN Supabase Auth rejects the token
- THEN the user is redirected to `/login?error=link_expired`
- AND no session is created

#### Scenario: SMTP rate limit hit (staging only — Assumption #1)

- GIVEN the Supabase project uses default SMTP (4 magic links/hr) and the limit is exhausted
- WHEN a magic link is requested
- THEN the server action returns `Result<never, { code: "RATE_LIMITED" }>`
- AND a user-visible message prompts to wait or use password sign-in
- NOTE: production MUST use custom SMTP (Resend or SES) — this scenario MUST NOT occur in production

---

### Requirement: Server-Side Session Extraction

Every server action that accesses user data MUST call `getServerSession()` at the top of the function body before any data operation. (A12 ZT-3, A25)

#### Scenario: Valid session present

- GIVEN a request carries a valid, non-expired session cookie
- WHEN any data-access server action is invoked
- THEN `getServerSession()` returns `{ userId: string }`
- AND execution continues to the data layer

#### Scenario: Missing or expired session

- GIVEN no session cookie is present, or the cookie is expired/invalid
- WHEN any data-access server action is invoked
- THEN `getServerSession()` returns `null`
- AND the server action returns `Result<never, { code: "UNAUTHENTICATED" }>`
- AND the client is redirected to `/login`
- AND NO data operation is executed

#### Scenario: Tampered session token

- GIVEN a request carries a syntactically valid but cryptographically forged JWT
- WHEN Supabase Auth verifies the token
- THEN verification fails
- AND the server action treats the request identically to "missing session" (ZT-3: fail-closed)

---

### Requirement: Sign-Out

An authenticated user MUST be able to terminate their session. All session tokens MUST be invalidated on sign-out. (A12)

#### Scenario: Successful sign-out

- GIVEN an authenticated user invokes sign-out
- WHEN the sign-out server action calls `supabase.auth.signOut()`
- THEN Supabase Auth revokes the refresh token
- AND the session cookie is cleared (Max-Age=0)
- AND the user is redirected to `/login`

#### Scenario: Sign-out with already-invalid session

- GIVEN the user's session has already expired or been revoked
- WHEN sign-out is invoked
- THEN the server action SHOULD complete without error (idempotent — A8)
- AND the cookie is cleared regardless
- AND the user is redirected to `/login`

---

### Requirement: Anonymous Access Blocking

Unauthenticated requests to any authenticated route MUST be redirected to `/login`. The redirect MUST happen at middleware layer before any server action executes. (A12 ZT-1, A25)

#### Scenario: Unauthenticated GET to protected route

- GIVEN no session cookie is present
- WHEN a request is made to `/todos` or any route under `/(app)/`
- THEN Next.js middleware intercepts the request
- AND responds with HTTP 302 redirect to `/login`
- AND no server action or data query is executed

#### Scenario: Direct DB access via anon key — zero rows

- GIVEN an attacker makes a direct Supabase query using the `anon` key without a JWT
- WHEN the query targets the `todos` table
- THEN RLS policy returns 0 rows (not an error — fail-silent per Postgres RLS)
- AND no user data is disclosed (A5 + A12)

---

### Requirement: Rate Limiting on Auth Endpoints (A16)

Auth server actions (sign-in, sign-up, magic-link) MUST be rate-limited to prevent brute-force and enumeration attacks. (A16, Assumption #2)

#### Scenario: Rate limit not exceeded

- GIVEN a client has made fewer than the configured threshold of auth attempts in the window
- WHEN an auth action is invoked
- THEN the action proceeds normally

#### Scenario: Rate limit exceeded

- GIVEN a client has exceeded the threshold (Upstash Redis counter — Assumption #2)
- WHEN an auth action is invoked
- THEN the server action returns `Result<never, { code: "RATE_LIMITED" }>`
- AND responds HTTP 429 with `Retry-After` header
- AND the attempt is NOT forwarded to Supabase Auth

---

## Invariants

1. **Session-first**: No server action touching user data SHALL execute before `getServerSession()` succeeds. (A12 ZT-3)
2. **Non-enumerating errors**: Sign-in and sign-up MUST NOT reveal whether an email exists in the system.
3. **httpOnly cookies only**: Session tokens MUST NOT be accessible via `document.cookie` or JavaScript. (A22)
4. **`service_role` key never on client**: `SUPABASE_SERVICE_ROLE_KEY` MUST NOT appear in client-bundle code or client components. (A22)
5. **Fail-closed**: Any auth verification failure MUST block the request. The default action is DENY. (A12 ZT-1)

---

## Multi-Tenant Isolation Block (A5)

Auth is scale=1 (one user = one tenant), but the isolation invariant MUST hold identically to a multi-tenant scenario:

- RLS policy on `todos` references `auth.uid()` — the authenticated user's JWT sub claim.
- Server actions extract `userId` from the verified session and pass it explicitly to the repository; they MUST NOT trust client-supplied user IDs.
- `anon` role has SELECT, INSERT, UPDATE, DELETE revoked on `todos` via RLS.
- No cross-user query path exists — the ownership predicate is `user_id = auth.uid()`, enforced independently at app layer AND DB layer (defense in depth).

---

## Adversarial Scenarios (A15)

| # | Attack | Expected System Behavior |
|---|--------|--------------------------|
| ADV-A1 | Attacker submits 100 sign-in attempts in 60s | Rate limiter returns 429 after threshold; Supabase Auth never receives the overflow requests |
| ADV-A2 | Attacker sends forged JWT with valid structure but wrong signature | `getServerSession()` returns null; request blocked at ZT-3 gate |
| ADV-A3 | Attacker replays an expired access token (but valid refresh token revoked) | Supabase Auth rejects; session MUST NOT be silently refreshed from a revoked refresh token |
| ADV-A4 | Attacker injects `user_id` in the request body to impersonate another user | Server action ignores client-supplied `user_id`; ONLY `getServerSession().userId` is used |
| ADV-A5 | `service_role` key exposed in client bundle | `env.ts` validation fails at boot; eslint rule flags `process.env.SUPABASE_SERVICE_ROLE_KEY` in client paths |
| ADV-A6 | Magic link forwarded/stolen and replayed | Supabase Auth OTP is single-use; second use returns token-invalid error |

These scenarios MUST be written as automated tests BEFORE the corresponding feature code is implemented. (A15 — adversarial-first)
