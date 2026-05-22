/**
 * SupabaseTodoRepository
 * Implements the TodoRepository port using Supabase + @supabase/ssr.
 *
 * A5:  every query is scoped to userId; RLS enforces isolation at DB layer.
 *      App-layer ownership check is an ADDITIONAL gate (defense-in-depth per A25).
 * A8:  complete/uncomplete/softDelete are idempotent: if state already matches,
 *      return current row without mutation.
 * A11: DAO pattern — Supabase rows translated to domain Todo via rowToTodo().
 * A12: caller (server action) must have already asserted session; this adapter
 *      receives the user-scoped Supabase client (session baked in via cookie/token).
 * A13: update/complete/uncomplete accept expectedUpdatedAt; mismatch → STALE_VERSION.
 * A14: all methods return Result<T>; never throw.
 * A24: softDelete sets deleted_at = now(); listActive filters deleted_at IS NULL.
 *      Overflow cap: listActive uses LIMIT 201 and sets overflow flag if > 200 rows.
 */

import type { SupabaseClient } from "@supabase/supabase-js";

import type { TodoRepository } from "@/domain/ports/todo-repository";
import type {
  ListActiveTodosOptions,
  ListActiveTodosResult,
  CreateTodoOptions,
  UpdateTodoOptions,
  CompleteTodoOptions,
  UncompleteTodoOptions,
  SoftDeleteTodoOptions,
} from "@/domain/ports/todo-repository";
import type { Todo } from "@/domain/todo";
import type { Result } from "@/lib/result";
import { ok, err } from "@/lib/result";
import { Errors } from "@/domain/errors";
import { validateTodoText } from "@/domain/todo";
import { logger } from "@/adapters/logging/pino";

// ---------------------------------------------------------------------------
// Row shape returned by Supabase (A11 DAO)
// ---------------------------------------------------------------------------

interface TodoRow {
  id: string;
  user_id: string;
  text: string;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

/** Translate a Supabase DB row to the domain Todo entity (A11 DTO coercion). */
function rowToTodo(row: TodoRow): Todo {
  return {
    id: row.id,
    userId: row.user_id,
    text: row.text,
    completedAt: row.completed_at ? new Date(row.completed_at) : null,
    createdAt: new Date(row.created_at),
    updatedAt: new Date(row.updated_at),
    deletedAt: row.deleted_at ? new Date(row.deleted_at) : null,
  };
}

// ---------------------------------------------------------------------------
// SupabaseTodoRepository
// ---------------------------------------------------------------------------

export class SupabaseTodoRepository implements TodoRepository {
  constructor(private readonly _client: SupabaseClient) {}

  // -------------------------------------------------------------------------
  // listActive
  // A24: cap at 200; LIMIT 201 to detect overflow.
  // A5:  user_id scoped + RLS enforces at DB layer.
  // Cursor-based pagination: pageCursor is the created_at of the last item seen.
  // -------------------------------------------------------------------------

  async listActive(options: ListActiveTodosOptions): Promise<Result<ListActiveTodosResult>> {
    const limit = Math.min(options.limit ?? 50, 100);
    // A24: fetch 201 to detect overflow
    const fetchLimit = limit + 1;

    try {
      let query = this._client
        .from("todos")
        .select("*")
        .eq("user_id", options.userId)
        .is("deleted_at", null)
        .order("created_at", { ascending: false })
        .limit(fetchLimit);

      // Cursor: exclude items at-or-after the cursor timestamp
      if (options.pageCursor) {
        query = query.lt("created_at", options.pageCursor);
      }

      const { data, error } = await query;

      if (error) {
        return err(Errors.internal());
      }

      const rows = (data ?? []) as TodoRow[];

      // A24: overflow detection
      const hasMore = rows.length > limit;
      const pageRows = hasMore ? rows.slice(0, limit) : rows;

      const items = pageRows.map(rowToTodo);
      const nextCursor =
        hasMore && pageRows.length > 0
          ? pageRows[pageRows.length - 1].created_at
          : null;

      return ok({ items, nextCursor });
    } catch (e) {
      // G-3/G-6: structured log before returning internal error
      logger.error({ action: "listActive", error: e instanceof Error ? e.message : String(e) }, "TodoRepository.listActive: unexpected exception");
      return err(Errors.internal());
    }
  }

