# Observability Specification

## Purpose

Defines structured logging, PII redaction, server-action timing, and error categorization for the todo management application. The system SHALL use `pino` as the sole logging library. Every log line MUST be structured JSON. PII fields MUST be redacted before any log line reaches a transport. (A21, A24, Principio I — deterministic verification)

---

## Requirements

### Requirement: Structured JSON Logging

The application MUST emit all log output as structured JSON via `pino`. Human-readable pretty-print MUST NOT appear in production; it MAY be enabled in local development via `pino-pretty`. (A21)

| Field | Rule |
|-------|------|
| `level` | MUST use pino standard levels: `trace`, `debug`, `info`, `warn`, `error`, `fatal` |
| `time` | MUST be Unix epoch milliseconds (pino default) |
| `msg` | MUST be a static string — MUST NOT embed dynamic user data in the message string |
| `context` | Dynamic data MUST go in a structured `context` object, never interpolated into `msg` |
| `service` | MUST be `"todo-app"` on every log line (set via pino `base` option) |

#### Scenario: Info log on successful server action

- GIVEN a server action completes successfully
- WHEN the logger emits the result
- THEN the log line is valid JSON with fields `{ level: "info", msg: "action.success", context: { action, durationMs, userId: "<REDACTED>" } }`
- AND the raw email address MUST NOT appear anywhere in the log line

#### Scenario: Warn log on validation failure

- GIVEN a server action receives invalid input
- WHEN the zod schema rejects the payload
- THEN the logger emits `{ level: "warn", msg: "action.validation_failed", context: { action, field, code } }`
- AND no user-supplied input values are echoed into the log (only field names and error codes)

#### Scenario: Error log on infra failure

- GIVEN a Supabase call throws an unexpected error
- WHEN the server action catches it
- THEN the logger emits `{ level: "error", msg: "action.infra_error", context: { action, errorCode, durationMs } }`
- AND no stack trace containing user data is emitted in production (stack MAY be included in `development` only)

#### Scenario: Pretty-print in local dev

- GIVEN `NODE_ENV=development`
- WHEN the logger is initialized
- THEN `pino-pretty` transport MAY be used for human-readable output
- AND the same redaction rules MUST apply (redaction is not optional in dev)

---

### Requirement: PII Redaction

Email addresses and any other PII MUST be redacted in all log output before reaching any transport (file, stdout, external sink). Redaction MUST be applied at the pino serializer layer — not post-hoc string replacement. (A21, A24)

| PII Field | Redaction Rule |
|-----------|---------------|
| `email` | MUST be replaced with `"<REDACTED>"` at the pino serializer level |
| `userId` | SHOULD be replaced with `"<REDACTED>"` in log output (internal correlation uses opaque IDs) |
| Request bodies containing user input | MUST NOT be logged wholesale; only field names and validation codes are permitted |

#### Scenario: Email present in log context

- GIVEN a log call includes `context.email = "user@example.com"`
- WHEN pino serializes the log line
- THEN the output JSON contains `"email": "<REDACTED>"`
- AND the string `"user@example.com"` MUST NOT appear anywhere in the serialized output

#### Scenario: Deterministic CI verification of PII redaction

- GIVEN a log fixture is run through the pino logger in test mode
- WHEN the fixture output is captured
- THEN a deterministic grep `rg "email" --include="*.log"` on the fixture output returns NO matches for raw email addresses
- AND this check MUST be a CI gate (boolean: pass = no raw PII found)

#### Scenario: Nested PII in deep object

- GIVEN a log call includes a nested object with `data.user.email = "x@example.com"`
- WHEN pino serializes using the redaction paths config (`["context.email", "context.user.email", "*.email"]`)
- THEN all matching paths are redacted
- AND the raw email MUST NOT appear in output

#### Scenario: No PII in message string (enforcement)

- GIVEN a developer writes `logger.info(\`User \${email} logged in\`)`
- WHEN a linting rule or code review catches interpolated PII in `msg`
- THEN the pattern is flagged as a violation
- AND the correct pattern is `logger.info({ context: { email } }, "user.login")` with redaction handling the rest

---

### Requirement: Server-Action Timing Metrics

Every server action MUST log its execution duration in milliseconds. This enables performance regression detection without a full tracing infrastructure (OpenTelemetry deferred to v2). (A21)

#### Scenario: Duration logged on success

- GIVEN a server action completes without throwing
- WHEN the result is returned
- THEN a log line includes `{ context: { durationMs: <number> } }`
- AND `durationMs` MUST be a non-negative integer

#### Scenario: Duration logged on handled failure

- GIVEN a server action catches a known error and returns `Result<never, E>`
- WHEN the result is returned
- THEN `durationMs` is still included in the log
- AND the error category is included: `{ context: { durationMs, errorCategory: "auth" | "authz" | "domain" | "infra" } }`

#### Scenario: Vercel Analytics integration

- GIVEN the app is deployed on Vercel
- WHEN a server action completes
- THEN Vercel Analytics MAY capture the route-level timing independently (no additional code required)
- AND pino timing MUST still be present as the authoritative application-level signal

---

### Requirement: Error Categorization

