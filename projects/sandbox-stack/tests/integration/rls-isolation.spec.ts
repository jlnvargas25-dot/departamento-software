/**
 * Vitest integration: RLS isolation bypass attempts
 *
 * Spec: US3 FR-008 — "enforce ownership at the data layer such that a request
 * for another user's todo is denied with no data exposure, regardless of the
 * requesting interface."
 *
 * These tests use the Supabase JS client DIRECTLY (bypassing server actions)
 * to prove the RLS layer holds independently of application code.
 *
 * Requires: `supabase start` with 202605211900_initial.sql migrated.
 *
 * A5:  RLS policies block cross-tenant access
 * A12: No session = auth.uid() = null = 0 rows on SELECT
 * A25: user_id in insert must match auth.uid() or RLS rejects
 */

import { describe, it, expect, beforeAll } from "vitest";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";

// ---------------------------------------------------------------------------
// Env helpers
// ---------------------------------------------------------------------------

function requireEnv(name: string): string {
  const val = process.env[name];
  if (!val) throw new Error(`Missing required env var: ${name}`);
  return val;
}

function makeAnonClient(): SupabaseClient {
  return createClient(
    requireEnv("NEXT_PUBLIC_SUPABASE_URL"),
    requireEnv("NEXT_PUBLIC_SUPABASE_ANON_KEY"),
    { auth: { persistSession: false, autoRefreshToken: false } },
  );
}

function makeServiceClient(): SupabaseClient {
  return createClient(
    requireEnv("NEXT_PUBLIC_SUPABASE_URL"),
    requireEnv("SUPABASE_SERVICE_ROLE_KEY"),
    { auth: { persistSession: false, autoRefreshToken: false } },
  );
}

// ---------------------------------------------------------------------------
// Test user creation via service role
// ---------------------------------------------------------------------------

interface TestUser {
  id: string;
  email: string;
  client: SupabaseClient; // authenticated client for this user
}

async function createTestUser(
  serviceClient: SupabaseClient,
  email: string,
  password: string,
): Promise<TestUser> {
  const { data, error } = await serviceClient.auth.admin.createUser({
    email,
    password,
    email_confirm: true, // skip email verification for tests
  });
  if (error || !data.user) throw new Error(`Failed to create test user: ${error?.message}`);

  // Create an authenticated client for this user
  const anonClient = makeAnonClient();
  const { error: signInError } = await anonClient.auth.signInWithPassword({ email, password });
  if (signInError) throw new Error(`Failed to sign in test user: ${signInError.message}`);

  return { id: data.user.id, email, client: anonClient };
}

