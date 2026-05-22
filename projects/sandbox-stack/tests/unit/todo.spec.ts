/**
 * Unit tests: Todo domain entity invariants
 *
 * Tests: validateTodoText, isActive, isCompleted, isDeleted,
 *        complete (idempotent), uncomplete (idempotent), softDelete (idempotent), updateText.
 *
 * A15: unhappy-path tests written first.
 * A8:  idempotency of complete / uncomplete / softDelete verified explicitly.
 * A13: updatedAt changes on every mutation.
 */

import { describe, it, expect } from "vitest";
import {
  validateTodoText,
  isActive,
  isCompleted,
  isDeleted,
  complete,
  uncomplete,
  softDelete,
  updateText,
  TODO_TEXT_MIN,
  TODO_TEXT_MAX,
} from "@/domain/todo";
import type { Todo } from "@/domain/todo";

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

function makeTodo(overrides: Partial<Todo> = {}): Todo {
  return {
    id: "00000000-0000-0000-0000-000000000001",
    userId: "00000000-0000-0000-0000-000000000099",
    text: "Buy milk",
    completedAt: null,
    createdAt: new Date("2026-01-01T00:00:00Z"),
    updatedAt: new Date("2026-01-01T00:00:00Z"),
    deletedAt: null,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// validateTodoText
// ---------------------------------------------------------------------------

describe("validateTodoText", () => {
  // A15 unhappy paths first
  it("returns null for empty string", () => {
    expect(validateTodoText("")).toBeNull();
  });

  it("returns null for whitespace-only string", () => {
    expect(validateTodoText("   ")).toBeNull();
  });

  it("returns null when trimmed length exceeds TODO_TEXT_MAX", () => {
    const tooLong = "a".repeat(TODO_TEXT_MAX + 1);
    expect(validateTodoText(tooLong)).toBeNull();
  });

  it("returns null when text is exactly TODO_TEXT_MAX + 1 chars after trim", () => {
    // Padding + excess: spaces don't help since trim removes them
    const tooLong = "a".repeat(TODO_TEXT_MAX + 1);
    expect(validateTodoText("  " + tooLong + "  ")).toBeNull();
  });

  // Happy paths
  it("returns trimmed text for a single character", () => {
    expect(validateTodoText("a")).toBe("a");
  });

  it("trims surrounding whitespace", () => {
    expect(validateTodoText("  hello  ")).toBe("hello");
  });

  it("accepts text at exactly TODO_TEXT_MAX chars", () => {
    const maxText = "a".repeat(TODO_TEXT_MAX);
    expect(validateTodoText(maxText)).toBe(maxText);
  });

  it("accepts text at exactly TODO_TEXT_MIN chars", () => {
    const minText = "a".repeat(TODO_TEXT_MIN);
    expect(validateTodoText(minText)).toBe(minText);
  });

  it("preserves internal whitespace", () => {
    expect(validateTodoText("buy   milk")).toBe("buy   milk");
  });
});

// ---------------------------------------------------------------------------
// State predicates
// ---------------------------------------------------------------------------

describe("isActive", () => {
  it("returns true when deletedAt is null", () => {
    expect(isActive(makeTodo({ deletedAt: null }))).toBe(true);
  });

  it("returns false when deletedAt is set", () => {
    expect(isActive(makeTodo({ deletedAt: new Date() }))).toBe(false);
  });
});

describe("isCompleted", () => {
  it("returns false when completedAt is null", () => {
    expect(isCompleted(makeTodo({ completedAt: null }))).toBe(false);
  });

  it("returns true when completedAt is set", () => {
    expect(isCompleted(makeTodo({ completedAt: new Date() }))).toBe(true);
  });
});

describe("isDeleted", () => {
  it("returns false when deletedAt is null", () => {
    expect(isDeleted(makeTodo({ deletedAt: null }))).toBe(false);
  });

  it("returns true when deletedAt is set", () => {
    expect(isDeleted(makeTodo({ deletedAt: new Date() }))).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// complete (A8 idempotency)
// ---------------------------------------------------------------------------

describe("complete", () => {
  it("sets completedAt to provided now", () => {
    const todo = makeTodo({ completedAt: null });
    const now = new Date("2026-06-01T12:00:00Z");
    const result = complete(todo, now);
    expect(result.completedAt).toEqual(now);
  });

  it("updates updatedAt to now when completing", () => {
    const todo = makeTodo({ completedAt: null });
    const now = new Date("2026-06-01T12:00:00Z");
    const result = complete(todo, now);
    expect(result.updatedAt).toEqual(now);
  });

  // A8: idempotency
  it("is idempotent — returns same todo if already completed (A8)", () => {
    const alreadyCompleted = new Date("2026-05-01T00:00:00Z");
    const todo = makeTodo({ completedAt: alreadyCompleted });
    const now = new Date("2026-06-01T12:00:00Z");
    const result = complete(todo, now);
    // completedAt must NOT change on repeat complete
    expect(result.completedAt).toEqual(alreadyCompleted);
    expect(result).toBe(todo); // same reference — no allocation
  });

  it("does not mutate the original todo", () => {
    const todo = makeTodo({ completedAt: null });
    const now = new Date();
    const result = complete(todo, now);
    expect(result).not.toBe(todo);
    expect(todo.completedAt).toBeNull(); // original unchanged
  });

  it("preserves all other fields unchanged", () => {
    const todo = makeTodo({ completedAt: null });
    const now = new Date("2026-06-01T12:00:00Z");
    const result = complete(todo, now);
    expect(result.id).toBe(todo.id);
    expect(result.userId).toBe(todo.userId);
    expect(result.text).toBe(todo.text);
    expect(result.deletedAt).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// uncomplete (A8 idempotency)
// ---------------------------------------------------------------------------

describe("uncomplete", () => {
  it("clears completedAt", () => {
    const todo = makeTodo({ completedAt: new Date("2026-05-01T00:00:00Z") });
    const now = new Date("2026-06-01T12:00:00Z");
    const result = uncomplete(todo, now);
    expect(result.completedAt).toBeNull();
  });

  it("updates updatedAt when uncompleting", () => {
    const todo = makeTodo({ completedAt: new Date("2026-05-01T00:00:00Z") });
    const now = new Date("2026-06-01T12:00:00Z");
    const result = uncomplete(todo, now);
    expect(result.updatedAt).toEqual(now);
  });

  // A8: idempotency
  it("is idempotent — returns same todo if not completed (A8)", () => {
    const todo = makeTodo({ completedAt: null });
    const now = new Date("2026-06-01T12:00:00Z");
    const result = uncomplete(todo, now);
    expect(result).toBe(todo); // same reference
  });

  it("does not mutate the original todo", () => {
    const completedAt = new Date("2026-05-01T00:00:00Z");
    const todo = makeTodo({ completedAt });
    const result = uncomplete(todo, new Date());
    expect(result).not.toBe(todo);
    expect(todo.completedAt).toEqual(completedAt); // original unchanged
  });
});

// ---------------------------------------------------------------------------
// softDelete (A8 idempotency, A24 soft-delete)
// ---------------------------------------------------------------------------

describe("softDelete", () => {
  it("sets deletedAt to now", () => {
    const todo = makeTodo({ deletedAt: null });
    const now = new Date("2026-06-01T12:00:00Z");
    const result = softDelete(todo, now);
    expect(result.deletedAt).toEqual(now);
  });

  it("updates updatedAt when soft-deleting", () => {
    const todo = makeTodo({ deletedAt: null });
    const now = new Date("2026-06-01T12:00:00Z");
    const result = softDelete(todo, now);
    expect(result.updatedAt).toEqual(now);
  });

  // A8: idempotency — second delete preserves original deletedAt
  it("is idempotent — returns same todo if already deleted (A8)", () => {
    const originalDeletedAt = new Date("2026-05-01T00:00:00Z");
    const todo = makeTodo({ deletedAt: originalDeletedAt });
    const now = new Date("2026-06-01T12:00:00Z");
    const result = softDelete(todo, now);
    expect(result).toBe(todo); // same reference
    expect(result.deletedAt).toEqual(originalDeletedAt); // not overwritten
  });

  it("does not mutate the original todo", () => {
    const todo = makeTodo({ deletedAt: null });
    const result = softDelete(todo, new Date());
    expect(result).not.toBe(todo);
    expect(todo.deletedAt).toBeNull();
  });

  it("preserves all other fields", () => {
    const todo = makeTodo({ deletedAt: null });
    const now = new Date();
    const result = softDelete(todo, now);
    expect(result.id).toBe(todo.id);
    expect(result.text).toBe(todo.text);
    expect(result.completedAt).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// updateText
// ---------------------------------------------------------------------------

describe("updateText", () => {
  it("returns a new todo with updated text", () => {
    const todo = makeTodo({ text: "old text" });
    const now = new Date("2026-06-01T12:00:00Z");
    const result = updateText(todo, "new text", now);
    expect(result.text).toBe("new text");
  });

  it("updates updatedAt", () => {
    const todo = makeTodo();
    const now = new Date("2026-06-01T12:00:00Z");
    const result = updateText(todo, "new text", now);
    expect(result.updatedAt).toEqual(now);
  });

  it("does not mutate the original todo", () => {
    const todo = makeTodo({ text: "original" });
    updateText(todo, "changed", new Date());
    expect(todo.text).toBe("original");
  });

  it("preserves id, userId, completedAt, deletedAt", () => {
    const completedAt = new Date("2026-03-01T00:00:00Z");
    const todo = makeTodo({ completedAt });
    const result = updateText(todo, "new", new Date());
    expect(result.id).toBe(todo.id);
    expect(result.userId).toBe(todo.userId);
    expect(result.completedAt).toEqual(completedAt);
    expect(result.deletedAt).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// State transition sequences (A13 concurrency-aware flows)
// ---------------------------------------------------------------------------

describe("state transition sequences", () => {
  it("create → complete → uncomplete restores to active-not-completed", () => {
    const todo = makeTodo({ completedAt: null });
    const t1 = new Date("2026-06-01T10:00:00Z");
    const t2 = new Date("2026-06-01T11:00:00Z");

    const completed = complete(todo, t1);
    const uncompleted = uncomplete(completed, t2);

    expect(uncompleted.completedAt).toBeNull();
    expect(uncompleted.updatedAt).toEqual(t2);
    expect(isActive(uncompleted)).toBe(true);
    expect(isCompleted(uncompleted)).toBe(false);
  });

  it("completed todo can be soft-deleted", () => {
    const todo = makeTodo({ completedAt: new Date("2026-05-01T00:00:00Z") });
    const now = new Date("2026-06-01T00:00:00Z");
    const deleted = softDelete(todo, now);
    expect(isDeleted(deleted)).toBe(true);
    expect(deleted.completedAt).toEqual(todo.completedAt); // completion preserved
  });

  it("updatedAt is monotonically advancing through mutations (A13)", () => {
    const t0 = new Date("2026-06-01T10:00:00Z");
    const t1 = new Date("2026-06-01T10:01:00Z");
    const t2 = new Date("2026-06-01T10:02:00Z");
    const t3 = new Date("2026-06-01T10:03:00Z");

    const base = makeTodo({ updatedAt: t0 });
    const step1 = updateText(base, "step 1", t1);
    const step2 = complete(step1, t2);
    const step3 = uncomplete(step2, t3);

    expect(step1.updatedAt).toEqual(t1);
    expect(step2.updatedAt).toEqual(t2);
    expect(step3.updatedAt).toEqual(t3);
  });
});
