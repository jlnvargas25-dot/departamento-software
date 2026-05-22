/**
 * Vitest integration: AuthProvider adapter against local Supabase
 *
 * Tests the SupabaseAuthProvider adapter in isolation (mocked Supabase client).
 * Verifies return shapes match contracts/api.md for:
 *   - signUp: ok + requiresEmailConfirmation shape
 *   - signInWithPassword: ok + userId shape; UNAUTHENTICATED on bad creds
 *   - requestMagicLink: always returns sent:true (anti-enum A5)
 *   - signOut: ok + null
 *   - getUser: ok + User shape; UNAUTHENTICATED when no session
 *
 * A14: all paths return Result<T, DomainError>, never throw.
 * A15: unhappy paths tested first per describe block.
 * A5: anti-enumeration behavior asserted explicitly.
 * A12: getUser returns UNAUTHENTICATED on missing/expired session.
 *
 * Note: Uses vi.mock to stub @supabase/ssr — no live Supabase required.
 * A real integration test against local Supabase requires `supabase start`.
 * That manual step is documented in specs/001-todo-management/quickstart.md.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import type { SupabaseClient } from "@supabase/supabase-js";

// ---------------------------------------------------------------------------
// Mock the Supabase client factory so tests don't need real env vars (A22)
// ---------------------------------------------------------------------------

const mockAuth = {
  signUp: vi.fn(),
  signInWithPassword: vi.fn(),
  signInWithOtp: vi.fn(),
  signOut: vi.fn(),
  getUser: vi.fn(),
  admin: {
    deleteUser: vi.fn(),
  },
};

const mockFrom = vi.fn().mockReturnValue({
  select: vi.fn().mockReturnThis(),
  eq: vi.fn().mockReturnThis(),
  is: vi.fn().mockReturnThis(),
  count: vi.fn().mockResolvedValue({ count: 0, error: null }),
  delete: vi.fn().mockReturnThis(),
});

vi.mock("@/adapters/supabase/client", () => ({
  createServerClient: vi.fn(
    () =>
      ({
        auth: mockAuth,
        from: mockFrom,
      }) as unknown as SupabaseClient,
  ),
  createServiceRoleClient: vi.fn(
    () =>
      ({
        auth: { admin: mockAuth.admin },
        from: mockFrom,
      }) as unknown as SupabaseClient,
  ),
}));

// Import adapter AFTER mock is set up
import { SupabaseAuthProvider } from "@/adapters/supabase/auth-provider";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Build a provider instance with a minimal cookie stub. */
function makeProvider(): SupabaseAuthProvider {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return new SupabaseAuthProvider({} as any);
}

beforeEach(() => {
  vi.clearAllMocks();
});

// ---------------------------------------------------------------------------
// signUp
// ---------------------------------------------------------------------------

describe("SupabaseAuthProvider.signUp", () => {
  it("returns INVALID_INPUT when email is missing", async () => {
    const provider = makeProvider();
    const result = await provider.signUp({ email: "", password: "StrongPass1!" });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("INVALID_INPUT");
    }
  });

  it("returns INVALID_INPUT when password is too weak", async () => {
    const provider = makeProvider();
    const result = await provider.signUp({ email: "a@b.com", password: "weak" });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("INVALID_INPUT");
    }
  });

  it("returns ok with requiresEmailConfirmation:true on standard sign-up", async () => {
    mockAuth.signUp.mockResolvedValueOnce({
      data: { user: { id: "uid-1", email: "a@b.com" }, session: null },
      error: null,
    });

    const provider = makeProvider();
    const result = await provider.signUp({
      email: "a@b.com",
      password: "StrongPass1!",
    });

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(typeof result.value.requiresEmailConfirmation).toBe("boolean");
    }
  });

  it("returns ok (anti-enum A5) when email already exists", async () => {
    // Supabase returns an error for duplicate email — adapter must swallow it
    mockAuth.signUp.mockResolvedValueOnce({
      data: { user: null, session: null },
      error: { message: "User already registered", status: 422 },
    });

    const provider = makeProvider();
    const result = await provider.signUp({
      email: "dup@b.com",
      password: "StrongPass1!",
    });

    // Anti-enumeration: must return ok, not UNAUTHENTICATED or INTERNAL
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value.requiresEmailConfirmation).toBe(true);
    }
  });

  it("returns INTERNAL on unexpected Supabase error", async () => {
    mockAuth.signUp.mockResolvedValueOnce({
      data: null,
      error: { message: "Database connection failed", status: 500 },
    });

    const provider = makeProvider();
    const result = await provider.signUp({
      email: "a@b.com",
      password: "StrongPass1!",
    });

    expect(result.ok).toBe(false);
    if (!result.ok) {
      // 500-class errors → INTERNAL (not leaked message)
      expect(result.error.code).toBe("INTERNAL");
      expect(result.error.message).not.toMatch(/Database connection/i);
    }
  });
});