async function deleteTestUser(serviceClient: SupabaseClient, userId: string): Promise<void> {
  await serviceClient.auth.admin.deleteUser(userId);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

const TS = Date.now();
const USER_A_EMAIL = `rls-test-a-${TS}@example.com`;
const USER_B_EMAIL = `rls-test-b-${TS}@example.com`;
const PASSWORD = "Adv3rs@rialRLS!";

describe("RLS Isolation — US3 FR-008 (integration)", () => {
  let serviceClient: SupabaseClient;
  let userA: TestUser;
  let userB: TestUser;
  let userA_todoId: string;

  beforeAll(async () => {
    serviceClient = makeServiceClient();

    // Create two test users
    userA = await createTestUser(serviceClient, USER_A_EMAIL, PASSWORD);
    userB = await createTestUser(serviceClient, USER_B_EMAIL, PASSWORD);

    // Create a todo as User A
    const { data, error } = await userA.client.from("todos").insert({
      user_id: userA.id,
      text: "User A secret todo for RLS test",
    }).select().single();

    if (error || !data) throw new Error(`Failed to create User A todo: ${error?.message}`);
    userA_todoId = data.id;
  }, 30_000);

  // -------------------------------------------------------------------------

  it("RLS-01: Anonymous client SELECT todos → 0 rows [A5, A12]", async () => {
    const anon = makeAnonClient();
    const { data, error } = await anon.from("todos").select("*");

    expect(error).toBeNull();
    expect(data).toEqual([]);
  });

  it("RLS-02: Anonymous client INSERT todo → RLS violation [A5, A25]", async () => {
    const anon = makeAnonClient();
    const { data, error } = await anon.from("todos").insert({
      user_id: userA.id,
      text: "Anonymous insert bypass",
    });

    expect(error).not.toBeNull();
    expect(data).toBeNull();
    // Must be a policy/privilege error
    const isRlsError =
      error?.code === "42501" ||
      error?.message?.toLowerCase().includes("policy") ||
      error?.message?.toLowerCase().includes("permission") ||
      error?.message?.toLowerCase().includes("row-level security");
    expect(isRlsError, `Expected RLS error, got: ${JSON.stringify(error)}`).toBe(true);
  });

  it("RLS-03: User B SELECT todos → cannot see User A's todos [A5]", async () => {
    const { data, error } = await userB.client.from("todos").select("*");

    expect(error).toBeNull();
    // User B sees 0 rows (their own todos only, and they have none)
    const containsA = data?.some((t) => t.id === userA_todoId) ?? false;
    expect(containsA, "User B must not see User A's todo").toBe(false);
  });

  it("RLS-04: User B SELECT by A's todo id → empty [A5]", async () => {
    const { data, error } = await userB.client
      .from("todos")
      .select("*")
      .eq("id", userA_todoId);

    expect(error).toBeNull();
    expect(data).toEqual([]);
  });

  it("RLS-05: User B UPDATE A's todo → 0 rows affected [A5]", async () => {
    const { data, error } = await userB.client
      .from("todos")
      .update({ text: "User B injected text" })
      .eq("id", userA_todoId)
      .select();

    // RLS: no rows match (user_id ≠ auth.uid()) → 0 rows, no error
    const zeroRows = data !== null && data.length === 0;
    const policyError = error?.code === "42501";
    expect(
      zeroRows || policyError,
      `Expected 0 rows, got: data=${JSON.stringify(data)} error=${JSON.stringify(error)}`,
    ).toBe(true);
  });

  it("RLS-06: User B DELETE A's todo → 0 rows affected [A5]", async () => {
    const { data, error } = await userB.client
      .from("todos")
      .delete()
      .eq("id", userA_todoId)
      .select();

    const zeroRows = data !== null && data.length === 0;
    const policyError = error?.code === "42501";
    expect(
      zeroRows || policyError,
      `Expected 0 rows, got: data=${JSON.stringify(data)} error=${JSON.stringify(error)}`,
    ).toBe(true);
  });

  it("RLS-07: After all attacks, User A's todo is UNCHANGED [A5]", async () => {
    const { data, error } = await userA.client
      .from("todos")
      .select("*")
      .eq("id", userA_todoId)
      .single();

    expect(error).toBeNull();
    expect(data).not.toBeNull();
    expect(data?.text).toBe("User A secret todo for RLS test");
    expect(data?.user_id).toBe(userA.id);
  });

  it("RLS-08: User B INSERT with A's user_id → RLS violation [A25]", async () => {
    // Even if User B knows A's user_id, they cannot forge ownership
    const { data, error } = await userB.client.from("todos").insert({
      user_id: userA.id, // forged — must be rejected by RLS WITH CHECK
      text: "Ownership forgery attempt",
    });

    expect(error).not.toBeNull();
    expect(data).toBeNull();
  });

  it("RLS-09: Anonymous client SELECT todo_events → 0 rows [A5, A6]", async () => {
    const anon = makeAnonClient();
    const { data, error } = await anon.from("todo_events").select("*");

    expect(error).toBeNull();
    expect(data).toEqual([]);
  });

  it("RLS-10: User B SELECT todo_events → cannot see A's events [A5, A6]", async () => {
    const { data, error } = await userB.client
      .from("todo_events")
      .select("*")
      .eq("actor_user_id", userA.id);

    expect(error).toBeNull();
    expect(data).toEqual([]);
  });

  // Cleanup
  afterAll(async () => {
    await deleteTestUser(serviceClient, userA.id);
    await deleteTestUser(serviceClient, userB.id);
  });
});
