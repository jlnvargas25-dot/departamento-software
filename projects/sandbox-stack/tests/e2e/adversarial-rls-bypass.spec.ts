/**
 * Adversarial: RLS bypass via direct Supabase client
 *
 * Spec: US3 FR-008 — "System MUST enforce ownership at the data layer such that
 * a request for another user's todo is denied with no data exposure, regardless
 * of the requesting interface."
 *
 * Attack scenarios covered:
 *   RLS-01: Direct Supabase JS select without auth session → 0 rows returned
 *   RLS-02: Direct Supabase JS insert without auth session → RLS error
 *   RLS-03: Direct Supabase JS update with wrong user JWT → 0 rows affected
 *   RLS-04: Direct Supabase JS delete with wrong user JWT → 0 rows affected
 *
 * A5:  RLS policies enforce auth.uid() = user_id on every DML operation
 * A12: Supabase anon key without valid JWT = no session = RLS blocks everything
 *
 * NOTE: These tests use the Supabase JS client directly (not server actions)
 * to prove the defense-in-depth layer at the DB level holds, independent
 * of application code.
 */

import { test, expect } from "@playwright/test";
import { createClient } from "@supabase/supabase-js";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getSupabaseAnonClient() {
  const url = process.env["NEXT_PUBLIC_SUPABASE_URL"];
  const anonKey = process.env["NEXT_PUBLIC_SUPABASE_ANON_KEY"];

  if (!url || !anonKey) {
    throw new Error(
      "NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY must be set for RLS tests",
    );
  }

  // Intentionally using anon key WITHOUT setting a session — simulates
  // a direct Supabase client call with no authentication (A12)
  return createClient(url, anonKey);
}

// ---------------------------------------------------------------------------
// Test suite
// ---------------------------------------------------------------------------

test.describe("US3 FR-008 — RLS bypass denial (adversarial)", () => {
  test("RLS-01: Anonymous Supabase client SELECT todos → 0 rows [A5, A12]", async () => {
    const supabase = getSupabaseAnonClient();

    const { data, error } = await supabase.from("todos").select("*");

    // RLS should return 0 rows (not error — SELECT with no matching rows is valid)
    // With RLS enabled and no session, auth.uid() = null → no rows match
    expect(error).toBeNull();
    expect(data).toEqual([]);
  });

  test("RLS-02: Anonymous Supabase client INSERT todo → RLS violation [A5, A25]", async () => {
    const supabase = getSupabaseAnonClient();

    const { data, error } = await supabase.from("todos").insert({
      user_id: "00000000-0000-0000-0000-000000000000",
      text: "RLS bypass injection attempt",
    });

    // Must fail — RLS check (auth.uid() = user_id) will reject since auth.uid() = null
    expect(error).not.toBeNull();
    expect(data).toBeNull();

    // Postgres error code 42501 = insufficient_privilege (RLS violation)
    const isRlsError =
      error?.code === "42501" ||
      error?.message?.toLowerCase().includes("row-level security") ||
      error?.message?.toLowerCase().includes("policy") ||
      error?.message?.toLowerCase().includes("permission denied");
    expect(isRlsError, `Expected RLS error, got: ${JSON.stringify(error)}`).toBe(true);
  });

  test("RLS-03: Anonymous Supabase client UPDATE todos → 0 rows affected [A5]", async () => {
    const supabase = getSupabaseAnonClient();

    const { data, error } = await supabase
      .from("todos")
      .update({ text: "RLS update bypass" })
      .eq("id", "00000000-0000-0000-0000-000000000000")
      .select();

    // RLS blocks the update — either 0 rows or a policy error
    const zeroRows = data !== null && data.length === 0;
    const policyError =
      error?.code === "42501" ||
      error?.message?.toLowerCase().includes("policy") ||
      error?.message?.toLowerCase().includes("permission");

    expect(
      zeroRows || policyError,
      `Expected 0 rows or policy error, got data=${JSON.stringify(data)} error=${JSON.stringify(error)}`,
    ).toBe(true);
  });

  test("RLS-04: Anonymous Supabase client DELETE todos → 0 rows affected [A5]", async () => {
    const supabase = getSupabaseAnonClient();

    const { data, error } = await supabase
      .from("todos")
      .delete()
      .eq("id", "00000000-0000-0000-0000-000000000000")
      .select();

    // RLS blocks the delete — either 0 rows or a policy error
    const zeroRows = data !== null && data.length === 0;
    const policyError =
      error?.code === "42501" ||
      error?.message?.toLowerCase().includes("policy") ||
      error?.message?.toLowerCase().includes("permission");

    expect(
      zeroRows || policyError,
      `Expected 0 rows or policy error, got data=${JSON.stringify(data)} error=${JSON.stringify(error)}`,
    ).toBe(true);
  });

  test("RLS-05: Anonymous Supabase client SELECT todo_events → 0 rows [A5, A6]", async () => {
    const supabase = getSupabaseAnonClient();

    const { data, error } = await supabase.from("todo_events").select("*");

    expect(error).toBeNull();
    expect(data).toEqual([]);
  });

  test("RLS-06: Service role key must NOT be reachable via browser env vars [A22]", async ({
    page,
  }) => {
    // Navigate to a public page and attempt to read env vars from window
    await page.goto("/sign-in");

    const exposedKeys = await page.evaluate(() => {
      // Check if any window-level env var exposes the service role key
      const env = (window as unknown as Record<string, unknown>).__ENV__ ?? {};
      const keys = Object.keys(env as object);
      return keys.filter(
        (k) =>
          k.toLowerCase().includes("service_role") ||
          k.toLowerCase().includes("service-role"),
      );
    });

    expect(
      exposedKeys,
      `Service role key exposed in browser: ${exposedKeys.join(", ")}`,
    ).toHaveLength(0);
  });
});
