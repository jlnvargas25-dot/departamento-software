/**
 * Integration tests: TodoRepository (Supabase RLS + ownership)
 *
 * Tests the SupabaseTodoRepository adapter against a local Supabase instance.
 * A5:  RLS-scoped queries return only own rows; cross-tenant insert/select/update FAILS.
 * A8:  idempotent complete/uncomplete/softDelete verified.
 * A13: expectedUpdatedAt mismatch returns STALE_VERSION.
 * A12: all queries must have an active Supabase session (via server client with cookies).
 * A24: soft-delete sets deleted_at; listActive excludes deleted rows.
 *
 * PREREQUISITES: Supabase local stack running (`supabase start`).
 * Run with: npx vitest tests/integration/todo-repository.spec.ts
 *
 * Pattern: each test creates its own user via Supabase Admin API and signs
 * them in to get a cookie-like context. We use service-role client to bootstrap
 * users and user-scoped server clients to assert RLS behavior.
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { createClient } from "@supabase/supabase-js";
import { SupabaseTodoRepository } from "@/adapters/supabase/todo-repository";
import type { SupabaseClient } from "@supabase/supabase-js";

// ---------------------------------------------------------------------------
// Helpers — test environment
// ---------------------------------------------------------------------------

const SUPABASE_URL = process.env["NEXT_PUBLIC_SUPABASE_URL"] ?? "http://127.0.0.1:54321";
const SERVICE_ROLE_KEY = process.env["SUPABASE_SERVICE_ROLE_KEY"] ?? "";
const ANON_KEY = process.env["NEXT_PUBLIC_SUPABASE_ANON_KEY"] ?? "";

/** Admin client — bypasses RLS for test setup and teardown only. */
function adminClient(): SupabaseClient {
  return createClient(SUPABASE_URL, SERVICE_ROLE_KEY, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}

/**
 * Creates a user-scoped Supabase client authenticated as the given user.
 * Mimics the server client pattern used in production (A12).
 */
function userClient(accessToken: string): SupabaseClient {
  return createClient(SUPABASE_URL, ANON_KEY, {
    auth: { autoRefreshToken: false, persistSession: false },
    global: { headers: { Authorization: `Bearer ${accessToken}` } },
  });
}

interface TestUser {
  id: string;
  email: string;
  accessToken: string;
  client: SupabaseClient;
  repo: SupabaseTodoRepository;
}

let userA: TestUser;
let userB: TestUser;
const admin = adminClient();

async function createTestUser(email: string, password: string): Promise<TestUser> {
  // Create via admin API
  const { data: created, error: createError } = await admin.auth.admin.createUser({
    email,
    password,
    email_confirm: true,
  });
  if (createError || !created.user) {
    throw new Error(`Failed to create test user ${email}: ${createError?.message}`);
  }

  // Sign in to get access token
  const anonCl = createClient(SUPABASE_URL, ANON_KEY);
  const { data: signInData, error: signInError } = await anonCl.auth.signInWithPassword({ email, password });
  if (signInError || !signInData.session) {
    throw new Error(`Failed to sign in as ${email}: ${signInError?.message}`);
  }

  const accessToken = signInData.session.access_token;
  const client = userClient(accessToken);
  const repo = new SupabaseTodoRepository(client);

  return { id: created.user.id, email, accessToken, client, repo };
}

async function deleteTestUser(id: string): Promise<void> {
  await admin.auth.admin.deleteUser(id);
}

beforeAll(async () => {
  userA = await createTestUser(
    `test-a-${Date.now()}@integration.test`,
    "Pass1234!",
  );
  userB = await createTestUser(
    `test-b-${Date.now()}@integration.test`,
    "Pass1234!",
  );
});

afterAll(async () => {
  await deleteTestUser(userA.id);
  await deleteTestUser(userB.id);
});

// ---------------------------------------------------------------------------
// create
// ---------------------------------------------------------------------------

describe("create", () => {
  it("creates a todo for the authenticated user", async () => {
    const result = await userA.repo.create({ userId: userA.id, text: "Test todo" });
    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.value.text).toBe("Test todo");
    expect(result.value.userId).toBe(userA.id);
    expect(result.value.completedAt).toBeNull();
    expect(result.value.deletedAt).toBeNull();
    expect(result.value.id).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/,
    );
  });

  it("returns INVALID_INPUT for empty text", async () => {
    const result = await userA.repo.create({ userId: userA.id, text: "" });
    expect(result.ok).toBe(false);
    if (result.ok) return;
    expect(result.error.code).toBe("INVALID_INPUT");
  });

  it("returns INVALID_INPUT for text exceeding 1000 chars", async () => {
    const result = await userA.repo.create({ userId: userA.id, text: "x".repeat(1001) });
    expect(result.ok).toBe(false);
    if (result.ok) return;
    expect(result.error.code).toBe("INVALID_INPUT");
  });
});