All errors returned from server actions MUST be categorized into one of four categories. This categorization MUST appear in every error log. (A14, A21)

| Category | Meaning | Examples |
|----------|---------|---------|
| `auth` | Authentication failure | Missing session, expired token, invalid JWT |
| `authz` | Authorization failure | Ownership check failed, cross-tenant attempt |
| `domain` | Business rule violation | Empty title, validation error, idempotency conflict |
| `infra` | Infrastructure/external failure | Supabase unreachable, DB constraint violation, rate-limit backend down |

#### Scenario: Auth error categorized correctly

- GIVEN `getServerSession()` returns null
- WHEN the server action logs the early return
- THEN log includes `{ errorCategory: "auth", code: "UNAUTHENTICATED" }`

#### Scenario: Authz error categorized correctly

- GIVEN an ownership check finds 0 rows updated
- WHEN the server action logs the NOT_FOUND result
- THEN log includes `{ errorCategory: "authz", code: "NOT_FOUND" }`

#### Scenario: Domain error categorized correctly

- GIVEN zod validation rejects a payload
- WHEN the server action logs the failure
- THEN log includes `{ errorCategory: "domain", code: "VALIDATION_ERROR", field: "<field_name>" }`

#### Scenario: Infra error categorized correctly

- GIVEN Supabase returns a non-Postgres error (e.g. network timeout)
- WHEN the server action catches the exception
- THEN log includes `{ errorCategory: "infra", code: "DB_ERROR" }`
- AND the raw Supabase error message MUST be logged at `debug` level only (not `error` — to avoid leaking infra details in production logs shipped to external sinks)

---

### Requirement: Hexagonal Boundary — Logger as Port (A20)

The `pino` logger instance MUST be a singleton initialized in `src/lib/logger.ts` and injected where needed. Domain objects in `src/domain/` MUST NOT import `pino` or `src/lib/logger.ts` directly. (A20, A4 — acyclicity)

#### Scenario: Domain layer emits no logs directly

- GIVEN domain entities and value objects in `src/domain/`
- WHEN a static analysis check runs `rg "pino|logger" src/domain/`
- THEN zero matches are found
- AND this check MUST be a CI gate (deterministic — Principio I)

#### Scenario: Server actions receive logger via dependency injection or module import

- GIVEN a server action needs to log
- WHEN it imports `src/lib/logger.ts`
- THEN the import is permitted (adapter/app layer — outside domain boundary)
- AND the adapter MUST NOT pass raw log objects into domain functions

---

## Invariants

1. **PII-free transports**: No log line containing a raw email address or userId SHALL reach any transport (stdout, file, external sink). Redaction is applied at pino serializer level — not per-call. (A21, A24)
2. **Structured-only**: `console.log`, `console.error`, and unstructured string logs MUST NOT appear in production code. An eslint rule SHOULD flag `console.*` usage outside `src/lib/logger.ts`. (A21)
3. **Duration on every action**: Every server action boundary MUST emit a timing log. Missing `durationMs` is a spec violation. (A21)
4. **Error category always present**: Every `Result<never, E>` return MUST be accompanied by a log line with `errorCategory` set. (A14, A21)
5. **Domain isolation**: `src/domain/` MUST NOT import any logging library. Logger flows inward only from adapter/app layer. (A20)

---

## Multi-Tenant Context in Logs (A5)

Log lines that include user context MUST use the authenticated `userId` (opaque UUID) as a correlation ID, never the email. This ensures log aggregation tools can correlate per-user without storing PII in the log index.

- `userId` in logs: SHOULD be present for correlation; MUST be redacted in log output (stored only in Supabase Auth, not in log transports).
- Cross-tenant incidents: If an authz violation is logged (`ADV-T2`, `ADV-T3` scenarios), the log MUST record `{ errorCategory: "authz", requestedId: "<id>", authenticatedUserId: "<REDACTED>" }` — enough for incident forensics, no PII disclosed.

---

## Adversarial Scenarios (A15)

| # | Attack / Bug | Expected System Behavior |
|---|-------------|--------------------------|
| ADV-O1 | Developer accidentally logs `{ user: { email: "x@example.com" } }` | Pino redaction path `*.email` catches and redacts before output; CI fixture test confirms no raw email in log |
| ADV-O2 | External log sink (e.g. Datadog) receives log stream — attacker queries logs for PII | No raw PII present — redaction at source means the sink never receives it |
| ADV-O3 | Server action throws unhandled exception (missing try/catch) | Global Next.js error boundary catches; logs `{ level: "fatal", msg: "action.unhandled_exception", errorCategory: "infra" }`; MUST NOT expose stack trace in HTTP response |
| ADV-O4 | `pino` redaction config accidentally omits a PII path (e.g. new field added) | CI gate (`rg` fixture test) catches the raw PII in log output and fails the build deterministically |
| ADV-O5 | `console.log(user)` left in production code | eslint rule flags `console.*` outside `src/lib/logger.ts`; CI lint step fails before merge |

These scenarios MUST be encoded as automated tests or CI gates BEFORE the observability layer is implemented. (A15, Principio I — Python/deterministic-code verifies)
