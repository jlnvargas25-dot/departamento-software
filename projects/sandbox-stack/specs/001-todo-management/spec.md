# Feature Specification: Personal Todo Management with User Authentication

**Feature Branch**: `001-todo-management`

**Created**: 2026-05-21

**Status**: Draft

**Input**: User description: "Build a simple todo CRUD with user authentication using Supabase + Vercel. The app lets a signed-in user create, read, update, delete and complete their own todos. Anonymous users cannot access todos. Multi-tenant by user_id (no shared workspaces). Stack: Next.js on Vercel, Supabase Auth (email/password + magic link), Supabase Postgres with RLS, Tailwind UI minimal."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authenticated user manages their own todos (Priority: P1)

A signed-in user opens the app, sees only the todos they have created, and can add new ones, edit existing ones, mark them as completed, or remove them. Their list is fully isolated from any other user's list. The same user accessing the app from a different device after signing in sees the same list.

**Why this priority**: This is the core value proposition. Without authenticated CRUD over private todos, the product does not exist.

**Independent Test**: Sign in as user A, create three todos, sign out. Sign in as user B and verify zero todos appear. Sign in again as user A and verify the three todos appear unchanged with the same content, order, and completion state.

**Acceptance Scenarios**:

1. **Given** a signed-in user with an empty todo list, **When** they create a todo with non-empty text, **Then** the todo appears in their list with a creation timestamp and "not completed" state.
2. **Given** a signed-in user with existing todos, **When** they edit a todo's text, **Then** the change is persisted and visible after a page reload.
3. **Given** a signed-in user with a todo in "not completed" state, **When** they mark it complete, **Then** the todo is visibly distinguished and a completion timestamp is recorded.
4. **Given** a signed-in user with a todo, **When** they delete it, **Then** the todo no longer appears in the active list and counts decrease accordingly.
5. **Given** two different signed-in users A and B, **When** A creates a todo, **Then** B never sees that todo in their list under any circumstance.

---

### User Story 2 - New user signs up and signs in (Priority: P1)

A first-time visitor signs up with an email and password, completes any required verification, and lands in the application with an empty todo list ready for use. A returning visitor signs in with email and password, or alternatively requests a one-time login link via email.

**Why this priority**: Same priority as Story 1 — there is no authenticated CRUD without a working sign-up and sign-in flow.

**Independent Test**: Open the app in a clean session, complete sign-up with a previously-unused email, confirm email if required, and land in the authenticated app with an empty list. Sign out and sign in again with the same credentials and verify the list is preserved.

**Acceptance Scenarios**:

1. **Given** a clean browser session, **When** a visitor submits a sign-up form with a valid unused email and a sufficiently strong password, **Then** an account is created and the visitor is either signed in or asked to confirm email per the verification policy.
2. **Given** an existing user signed out, **When** they submit correct email and password, **Then** they are signed in and see their preserved list.
3. **Given** an existing user signed out, **When** they request a magic link to their email, **Then** clicking the link within the validity window signs them in.
4. **Given** any visitor, **When** they submit incorrect credentials, **Then** they are denied access with a clear non-disclosing error message (no enumeration of which field was wrong).

---

### User Story 3 - Anonymous user is denied access (Priority: P1)

An anonymous visitor (not signed in) is denied access to any todo data. They are either redirected to the sign-in screen or shown a clear message that requires authentication.

**Why this priority**: This is a security boundary. A leak here invalidates the entire multi-tenant model.

**Independent Test**: Without signing in, attempt to open the todos screen directly via URL. Verify redirect to sign-in. Sign in as user A, capture an API request that returns A's todos, sign out, then replay the same request from the anonymous session. Verify the request is denied with no data returned.

**Acceptance Scenarios**:

1. **Given** an anonymous session, **When** the visitor navigates directly to the todos URL, **Then** they are redirected to sign-in without exposing any todo data in the response.
2. **Given** an anonymous session, **When** any todo-related request is made (read, create, update, delete), **Then** the system denies the request and returns no todo content.
3. **Given** a signed-in session whose authentication has expired, **When** the user makes any todo-related request, **Then** the system treats the session as anonymous (deny + redirect to re-authentication).

---

### Edge Cases

- **Empty todo text on create or update**: rejected with an inline validation error; the list state remains unchanged.
- **Maximum todo text length exceeded**: rejected with a clear error indicating the cap (default 1000 characters).
- **Delete of an already-deleted todo (race)**: the second delete returns idempotent success; the user-visible state is consistent.
- **Mark complete on an already-completed todo**: idempotent — completion timestamp does not change on repeat completion.
- **List size grows large** (>= 500 todos for one user): the list remains usable; pagination or progressive loading kicks in at a documented threshold.
- **Magic link reuse**: a magic link can be redeemed at most once; reuse is denied.
- **Sign-up with an email already in use**: returns a non-enumerating error indicating "if the email is valid, you will receive instructions" (or equivalent privacy-preserving response).
- **Network failure mid-edit**: the user sees a clear error; no partial write is persisted; the previous state remains intact.
- **Two devices editing the same todo near-simultaneously**: last write wins; the losing device sees the updated state on next read with no silent loss of information beyond what was overwritten.