  // -------------------------------------------------------------------------
  // create
  // A5: insert with user_id = options.userId; RLS also enforces this.
  // -------------------------------------------------------------------------

  async create(options: CreateTodoOptions): Promise<Result<Todo>> {
    // App-layer text validation (mirrors DB constraint)
    const trimmed = validateTodoText(options.text);
    if (trimmed === null) {
      return err(
        Errors.invalidInput(
          `Todo text must be between 1 and 1000 characters.`,
        ),
      );
    }

    try {
      const { data, error } = await this._client
        .from("todos")
        .insert({ user_id: options.userId, text: trimmed })
        .select()
        .single();

      if (error) {
        // Postgres check constraint violation
        if (error.code === "23514") {
          return err(Errors.invalidInput("Todo text is invalid."));
        }
        return err(Errors.internal());
      }

      return ok(rowToTodo(data as TodoRow));
    } catch (e) {
      // G-3/G-6: structured log before returning internal error
      logger.error({ action: "create", error: e instanceof Error ? e.message : String(e) }, "TodoRepository.create: unexpected exception");
      return err(Errors.internal());
    }
  }

  // -------------------------------------------------------------------------
  // update (A13 optimistic concurrency)
  // -------------------------------------------------------------------------

  async update(options: UpdateTodoOptions): Promise<Result<Todo>> {
    const trimmed = validateTodoText(options.text);
    if (trimmed === null) {
      return err(Errors.invalidInput("Todo text must be between 1 and 1000 characters."));
    }

    try {
      // A13: match on both id + user_id + updated_at (concurrency token)
      // RLS enforces user_id isolation; the updated_at check is app-layer A13.
      const expectedIso = options.expectedUpdatedAt.toISOString();

      const { data, error, count } = await this._client
        .from("todos")
        .update({ text: trimmed })
        .eq("id", options.id)
        .eq("user_id", options.userId)
        .eq("updated_at", expectedIso)
        .is("deleted_at", null)
        .select()
        .returns<TodoRow[]>();

      if (error) {
        return err(Errors.internal());
      }

      const rows = data ?? [];

      if (rows.length === 0) {
        // Could be STALE_VERSION (updated_at mismatch) or NOT_FOUND (RLS denied / deleted)
        // Distinguish: fetch the row as this user to check existence
        return await this._resolveUpdateConflict(options.id, options.userId, expectedIso);
      }

      return ok(rowToTodo(rows[0]));
    } catch (e) {
      // G-3/G-6: structured log before returning internal error
      logger.error({ action: "update", error: e instanceof Error ? e.message : String(e) }, "TodoRepository.update: unexpected exception");
      return err(Errors.internal());
    }
  }

  /**
   * Called when update returns 0 rows — distinguish STALE_VERSION from NOT_FOUND/FORBIDDEN.
   * A13: if row exists but updated_at differs → STALE_VERSION.
   * A5:  if row doesn't exist for this user → NOT_FOUND (RLS denied).
   */
  private async _resolveUpdateConflict(
    id: string,
    userId: string,
    _expectedIso: string,
  ): Promise<Result<Todo>> {
    const { data } = await this._client
      .from("todos")
      .select("id, updated_at, deleted_at")
      .eq("id", id)
      .eq("user_id", userId)
      .single();

    if (!data) {
      // RLS returned nothing — FORBIDDEN (cross-tenant) or NOT_FOUND
      return err(Errors.notFound());
    }

    const row = data as Pick<TodoRow, "id" | "updated_at" | "deleted_at">;

    if (row.deleted_at !== null) {
      return err(Errors.notFound());
    }

    // Row exists but updated_at didn't match → STALE_VERSION (A13)
    return err(Errors.staleVersion());
  }

  // -------------------------------------------------------------------------
  // complete (A8 idempotent, A13 concurrency)
  // If already completed, return current row without mutation.
  // -------------------------------------------------------------------------