// ---------------------------------------------------------------------------
// signInWithPassword
// ---------------------------------------------------------------------------

describe("SupabaseAuthProvider.signInWithPassword", () => {
  it("returns UNAUTHENTICATED for wrong password (anti-enum: same code as wrong email)", async () => {
    mockAuth.signInWithPassword.mockResolvedValueOnce({
      data: { user: null, session: null },
      error: { message: "Invalid login credentials", status: 400 },
    });

    const provider = makeProvider();
    const result = await provider.signInWithPassword({
      email: "a@b.com",
      password: "WrongPass1!",
    });

    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("UNAUTHENTICATED");
      // Generic message — no field disclosure (FR-005)
      expect(result.error.message).not.toMatch(/password|email/i);
    }
  });

  it("returns INVALID_INPUT for malformed email", async () => {
    const provider = makeProvider();
    const result = await provider.signInWithPassword({
      email: "not-an-email",
      password: "StrongPass1!",
    });

    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("INVALID_INPUT");
    }
  });

  it("returns ok with userId on successful sign-in", async () => {
    mockAuth.signInWithPassword.mockResolvedValueOnce({
      data: {
        user: { id: "uid-123", email: "a@b.com" },
        session: { access_token: "tok", refresh_token: "rtok" },
      },
      error: null,
    });

    const provider = makeProvider();
    const result = await provider.signInWithPassword({
      email: "a@b.com",
      password: "StrongPass1!",
    });

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value.userId).toBe("uid-123");
    }
  });
});

// ---------------------------------------------------------------------------
// requestMagicLink
// ---------------------------------------------------------------------------

describe("SupabaseAuthProvider.requestMagicLink", () => {
  it("returns INVALID_INPUT for empty email", async () => {
    const provider = makeProvider();
    const result = await provider.requestMagicLink({ email: "" });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("INVALID_INPUT");
    }
  });

  it("returns ok + sent:true even when email does not exist (anti-enum A5)", async () => {
    mockAuth.signInWithOtp.mockResolvedValueOnce({
      data: {},
      error: { message: "User not found", status: 422 },
    });

    const provider = makeProvider();
    const result = await provider.requestMagicLink({ email: "ghost@b.com" });

    // Must ALWAYS return sent:true to avoid enumeration
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value.sent).toBe(true);
    }
  });

  it("returns ok + sent:true on success", async () => {
    mockAuth.signInWithOtp.mockResolvedValueOnce({
      data: {},
      error: null,
    });

    const provider = makeProvider();
    const result = await provider.requestMagicLink({ email: "a@b.com" });

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value.sent).toBe(true);
    }
  });
});

// ---------------------------------------------------------------------------
// signOut
// ---------------------------------------------------------------------------

describe("SupabaseAuthProvider.signOut", () => {
  it("returns ok:true + null on success", async () => {
    mockAuth.signOut.mockResolvedValueOnce({ error: null });

    const provider = makeProvider();
    const result = await provider.signOut();

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value).toBeNull();
    }
  });

  it("returns ok:true even when Supabase signOut fails (best-effort)", async () => {
    // signOut is best-effort — clear cookies regardless of Supabase response
    mockAuth.signOut.mockResolvedValueOnce({
      error: { message: "Network error", status: 503 },
    });

    const provider = makeProvider();
    const result = await provider.signOut();

    // Must still return ok — cookies were cleared
    expect(result.ok).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// getUser (A12 zero-trust — session boundary)
// ---------------------------------------------------------------------------

describe("SupabaseAuthProvider.getUser", () => {
  it("returns UNAUTHENTICATED when no session exists (A12)", async () => {
    mockAuth.getUser.mockResolvedValueOnce({
      data: { user: null },
      error: { message: "Not authenticated", status: 401 },
    });

    const provider = makeProvider();
    const result = await provider.getUser();

    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("UNAUTHENTICATED");
    }
  });

  it("returns ok + User shape when session is valid", async () => {
    mockAuth.getUser.mockResolvedValueOnce({
      data: {
        user: {
          id: "uid-abc",
          email: "a@b.com",
          created_at: "2026-01-01T00:00:00Z",
        },
      },
      error: null,
    });

    const provider = makeProvider();
    const result = await provider.getUser();

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value.id).toBe("uid-abc");
      // email is PII — must be present on User but never logged (A21/A22 enforced at logger)
      expect(typeof result.value.email).toBe("string");
    }
  });

  it("returns UNAUTHENTICATED for expired session token (A12)", async () => {
    mockAuth.getUser.mockResolvedValueOnce({
      data: { user: null },
      error: { message: "JWT expired", status: 401 },
    });

    const provider = makeProvider();
    const result = await provider.getUser();

    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("UNAUTHENTICATED");
    }
  });
});
