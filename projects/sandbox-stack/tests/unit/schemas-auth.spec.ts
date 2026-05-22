/**
 * Vitest unit: Zod schema validation for auth inputs
 *
 * Verifies that SignUpInputSchema, SignInWithPasswordInputSchema, and
 * RequestMagicLinkInputSchema reject invalid data per contracts/api.md:
 *   - empty fields
 *   - oversized fields (> 256 chars)
 *   - malformed email
 *   - weak password (< 8 chars, no number/symbol)
 *
 * A14: safeParse must return Err<INVALID_INPUT>, never throw.
 * A15: rejection paths tested first.
 * A3: schema shapes match contracts/api.md exactly.
 */

import { describe, it, expect } from "vitest";
import {
  SignUpInputSchema,
  SignInWithPasswordInputSchema,
  RequestMagicLinkInputSchema,
  safeParse,
} from "@/lib/schemas";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** String of n characters. */
const repeat = (ch: string, n: number) => ch.repeat(n);

// ---------------------------------------------------------------------------
// SignUpInputSchema
// ---------------------------------------------------------------------------

describe("SignUpInputSchema", () => {
  // --- Rejection paths first (A15) ---

  describe("email validation", () => {
    it("rejects empty email", () => {
      const result = SignUpInputSchema.safeParse({
        email: "",
        password: "StrongPass1!",
      });
      expect(result.success).toBe(false);
    });

    it("rejects missing email field", () => {
      const result = SignUpInputSchema.safeParse({ password: "StrongPass1!" });
      expect(result.success).toBe(false);
    });

    it("rejects malformed email (no @)", () => {
      const result = SignUpInputSchema.safeParse({
        email: "notanemail",
        password: "StrongPass1!",
      });
      expect(result.success).toBe(false);
    });

    it("rejects email over 256 chars", () => {
      const local = repeat("a", 250);
      const result = SignUpInputSchema.safeParse({
        email: `${local}@b.com`,
        password: "StrongPass1!",
      });
      expect(result.success).toBe(false);
    });

    it("rejects email with only whitespace", () => {
      const result = SignUpInputSchema.safeParse({
        email: "   ",
        password: "StrongPass1!",
      });
      expect(result.success).toBe(false);
    });
  });

  describe("password validation", () => {
    it("rejects empty password", () => {
      const result = SignUpInputSchema.safeParse({
        email: "a@b.com",
        password: "",
      });
      expect(result.success).toBe(false);
    });

    it("rejects password under 8 chars", () => {
      const result = SignUpInputSchema.safeParse({
        email: "a@b.com",
        password: "Abc1!",
      });
      expect(result.success).toBe(false);
    });

    it("rejects password with no number or symbol", () => {
      const result = SignUpInputSchema.safeParse({
        email: "a@b.com",
        password: "AllLettersOnly",
      });
      expect(result.success).toBe(false);
    });

    it("rejects password over 256 chars", () => {
      const result = SignUpInputSchema.safeParse({
        email: "a@b.com",
        password: repeat("A", 257) + "1!",
      });
      expect(result.success).toBe(false);
    });
  });

  // --- Acceptance paths ---

  describe("valid inputs", () => {
    it("accepts valid email + strong password (number)", () => {
      const result = SignUpInputSchema.safeParse({
        email: "user@example.com",
        password: "Password1",
      });
      expect(result.success).toBe(true);
    });

    it("accepts valid email + strong password (symbol)", () => {
      const result = SignUpInputSchema.safeParse({
        email: "user@example.com",
        password: "Password!",
      });
      expect(result.success).toBe(true);
    });

    it("accepts email with subdomain", () => {
      const result = SignUpInputSchema.safeParse({
        email: "user@mail.example.co.uk",
        password: "Pass1word!",
      });
      expect(result.success).toBe(true);
    });

    it("accepts email with plus alias", () => {
      const result = SignUpInputSchema.safeParse({
        email: "user+test@example.com",
        password: "Pass1word!",
      });
      expect(result.success).toBe(true);
    });
  });
});

// ---------------------------------------------------------------------------
// SignInWithPasswordInputSchema
// ---------------------------------------------------------------------------

describe("SignInWithPasswordInputSchema", () => {
  // No complexity check on sign-in (per schemas.ts contract)

  it("rejects empty email", () => {
    const result = SignInWithPasswordInputSchema.safeParse({
      email: "",
      password: "anything",
    });
    expect(result.success).toBe(false);
  });

  it("rejects malformed email", () => {
    const result = SignInWithPasswordInputSchema.safeParse({
      email: "bad-email",
      password: "anything",
    });
    expect(result.success).toBe(false);
  });

  it("rejects empty password", () => {
    const result = SignInWithPasswordInputSchema.safeParse({
      email: "a@b.com",
      password: "",
    });
    expect(result.success).toBe(false);
  });

  it("accepts valid email + any non-empty password (no complexity on sign-in)", () => {
    // sign-in should NOT re-check password strength (would break sign-in for old users)
    const result = SignInWithPasswordInputSchema.safeParse({
      email: "a@b.com",
      password: "simple",
    });
    expect(result.success).toBe(true);
  });

  it("accepts oversized (but valid) password on sign-in", () => {
    // Truncate-style passwords may exist — don't reject based on length on sign-in
    const result = SignInWithPasswordInputSchema.safeParse({
      email: "a@b.com",
      password: repeat("P", 100),
    });
    expect(result.success).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// RequestMagicLinkInputSchema
// ---------------------------------------------------------------------------

describe("RequestMagicLinkInputSchema", () => {
  it("rejects empty email", () => {
    const result = RequestMagicLinkInputSchema.safeParse({ email: "" });
    expect(result.success).toBe(false);
  });

  it("rejects malformed email", () => {
    const result = RequestMagicLinkInputSchema.safeParse({
      email: "notanemail",
    });
    expect(result.success).toBe(false);
  });

  it("rejects email over 256 chars", () => {
    const result = RequestMagicLinkInputSchema.safeParse({
      email: `${repeat("a", 250)}@b.com`,
    });
    expect(result.success).toBe(false);
  });

  it("accepts valid email", () => {
    const result = RequestMagicLinkInputSchema.safeParse({
      email: "user@example.com",
    });
    expect(result.success).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// safeParse helper (A14 — returns Result<T>, never throws)
// ---------------------------------------------------------------------------

describe("safeParse helper", () => {
  it("returns ok:false + INVALID_INPUT on parse failure", () => {
    const result = safeParse(SignUpInputSchema, { email: "", password: "" });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error.code).toBe("INVALID_INPUT");
      expect(typeof result.error.message).toBe("string");
      expect(result.error.message.length).toBeGreaterThan(0);
    }
  });

  it("returns ok:true on valid input", () => {
    const result = safeParse(SignUpInputSchema, {
      email: "user@example.com",
      password: "StrongPass1!",
    });
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value.email).toBe("user@example.com");
    }
  });

  it("never throws on arbitrary input (A14)", () => {
    expect(() =>
      safeParse(SignUpInputSchema, null),
    ).not.toThrow();

    expect(() =>
      safeParse(SignUpInputSchema, undefined),
    ).not.toThrow();

    expect(() =>
      safeParse(SignUpInputSchema, 42),
    ).not.toThrow();

    expect(() =>
      safeParse(SignUpInputSchema, { email: null, password: [] }),
    ).not.toThrow();
  });

  it("concatenates multiple validation errors into the message", () => {
    const result = safeParse(SignUpInputSchema, {
      email: "bad",
      password: "w",
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      // Message should mention more than one issue
      expect(result.error.message).toContain(";");
    }
  });
});