  async complete(options: CompleteTodoOptions): Promise<Result<Todo>> {
    try {
      // Fetch current state first (needed for idempotency check A8)
      const current = await this._fetchOwned(options.id, options.userId);
      if (!current.ok) return current;

      const todo = current.value;

      // A8: already completed — idempotent success
      if (todo.completedAt !== null) {
        return ok(todo);
      }

      // A13: check expectedUpdatedAt
      if (todo.updatedAt.toISOString() !== options.expectedUpdatedAt.toISOString()) {
        return err(Errors.staleVersion());
      }

      const now = new Date().toISOString();
      const { data, error } = await this._client
        .from("todos")
        .update({ completed_at: now })
        .eq("id", options.id)
        .eq("user_id", options.userId)
        .is("deleted_at", null)
        .select()
        .single();

      if (error || !data) {
        return err(Errors.internal());
      }

      return ok(rowToTodo(data as TodoRow));
    } catch (e) {
      // G-3/G-6: structured log before returning internal error
      logger.error({ action: "complete", error: e instanceof Error ? e.message : String(e) }, "TodoRepository.complete: unexpected exception");
      return err(Errors.internal());
    }
  }

  // -------------------------------------------------------------------------
  // uncomplete (A8 idempotent, A13 concurrency)
  // If not completed, return current row without mutation.
  // -------------------------------------------------------------------------

  async uncomplete(options: UncompleteTodoOptions): Promise<Result<Todo>> {
    try {
      const current = await this._fetchOwned(options.id, options.userId);
      if (!current.ok) return current;

      const todo = current.value;

      // A8: already not completed — idempotent success
      if (todo.completedAt === null) {
        return ok(todo);
      }

      // A13: check expectedUpdatedAt
      if (todo.updatedAt.toISOString() !== options.expectedUpdatedAt.toISOString()) {
        return err(Errors.staleVersion());
      }

      const { data, error } = await this._client
        .from("todos")
        .update({ completed_at: null })
        .eq("id", options.id)
        .eq("user_id", options.userId)
        .is("deleted_at", null)
        .select()
        .single();

      if (error || !data) {
        return err(Errors.internal());
      }

      return ok(rowToTodo(data as TodoRow));
    } catch (e) {
      // G-3/G-6: structured log before returning internal error
      logger.error({ action: "uncomplete", error: e instanceof Error ? e.message : String(e) }, "TodoRepository.uncomplete: unexpected exception");
      return err(Errors.internal());
    }
  }

  // -------------------------------------------------------------------------
  // softDelete (A8 idempotent, A24 soft-delete)
  // -------------------------------------------------------------------------

  async softDelete(options: SoftDeleteTodoOptions): Promise<Result<{ deletedAt: Date }>> {
    try {
      // Check if already deleted (A8 idempotency)
      const { data: existing } = await this._client
        .from("todos")
        .select("id, deleted_at")
        .eq("id", options.id)
        .eq("user_id", options.userId)
        .single();

      if (!existing) {
        // Not found for this user (RLS) — FORBIDDEN/NOT_FOUND
        return err(Errors.notFound());
      }

      const row = existing as Pick<TodoRow, "id" | "deleted_at">;

      // A8: already deleted — return existing deletedAt without mutation
      if (row.deleted_at !== null) {
        return ok({ deletedAt: new Date(row.deleted_at) });
      }

      // Perform soft delete
      const now = new Date().toISOString();
      const { data, error } = await this._client
        .from("todos")
        .update({ deleted_at: now })
        .eq("id", options.id)
        .eq("user_id", options.userId)
        .is("deleted_at", null)
        .select("deleted_at")
        .single();

      if (error || !data) {
        return err(Errors.internal());
      }

      const deletedAt = (data as Pick<TodoRow, "deleted_at">).deleted_at;
      if (!deletedAt) {
        return err(Errors.internal());
      }

      return ok({ deletedAt: new Date(deletedAt) });
    } catch (e) {
      // G-3/G-6: structured log before returning internal error
      logger.error({ action: "softDelete", error: e instanceof Error ? e.message : String(e) }, "TodoRepository.softDelete: unexpected exception");
      return err(Errors.internal());
    }
  }

  // -------------------------------------------------------------------------
  // _fetchOwned — fetch a single row owned by userId; FORBIDDEN if not found
  // A5 + A25: RLS enforces ownership; app layer double-checks
  // -------------------------------------------------------------------------

  private async _fetchOwned(id: string, userId: string): Promise<Result<Todo>> {
    const { data, error } = await this._client
      .from("todos")
      .select("*")
      .eq("id", id)
      .eq("user_id", userId)
      .is("deleted_at", null)
      .single();

    if (error || !data) {
      return err(Errors.notFound());
    }

    return ok(rowToTodo(data as TodoRow));
  }
}