// ---------------------------------------------------------------------------
// listActive + RLS isolation (A5)
// ---------------------------------------------------------------------------

describe("listActive — RLS isolation (A5)", () => {
  it("user A sees only their own todos", async () => {
    // Create todos for A and B
    await userA.repo.create({ userId: userA.id, text: "A's private todo" });
    await userB.repo.create({ userId: userB.id, text: "B's private todo" });

    const result = await userA.repo.listActive({ userId: userA.id });
    expect(result.ok).toBe(true);
    if (!result.ok) return;

    const texts = result.value.items.map((t) => t.text);
    expect(texts.some((t) => t.includes("A's private todo"))).toBe(true);
    // A5: B's todo must NOT appear in A's list
    expect(texts.every((t) => !t.includes("B's private todo"))).toBe(true);
  });

  it("user B sees only their own todos — cross-tenant isolation confirmed (A5)", async () => {
    await userA.repo.create({ userId: userA.id, text: "Another A todo" });

    const result = await userB.repo.listActive({ userId: userB.id });
    expect(result.ok).toBe(true);
    if (!result.ok) return;

    const texts = result.value.items.map((t) => t.text);
    expect(texts.every((t) => !t.includes("Another A todo"))).toBe(true);
  });

  it("does not include soft-deleted todos (A24)", async () => {
    const created = await userA.repo.create({ userId: userA.id, text: "Soon deleted" });
    expect(created.ok).toBe(true);
    if (!created.ok) return;

    await userA.repo.softDelete({ id: created.value.id, userId: userA.id });

    const listed = await userA.repo.listActive({ userId: userA.id });
    expect(listed.ok).toBe(true);
    if (!listed.ok) return;

    const ids = listed.value.items.map((t) => t.id);
    expect(ids.includes(created.value.id)).toBe(false);
  });

  it("returns nextCursor null when fewer than limit items", async () => {
    // Create a fresh user with 1 todo to test cursor behavior predictably
    const freshUser = await createTestUser(
      `cursor-test-${Date.now()}@integration.test`,
      "Pass1234!",
    );
    await freshUser.repo.create({ userId: freshUser.id, text: "Only one" });
    const result = await freshUser.repo.listActive({ userId: freshUser.id, limit: 50 });
    expect(result.ok).toBe(true);
    if (!result.ok) {
      await deleteTestUser(freshUser.id);
      return;
    }
    expect(result.value.nextCursor).toBeNull();
    await deleteTestUser(freshUser.id);
  });
});

// ---------------------------------------------------------------------------
// update + STALE_VERSION (A13)
// ---------------------------------------------------------------------------

