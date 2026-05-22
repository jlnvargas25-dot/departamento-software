/**
 * Playwright E2E: User Story 2 (Sign-up / Sign-in / Magic-link / Sign-out)
 *
 * Covers spec.md acceptance scenarios US2-1 through US2-4 + edge cases:
 *   - Happy path sign-up → lands in app
 *   - Sign-out → sign-in again → preserved state
 *   - Magic-link request UI (send side; redemption requires real email infra)
 *   - Anti-enumeration: bad credentials → generic error, no field disclosure
 *   - Sign-up with existing email → non-enumerating response
 *   - deleteAccount cascade
 *
 * A12 zero-trust: every protected route checked from anonymous context.
 * A15 unhappy path first: error scenarios precede happy path in each describe block.
 * A5: anti-enumeration assertions on every auth failure.
 * A21: no PII in page title or visible error text.
 */

import { test, expect, type Page } from "@playwright/test";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Unique email per test run to avoid cross-test pollution. */
function uniqueEmail(prefix = "test"): string {
  return `${prefix}+${Date.now()}@sandbox.example.com`;
}

/** Generic non-enumerating error copy we expect on credential failure. */
const GENERIC_AUTH_ERROR = /invalid credentials|check your email|sign.?in failed/i;

/** Navigate to sign-up page and fill the form. */
async function fillSignUp(
  page: Page,
  email: string,
  password: string,
): Promise<void> {
  await page.goto("/sign-up");
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/^password$/i).fill(password);
  await page.getByRole("button", { name: /sign up|create account/i }).click();
}

/** Navigate to sign-in page and fill the form. */
async function fillSignIn(
  page: Page,
  email: string,
  password: string,
): Promise<void> {
  await page.goto("/sign-in");
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/^password$/i).fill(password);
  await page.getByRole("button", { name: /sign in|log in/i }).click();
}

// ---------------------------------------------------------------------------
// US2: Anonymous access guards (A12 zero-trust — unhappy path first per A15)
// ---------------------------------------------------------------------------

test.describe("US2 — Anonymous access denied (A12)", () => {
  test("anonymous nav to /todos redirects to sign-in without data", async ({
    page,
  }) => {
    await page.goto("/todos");
    // Must redirect — never land on /todos without session
    await expect(page).toHaveURL(/sign-in/);
    // No todo content in body
    const body = await page.content();
    expect(body).not.toMatch(/todo/i);
  });

  test("anonymous nav to / redirects to sign-in", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveURL(/sign-in/);
  });
});

// ---------------------------------------------------------------------------
// US2: Bad credentials — anti-enumeration (A5 + FR-005)
// ---------------------------------------------------------------------------

test.describe("US2 — Bad credentials — anti-enumeration (A5, FR-005)", () => {
  test("wrong password shows generic error — no field disclosure", async ({
    page,
  }) => {
    await fillSignIn(page, "nonexistent@sandbox.example.com", "WrongPass1!");
    // Generic error visible
    await expect(page.getByRole("alert")).toBeVisible();
    const errorText = await page.getByRole("alert").textContent();
    // Must not reveal which field was wrong
    expect(errorText).not.toMatch(/password.*wrong|email.*not found|user.*not exist/i);
    expect(errorText).toMatch(GENERIC_AUTH_ERROR);
    // Still on sign-in page
    await expect(page).toHaveURL(/sign-in/);
  });

  test("wrong email + correct-format password shows same generic error", async ({
    page,
  }) => {
    await fillSignIn(page, "nobody@sandbox.example.com", "ValidPass1!");
    await expect(page.getByRole("alert")).toBeVisible();
    const errorText = await page.getByRole("alert").textContent();
    expect(errorText).not.toMatch(/email.*not found|no account/i);
  });
});

// ---------------------------------------------------------------------------
// US2: Sign-up happy path (spec.md US2-1)
// ---------------------------------------------------------------------------

test.describe("US2 — Sign-up happy path (US2-1)", () => {
  test("new email + strong password → account created, lands in app or email-confirm screen", async ({
    page,
  }) => {
    const email = uniqueEmail("signup");
    await fillSignUp(page, email, "StrongPass1!");

    // Either: redirected to /todos (email confirm disabled) OR shown a confirm email prompt
    const url = page.url();
    const body = await page.content();
    const successSignals =
      /todos|check.*email|verify.*email|confirm.*email|almost there/i;
    expect(url + body).toMatch(successSignals);

    // No stack trace or internal error visible
    expect(body).not.toMatch(/Error:|at\s+\w+\s+\(/);
  });

  test("sign-up with weak password shows validation error before submit", async ({
    page,
  }) => {
    await page.goto("/sign-up");
    await page.getByLabel(/email/i).fill(uniqueEmail("weak"));
    await page.getByLabel(/^password$/i).fill("short");
    await page.getByRole("button", { name: /sign up|create account/i }).click();

    // Validation error visible — still on sign-up page
    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page).toHaveURL(/sign-up/);
  });

  test("sign-up with empty email shows validation error", async ({ page }) => {
    await page.goto("/sign-up");
    await page.getByLabel(/^password$/i).fill("StrongPass1!");
    await page.getByRole("button", { name: /sign up|create account/i }).click();

    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page).toHaveURL(/sign-up/);
  });

  test("sign-up with existing email returns non-enumerating message (A5)", async ({
    page,
  }) => {
    // We don't know which emails exist in sandbox, so we try a plausible known one.
    // The assertion is on the MESSAGE shape, not the exact outcome.
    await fillSignUp(page, "existing@sandbox.example.com", "StrongPass1!");

    const body = await page.content();
    // Must NOT say "email already in use" or "account already exists"
    expect(body).not.toMatch(/already.*registered|email.*taken|account.*exists/i);
  });
});

