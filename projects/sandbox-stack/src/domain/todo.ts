/**
 * Domain entity: Todo
 * A20: pure domain — zero IO, zero framework imports.
 * A11: DTO shape lives in src/lib/schemas.ts; this is the domain model.
 * A13: updatedAt is the optimistic concurrency token.
 * A24: deletedAt enables soft-delete lifecycle.
 */

export interface Todo {
  readonly id: string; // UUID v4
  readonly userId: string; // Owner — matches auth.uid() in RLS (A5, A25)
  readonly text: string; // 1–1000 chars, trimmed
  readonly completedAt: Date | null; // null = active
  readonly createdAt: Date; // A6 audit timestamp
  readonly updatedAt: Date; // A13 concurrency token
  readonly deletedAt: Date | null; // null = active; set = soft-deleted (A24)
}

// -------------------------------------------------------
// Invariants (pure functions — no IO, no side effects)
// -------------------------------------------------------

export const TODO_TEXT_MIN = 1;
export const TODO_TEXT_MAX = 1000;

/**
 * Validates todo text length and content.
 * Returns the trimmed text if valid, or null if invalid.
 */
export function validateTodoText(raw: string): string | null {
  const trimmed = raw.trim();
  if (trimmed.length < TODO_TEXT_MIN || trimmed.length > TODO_TEXT_MAX) {
    return null;
  }
  return trimmed;
}

/** True if the todo is currently active (not soft-deleted, not hard-deleted). */
export function isActive(todo: Todo): boolean {
  return todo.deletedAt === null;
}

/** True if the todo has been completed. */
export function isCompleted(todo: Todo): boolean {
  return todo.completedAt !== null;
}

/** True if the todo is soft-deleted. */
export function isDeleted(todo: Todo): boolean {
  return todo.deletedAt !== null;
}

/**
 * Returns a new Todo with completedAt set to now.
 * Idempotent: if already completed, returns the same todo unchanged (A8).
 */
export function complete(todo: Todo, now: Date = new Date()): Todo {
  if (isCompleted(todo)) return todo;
  return { ...todo, completedAt: now, updatedAt: now };
}

/**
 * Returns a new Todo with completedAt cleared.
 * Idempotent: if not completed, returns the same todo unchanged (A8).
 */
export function uncomplete(todo: Todo, now: Date = new Date()): Todo {
  if (!isCompleted(todo)) return todo;
  return { ...todo, completedAt: null, updatedAt: now };
}

/**
 * Returns a new Todo with deletedAt set to now (soft delete).
 * Idempotent: re-deleting returns the existing deletedAt (A8).
 */
export function softDelete(todo: Todo, now: Date = new Date()): Todo {
  if (isDeleted(todo)) return todo;
  return { ...todo, deletedAt: now, updatedAt: now };
}

/**
 * Returns a new Todo with updated text.
 * Caller must validate text via validateTodoText() before calling this.
 */
export function updateText(todo: Todo, newText: string, now: Date = new Date()): Todo {
  return { ...todo, text: newText, updatedAt: now };
}