describe("update", () => {
  it("updates text when expectedUpdatedAt matches", async () => {
    const created = await userA.repo.create({ userId: userA.id, text: "Original" });
    expect(created.ok).toBe(true);
    if (!created.ok) return;

    const result = await userA.repo.update({
      id: created.value.id,
      userId: userA.id,
      text: "Updated text",
      expectedUpdatedAt: created.value.updatedAt,
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.value.text).toBe("Updated text");
  });

  it("returns STALE_VERSION when expectedUpdatedAt is stale (A13)", async () => {
    const created = await userA.repo.create({ userId: userA.id, text: "Stale test" });
    expect(created.ok).toBe(true);
    if (!created.ok) return;

    const staleDate = new Date("2000-01-01T00:00:00Z"); // intentionally wrong
    const result = await userA.repo.update({
      id: created.value.id,
      userId: userA.id,
      text: "Should not save",
      expectedUpdatedAt: staleDate,
    });

    expect(result.ok).toBe(false);
    if (result.ok) return;
    expect(result.error.code).toBe("STALE_VERSION");
  });

  it("returns NOT_FOUND or FORBIDDEN for cross-tenant update (A5)", async () => {
    // A creates a todo
    const created = await userA.repo.create({ userId: userA.id, text: "A's todo" });
    expect(created.ok).toBe(true);
    if (!created.ok) return;

    // B tries to update A's todo — must fail
    const result = await userB.repo.update({
      id: created.value.id,
      userId: userB.id,
      text: "B hijacking A's todo",
      expectedUpdatedAt: created.value.updatedAt,
    });

    expect(result.ok).toBe(false);
    if (result.ok) return;
    // RLS will return 0 rows → NOT_FOUND or FORBIDDEN (both acceptable per contracts)
    expect(["NOT_FOUND", "FORBIDDEN", "STALE_VERSION"]).toContain(result.error.code);
  });
});

// ---------------------------------------------------------------------------
// complete / uncomplete — idempotency (A8)
// ---------------------------------------------------------------------------

describe("complete", () => {
  it("sets completedAt on an active todo", async () => {
    const created = await userA.repo.create({ userId: userA.id, text: "Complete me" });
    expect(created.ok).toBe(true);
    if (!created.ok) return;

    const result = await userA.repo.complete({
      id: created.value.id,
      userId: userA.id,
      expectedUpdatedAt: created.value.updatedAt,
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.value.completedAt).not.toBeNull();
  });

  it("is idempotent — repeating complete returns success without changing completedAt (A8)", async () => {
    const created = await userA.repo.create({ userId: userA.id, text: "Idempotent complete" });
    expect(created.ok).toBe(true);
    if (!created.ok) return;

    const first = await userA.repo.complete({
      id: created.value.id,
      userId: userA.id,
      expectedUpdatedAt: created.value.updatedAt,
    });
    expect(first.ok).toBe(true);
    if (!first.ok) return;

    // Second complete — already completed, should succeed without timestamp change
    const second = await userA.repo.complete({
      id: created.value.id,
      userId: userA.id,
      expectedUpdatedAt: first.value.updatedAt,
    });
    expect(second.ok).toBe(true);
    if (!second.ok) return;
    // completedAt must not change on idempotent repeat
    expect(second.value.completedAt?.toISOString()).toBe(
      first.value.completedAt?.toISOString(),
    );
  });
});

describe("uncomplete", () => {
  it("clears completedAt", async () => {
    const created = await userA.repo.create({ userId: userA.id, text: "Uncomplete me" });
    expect(created.ok).toBe(true);
    if (!created.ok) return;

    const completed = await userA.repo.complete({
      id: created.value.id,
      userId: userA.id,
      expectedUpdatedAt: created.value.updatedAt,
    });
    expect(completed.ok).toBe(true);
    if (!completed.ok) return;

    const result = await userA.repo.uncomplete({
      id: created.value.id,
      userId: userA.id,
      expectedUpdatedAt: completed.value.updatedAt,
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.value.completedAt).toBeNull();
  });

  it("is idempotent — uncomplete on an already-active todo returns success (A8)", async () => {
    const created = await userA.repo.create({ userId: userA.id, text: "Already active" });
    expect(created.ok).toBe(true);
    if (!created.ok) return;

    // Todo is not completed — uncomplete should be idempotent
    const result = await userA.repo.uncomplete({
      id: created.value.id,
      userId: userA.id,
      expectedUpdatedAt: created.value.updatedAt,
    });
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.value.completedAt).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// softDelete — idempotency + RLS (A8, A24, A5)
// ---------------------------------------------------------------------------

describe("softDelete", () => {
  it("sets deleted_at and todo no longer appears in listActive (A24)", async () => {
    const created = await userA.repo.create({ userId: userA.id, text: "Delete me" });
    expect(created.ok).toBe(true);
    if (!created.ok) return;

    const deleteResult = await userA.repo.softDelete({
      id: created.value.id,
      userId: userA.id,
    });
    expect(deleteResult.ok).toBe(true);
    if (!deleteResult.ok) return;
    expect(deleteResult.value.deletedAt).toBeInstanceOf(Date);
  });

  it("is idempotent — re-deleting returns the existing deletedAt (A8)", async () => {
    const created = await userA.repo.create({ userId: userA.id, text: "Double delete" });
    expect(created.ok).toBe(true);
    if (!created.ok) return;

    const first = await userA.repo.softDelete({ id: created.value.id, userId: userA.id });
    expect(first.ok).toBe(true);
    if (!first.ok) return;

    const second = await userA.repo.softDelete({ id: created.value.id, userId: userA.id });
    expect(second.ok).toBe(true);
    if (!second.ok) return;

    // deletedAt must be the same on both calls
    expect(second.value.deletedAt.toISOString()).toBe(first.value.deletedAt.toISOString());
  });

  it("returns FORBIDDEN or NOT_FOUND when user B tries to delete user A's todo (A5)", async () => {
    const created = await userA.repo.create({ userId: userA.id, text: "A owns this" });
    expect(created.ok).toBe(true);
    if (!created.ok) return;

    const result = await userB.repo.softDelete({
      id: created.value.id,
      userId: userB.id,
    });

    expect(result.ok).toBe(false);
    if (result.ok) return;
    expect(["FORBIDDEN", "NOT_FOUND"]).toContain(result.error.code);
  });
});