## Requirements *(mandatory)*

### Functional Requirements

**Authentication**:
- **FR-001**: System MUST allow visitors to create an account using an email address and a password meeting a minimum strength policy.
- **FR-002**: System MUST allow returning users to sign in using email + password.
- **FR-003**: System MUST offer an alternative passwordless sign-in via a one-time magic link sent to the user's email, valid for a bounded window and single-use.
- **FR-004**: System MUST sign the user out on explicit request and on session expiry, after which they are treated as anonymous.
- **FR-005**: System MUST NOT disclose whether a given email is registered when sign-in fails (anti-enumeration).

**Authorization and multi-tenancy**:
- **FR-006**: System MUST deny any todo operation (read, create, update, delete, complete) to an anonymous session.
- **FR-007**: System MUST restrict every authenticated user to operating ONLY on todos they own.
- **FR-008**: System MUST enforce ownership at the data layer such that a request for another user's todo is denied with no data exposure, regardless of the requesting interface.
- **FR-009**: System MUST treat ownership as the only basis for access; there are no shared workspaces, organizations, teams, or admin overrides.

**Todo lifecycle**:
- **FR-010**: Users MUST be able to create a todo with non-empty text up to a documented maximum length.
- **FR-011**: Users MUST be able to read their full list of active todos, sorted by a consistent rule (default: most recently created first).
- **FR-012**: Users MUST be able to update the text of any of their own todos.
- **FR-013**: Users MUST be able to mark a todo as completed and revert that completion. The completion timestamp MUST be recorded.
- **FR-014**: Users MUST be able to delete any of their own todos. Deletion MUST be soft (recoverable for a bounded retention window) such that audit and recovery are possible.
- **FR-015**: System MUST display, alongside each todo, its creation timestamp and (if applicable) completion timestamp.

**Quality and observability**:
- **FR-016**: System MUST log every authentication event (sign-up, sign-in success/failure, sign-out, session expiry) with enough structure to support security review without exposing secrets.
- **FR-017**: System MUST log every todo write event (create, update, complete, delete) with the acting user identifier and timestamp.
- **FR-018**: System MUST surface user-visible errors with messages that do not leak internal details (stack traces, identifiers from other users, infrastructure information).

**Data lifecycle and privacy**:
- **FR-019**: System MUST allow a user to permanently delete their account, which MUST result in the destruction of all their todos within a documented window.
- **FR-020**: System MUST classify the user's email as personal identifying information and apply retention/deletion accordingly.

### Key Entities *(include if feature involves data)*

- **User**: an authenticated principal. Owns todos. Has an email address (PII), a creation date, and an authentication state. No profile beyond what authentication requires.
- **Todo**: a user-owned item. Has text content, a creation timestamp, an optional completion timestamp, an active/deleted flag, and a strict owner reference. Never shared.
- **AuthEvent**: a structured record of an authentication-related action (success, failure, expiry, sign-out). Carries actor identifier, kind, outcome, and timestamp.
- **TodoEvent**: a structured record of a todo write (create, update, complete, delete). Carries actor identifier, todo identifier, kind, and timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new visitor can complete sign-up and create their first todo in under **90 seconds** on a standard residential connection.
- **SC-002**: A returning user signing in with magic link reaches an interactive todo list in under **30 seconds** from clicking the link.
- **SC-003**: 100% of attempts by user A to read, update, or delete a todo owned by user B are denied. Verified by automated adversarial test on every release.
- **SC-004**: 100% of attempts by an anonymous session to read, create, update, or delete any todo are denied. Verified by automated adversarial test on every release.
- **SC-005**: Median time from "create todo" tap to the new todo being visible in the user's list is under **1 second** on a standard residential connection.
- **SC-006**: A user's deleted account results in zero recoverable todos within **30 days** of the deletion request.
- **SC-007**: 95% of users successfully complete the primary task ("create your first todo") on first attempt without abandoning the sign-up flow.

## Assumptions

- **Tech stack constraint (recorded but not specified)**: Next.js on Vercel for hosting/runtime, Supabase Auth for identity, Supabase Postgres with Row-Level Security for storage, Tailwind for minimal UI. Recorded so downstream planning honors the chosen stack.
- **Password policy default**: 8+ characters with at least one number or symbol. Standard for consumer apps.
- **Magic link validity**: 1 hour, single-use. Standard for Supabase Auth.
- **Email verification before first sign-in is optional for the MVP** and left to the auth provider's default (Supabase: required by default for email/password).
- **Soft-delete retention window**: 30 days, after which deleted todos are permanently removed.
- **Pagination threshold**: 50 active todos per page; progressive loading beyond.
- **Browser-only**: web app only for v1; mobile app deferred.
- **Single language (English) UI for v1**; i18n deferred.
- **No collaboration or sharing**: explicit non-goal for v1.
- **No reminders or notifications** in v1; explicit non-goal.
- **No file attachments** to todos in v1; explicit non-goal.