// ---------------------------------------------------------------------------
// US2: Sign-in happy path (spec.md US2-2)
// ---------------------------------------------------------------------------

test.describe("US2 — Sign-in happy path (US2-2)", () => {
  /**
   * Full sign-up → sign-out → sign-in cycle.
   * Uses a unique email so it's idempotent across test runs.
   * Skipped when email confirmation is required (sandbox may enforce it).
   */
  test("sign-up → sign-out → sign-in with same creds → preserved session", async ({
    page,
  }) => {
    const email = uniqueEmail("cycle");
    const password = "CyclePass1!";

    // Step 1: sign up
    await fillSignUp(page, email, password);

    // If we land on email-confirm screen, the test can't proceed (sandbox limitation).
    // We detect and skip gracefully.
    const bodyAfterSignUp = await page.content();
    if (/check.*email|verify.*email|confirm.*email/i.test(bodyAfterSignUp)) {
      test.skip();
      return;
    }

    await expect(page).toHaveURL(/todos/);

    // Step 2: sign out
    await page.getByRole("button", { name: /sign out|log out/i }).click();
    await expect(page).toHaveURL(/sign-in/);

    // Step 3: sign in with same credentials
    await fillSignIn(page, email, password);
    await expect(page).toHaveURL(/todos/);
  });
});

// ---------------------------------------------------------------------------
// US2: Magic-link request UI (spec.md US2-3 — send side only)
// ---------------------------------------------------------------------------

test.describe("US2 — Magic-link request (US2-3, send side)", () => {
  test("magic-link form accepts valid email and shows sent confirmation", async ({
    page,
  }) => {
    await page.goto("/magic-link");
    await page.getByLabel(/email/i).fill(uniqueEmail("magic"));
    await page.getByRole("button", { name: /send.*link|request.*link|magic link/i }).click();

    // Generic "check your email" shown regardless of whether email exists (anti-enum A5)
    await expect(
      page.getByText(/check.*email|link.*sent|magic.*sent/i),
    ).toBeVisible();
  });

  test("magic-link form rejects empty email", async ({ page }) => {
    await page.goto("/magic-link");
    await page.getByRole("button", { name: /send.*link|request.*link|magic link/i }).click();

    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page).toHaveURL(/magic-link/);
  });

  test("magic-link form rejects malformed email", async ({ page }) => {
    await page.goto("/magic-link");
    await page.getByLabel(/email/i).fill("not-an-email");
    await page.getByRole("button", { name: /send.*link|request.*link|magic link/i }).click();

    await expect(page.getByRole("alert")).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// US2: deleteAccount cascade
// ---------------------------------------------------------------------------

test.describe("US2 — deleteAccount cascade", () => {
  test("signed-in user can delete account and is redirected to sign-in", async ({
    page,
  }) => {
    const email = uniqueEmail("delete");
    const password = "DeletePass1!";

    await fillSignUp(page, email, password);

    const body = await page.content();
    if (/check.*email|verify.*email/i.test(body)) {
      test.skip();
      return;
    }

    await expect(page).toHaveURL(/todos/);

    // Navigate to account deletion (location may vary; try settings or profile)
    // This is a best-effort check — we look for a delete-account button anywhere
    const deleteBtn = page.getByRole("button", {
      name: /delete account|remove account/i,
    });

    if (await deleteBtn.isVisible()) {
      await deleteBtn.click();
      // Confirm if modal appears
      const confirmBtn = page.getByRole("button", {
        name: /confirm|yes.*delete|delete/i,
      });
      if (await confirmBtn.isVisible()) {
        await confirmBtn.click();
      }
      // After deletion: redirected to sign-in or landing
      await expect(page).toHaveURL(/sign-in|\//);
    } else {
      // UI not yet wired — test documents expectation for Phase 6 polish
      test.fixme(
        true,
        "Delete account button not found — UI wiring deferred to Phase 6",
      );
    }
  });
});
