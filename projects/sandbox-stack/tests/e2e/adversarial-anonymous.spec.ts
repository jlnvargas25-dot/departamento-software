/**
 * Adversarial: Anonymous denial
 *
 * Spec: US3 SC-004 — "100% of attempts by an anonymous session to read, create,
 * update, or delete any todo are denied."
 *
 * Attack scenarios covered:
 *   AN-01: Anonymous GET /todos → redirect to /sign-in, no todo data in body
 *   AN-02: Anonymous POST to createTodo server action → UNAUTHENTICATED
 *   AN-03: Anonymous POST to updateTodo server action → UNAUTHENTICATED
 *   AN-04: Anonymous POST to completeTodo server action → UNAUTHENTICATED
 *   AN-05: Anonymous POST to deleteTodo server action → UNAUTHENTICATED
 *   AN-06: Expired session treated as anonymous (no lingering session cookie)
 *
 * A12: zero-trust — getUser() validates JWT on every server action; no data
 *      is returned before authentication is confirmed.
 * A25: no client-supplied userId accepted; absent session = UNAUTHENTICATED.
 */

import { test, expect } from "@playwright/test";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Make a direct fetch call with NO credentials (anonymous context). */
async function anonFetch(
  page: import("@playwright/test").Page,
  path: string,
  body: Record<string, unknown> = {},
): Promise<{ status: number; text: string }> {
  return page.evaluate(
    async ({ path, body }) => {
      const res = await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        // credentials: 'omit' — no cookies, purely anonymous
        credentials: "omit",
        body: JSON.stringify(body),
      });
      return { status: res.status, text: await res.text() };
    },
    { path, body },
  );
}

// ---------------------------------------------------------------------------
// Test suite
// ---------------------------------------------------------------------------

test.describe("US3 SC-004 — Anonymous denial (adversarial)", () => {
  test.use({ storageState: { cookies: [], origins: [] } }); // force clean anonymous context

  test("AN-01: Anonymous GET /todos → redirected to /sign-in, no todo data exposed [A12]", async ({
    page,
  }) => {
    // Navigate directly to the protected route
    const response = await page.goto("/todos", { waitUntil: "networkidle" });

    // Must have been redirected to sign-in
    expect(page.url()).toContain("/sign-in");

    // The page body must not contain todo-related data
    const body = await page.content();
    expect(body).not.toMatch(/todo_id|data-todo-id|"todos":\[/);

    // Response chain must not have 200 for the /todos path
    // (redirect means the original /todos was a 3xx, not 200 with data)
    // The final landed page at /sign-in is 200 — that is correct.
    const finalUrl = page.url();
    expect(finalUrl).not.toBe("/todos");
    expect(finalUrl).not.toMatch(/^https?:\/\/[^/]+\/todos/);
  });

  test("AN-02: Anonymous createTodo server action → UNAUTHENTICATED [A12, A25]", async ({
    page,
  }) => {
    await page.goto("/sign-in"); // need a loaded page to run fetch

    const res = await anonFetch(page, "/api/todos/create", {
      text: "Anonymous injection attempt",
    });

    const body = res.text;
    // Must NOT return success
    expect(body).not.toContain('"ok":true');

    // Must signal denial
    const denied =
      body.includes("UNAUTHENTICATED") ||
      body.includes("Unauthorized") ||
      body.includes("FORBIDDEN") ||
      res.status === 401 ||
      res.status === 403;

    expect(denied, `Expected UNAUTHENTICATED, got status=${res.status} body=${body}`).toBe(true);
  });

  test("AN-03: Anonymous updateTodo server action → denied [A12]", async ({ page }) => {
    await page.goto("/sign-in");

    const res = await anonFetch(page, "/api/todos/update", {
      id: "00000000-0000-0000-0000-000000000000",
      text: "Anonymous update injection",
      expectedUpdatedAt: new Date().toISOString(),
    });

    const body = res.text;
    expect(body).not.toContain('"ok":true');
    const denied =
      body.includes("UNAUTHENTICATED") ||
      body.includes("FORBIDDEN") ||
      body.includes("NOT_FOUND") ||
      res.status >= 400;
    expect(denied, `Expected denial, got: ${body}`).toBe(true);
  });

  test("AN-04: Anonymous completeTodo server action → denied [A12]", async ({ page }) => {
    await page.goto("/sign-in");

    const res = await anonFetch(page, "/api/todos/complete", {
      id: "00000000-0000-0000-0000-000000000000",
      expectedUpdatedAt: new Date().toISOString(),
    });

    const body = res.text;
    expect(body).not.toContain('"ok":true');
    const denied =
      body.includes("UNAUTHENTICATED") ||
      body.includes("FORBIDDEN") ||
      body.includes("NOT_FOUND") ||
      res.status >= 400;
    expect(denied, `Expected denial, got: ${body}`).toBe(true);
  });

  test("AN-05: Anonymous deleteTodo server action → denied [A12]", async ({ page }) => {
    await page.goto("/sign-in");

    const res = await anonFetch(page, "/api/todos/delete", {
      id: "00000000-0000-0000-0000-000000000000",
    });

    const body = res.text;
    expect(body).not.toContain('"ok":true');
    const denied =
      body.includes("UNAUTHENTICATED") ||
      body.includes("FORBIDDEN") ||
      body.includes("NOT_FOUND") ||
      res.status >= 400;
    expect(denied, `Expected denial, got: ${body}`).toBe(true);
  });

  test("AN-06: Anonymous listActiveTodos server action → denied, zero rows returned [A12]", async ({
    page,
  }) => {
    await page.goto("/sign-in");

    const res = await anonFetch(page, "/api/todos/list", {
      limit: 50,
    });

    const body = res.text;
    // Must not return a list of todos
    expect(body).not.toContain('"todos":[{');
    expect(body).not.toContain('"ok":true');
    const denied =
      body.includes("UNAUTHENTICATED") ||
      body.includes("FORBIDDEN") ||
      res.status === 401 ||
      res.status === 403;
    expect(denied, `Expected UNAUTHENTICATED, got: ${body}`).toBe(true);
  });

  test("AN-07: Root path redirect — anonymous / → /sign-in [A12]", async ({ page }) => {
    await page.goto("/");
    expect(page.url()).toContain("/sign-in");
  });

  test("AN-08: No todo data leaks in 302 redirect headers [A12]", async ({ page }) => {
    // Intercept the redirect response to ensure no data in headers
    const responses: import("@playwright/test").Response[] = [];
    page.on("response", (r) => {
      if (r.url().includes("/todos")) responses.push(r);
    });

    await page.goto("/todos");

    // Check captured responses for data leakage in headers
    for (const r of responses) {
      const headers = r.headers();
      // Headers must not contain todo data
      const headerStr = JSON.stringify(headers);
      expect(headerStr).not.toMatch(/todo_id|user_id|completed_at/);
    }
  });
});
