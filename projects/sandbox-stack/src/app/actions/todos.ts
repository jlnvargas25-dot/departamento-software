/**
 * Todo server actions + structured logging
 *
 * Exports: createTodo, listActiveTodos, updateTodo, completeTodo, uncompleteTodo, deleteTodo
 *
 * Every action follows the same pattern (reused from auth.ts, per Principio II):
 *   1. PREVENTIVA  — zod input validation
 *   2. VERIFICABLE — zero-trust session assertion (A12: getUser() at top of every action)
 *   3. Execute     — delegate to TodoRepository adapter
 *   4. CORRECTIVA  — write todo_events row + structured log (A21)
 *   5. Return      — Result<T, DomainError>; nothing thrown (A14)
 *
 * A5:  userId from session (not from input) — user cannot forge ownership (A25).
 * A8:  complete/uncomplete/deleteTodo are idempotent (enforced in repository).
 * A12: getUser() called at the top of every action; absent session → UNAUTHENTICATED.
 * A13: update/complete/uncomplete accept expectedUpdatedAt for concurrency guard.
 * A14: all paths return Result<T>; no throws escape.
 * A21: every outcome logged with user_id, action, todo_id, outcome, duration_ms.
 * A24: deleteTodo is a soft delete; deleted_at = now().
 * A25: userId sourced from getUser() session, never from client input.
 */

"use server";

import { cookies, headers } from "next/headers";

import type { Result } from "@/lib/result";
import { err } from "@/lib/result";
import { Errors } from "@/domain/errors";
import { logActionResult, logger } from "@/adapters/logging/pino";
import { createServerClient, createServiceRoleClient } from "@/adapters/supabase/client";
import { SupabaseTodoRepository } from "@/adapters/supabase/todo-repository";
import type { Todo } from "@/domain/todo";
import type { ListActiveTodosResult } from "@/domain/ports/todo-repository";

import {
  CreateTodoInputSchema,
  ListActiveTodosInputSchema,
  UpdateTodoInputSchema,
  CompleteTodoInputSchema,
  UncompleteTodoInputSchema,
  DeleteTodoInputSchema,
  safeParse,
} from "@/lib/schemas";

// ---------------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------------

/**
 * Resolve the authenticated user from the current request's session cookie.
 * A12: UNAUTHENTICATED returned immediately if session is absent or expired.
 * A25: userId comes from getUser() — never from client input.
 */
async function resolveUser(): Promise<
  | { ok: true; userId: string; client: ReturnType<typeof createServerClient> }
  | { ok: false; result: Result<never> }
> {
  const cookieStore = await cookies();
  const supabase = createServerClient(cookieStore);
  const {
    data: { user },
    error,
  } = await supabase.auth.getUser();

  if (error || !user) {
    return { ok: false, result: err(Errors.unauthenticated()) };
  }

  return { ok: true, userId: user.id, client: supabase };
}

/** Read the correlation ID injected by middleware (OBS-3). */
async function getRequestId(): Promise<string | undefined> {
  const hdrs = await headers();
  return hdrs.get("x-request-id") ?? undefined;
}

/** Build a TodoRepository bound to the current user's session client. */
function makeRepo(client: ReturnType<typeof createServerClient>): SupabaseTodoRepository {
  return new SupabaseTodoRepository(client);
}

/**
 * Append a row to todo_events via service-role client.
 * A6: append-only; no update/delete.
 * A21: payload never contains raw PII — only text snippet (first 100 chars, trimmed).
 * A22: service-role client stays server-side.
 */
async function writeTodoEvent(params: {
  kind: "create" | "update" | "complete" | "uncomplete" | "delete";
  actorUserId: string;
  todoId: string;
  payload?: Record<string, unknown>;
}): Promise<void> {
  try {
    const serviceClient = createServiceRoleClient();
    await serviceClient.from("todo_events").insert({
      kind: params.kind,
      actor_user_id: params.actorUserId,
      todo_id: params.todoId,
      payload: params.payload ?? null,
    });
  } catch (e) {
    // Non-fatal — event write must never break the primary flow (A14)
    // G-3/G-6: structured log so infra has visibility without alarming callers
    logger.warn(
      {
        action: "writeTodoEvent",
        errorCode: "TODO_EVENT_WRITE_FAILED",
        error: e instanceof Error ? e.message : String(e),
      },
      "writeTodoEvent: failed to insert todo_events row (non-fatal)",
    );
  }
}

// ---------------------------------------------------------------------------
// createTodo
// A12: session required.
// A25: userId from session.
// ---------------------------------------------------------------------------

export async function createTodo(input: unknown): Promise<Result<Todo>> {
  const start = Date.now();
  const requestId = await getRequestId();

  // Step 1: validate input (PREVENTIVA)
  const parsed = safeParse(CreateTodoInputSchema, input);
  if (!parsed.ok) {
    logActionResult({
      action: "createTodo",
      outcome: "error",
      errorCode: "INVALID_INPUT",
      durationMs: Date.now() - start,
      requestId,
    });
    return parsed;
  }

  // Step 2: zero-trust session gate (A12)
  const session = await resolveUser();
  if (!session.ok) {
    logActionResult({
      action: "createTodo",
      outcome: "error",
      errorCode: "UNAUTHENTICATED",
      durationMs: Date.now() - start,
      requestId,
    });
    return session.result;
  }

  const { userId, client } = session;
  const repo = makeRepo(client);

  // Step 3: execute via port
  const result = await repo.create({ userId, text: parsed.value.text });
  const durationMs = Date.now() - start;

  if (!result.ok) {
    logActionResult({
      action: "createTodo",
      outcome: "error",
      errorCode: result.error.code,
      userId,
      durationMs,
      requestId,
    });
    return result;
  }

  // Step 4: audit event + log (A21, A6)
  await writeTodoEvent({ kind: "create", actorUserId: userId, todoId: result.value.id });
  logActionResult({
    action: "createTodo",
    outcome: "success",
    userId,
    todoId: result.value.id,
    durationMs,
    requestId,
  });

  return result;
}

// ---------------------------------------------------------------------------
// listActiveTodos
// A12: session required.
// A24: cap at 200; overflow returned as metadata.
// ---------------------------------------------------------------------------

export async function listActiveTodos(
  input: unknown,
): Promise<Result<ListActiveTodosResult & { overflow?: boolean }>> {
  const start = Date.now();
  const requestId = await getRequestId();

  const parsed = safeParse(ListActiveTodosInputSchema, input);
  if (!parsed.ok) {
    logActionResult({
      action: "listActiveTodos",
      outcome: "error",
      errorCode: "INVALID_INPUT",
      durationMs: Date.now() - start,
      requestId,
    });
    return parsed;
  }

  const session = await resolveUser();
  if (!session.ok) {
    logActionResult({
      action: "listActiveTodos",
      outcome: "error",
      errorCode: "UNAUTHENTICATED",
      durationMs: Date.now() - start,
      requestId,
    });
    return session.result;
  }

  const { userId, client } = session;
  const repo = makeRepo(client);

  // A24: request limit+1 via LIMIT 201 convention — done inside repo.listActive
  const result = await repo.listActive({
    userId,
    pageCursor: parsed.value.pageCursor,
    limit: parsed.value.limit,
  });

  const durationMs = Date.now() - start;

  if (!result.ok) {
    logActionResult({
      action: "listActiveTodos",
      outcome: "error",
      errorCode: result.error.code,
      userId,
      durationMs,
      requestId,
    });
    return result;
  }

  logActionResult({ action: "listActiveTodos", outcome: "success", userId, durationMs, requestId });
  return result;
}

// ---------------------------------------------------------------------------
// updateTodo
// A12: session required.
// A13: expectedUpdatedAt enforces optimistic concurrency.
// A5:  userId from session — cannot forge ownership.
// ---------------------------------------------------------------------------

export async function updateTodo(input: unknown): Promise<Result<Todo>> {
  const start = Date.now();
  const requestId = await getRequestId();

  const parsed = safeParse(UpdateTodoInputSchema, input);
  if (!parsed.ok) {
    logActionResult({
      action: "updateTodo",
      outcome: "error",
      errorCode: "INVALID_INPUT",
      durationMs: Date.now() - start,
      requestId,
    });
    return parsed;
  }

  const session = await resolveUser();
  if (!session.ok) {
    logActionResult({
      action: "updateTodo",
      outcome: "error",
      errorCode: "UNAUTHENTICATED",
      durationMs: Date.now() - start,
      requestId,
    });
    return session.result;
  }

  const { userId, client } = session;
  const repo = makeRepo(client);

  const result = await repo.update({
    id: parsed.value.id,
    userId,
    text: parsed.value.text,
    expectedUpdatedAt: new Date(parsed.value.expectedUpdatedAt),
  });

  const durationMs = Date.now() - start;

  if (!result.ok) {
    logActionResult({
      action: "updateTodo",
      outcome: "error",
      errorCode: result.error.code,
      userId,
      todoId: parsed.value.id,
      durationMs,
      requestId,
    });
    return result;
  }

  await writeTodoEvent({
    kind: "update",
    actorUserId: userId,
    todoId: result.value.id,
    // A21: only first 100 chars of new text in payload — no full content exposure
    payload: { text_preview: parsed.value.text.slice(0, 100) },
  });
  logActionResult({
    action: "updateTodo",
    outcome: "success",
    userId,
    todoId: result.value.id,
    durationMs,
    requestId,
  });

  return result;
}

// ---------------------------------------------------------------------------
// Idempotency policy for state-mutation actions (completeTodo, uncompleteTodo, deleteTodo)
//
// A8 idempotency is satisfied via state-based check in the repository:
//   - completeTodo:   fetch-then-skip-if-already-completed
//   - uncompleteTodo: fetch-then-skip-if-already-not-completed
//   - deleteTodo:     fetch-then-skip-if-already-deleted (returns existing deleted_at)
//
// Explicit Idempotency-Key header is NOT implemented for v1.
// Formal exception: decisions/ADR-SB-004-idempotency-via-state-not-header.md
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// completeTodo
// A8: idempotent (handled in repository).
// A13: expectedUpdatedAt concurrency guard.
// ---------------------------------------------------------------------------

export async function completeTodo(input: unknown): Promise<Result<Todo>> {
  const start = Date.now();
  const requestId = await getRequestId();

  const parsed = safeParse(CompleteTodoInputSchema, input);
  if (!parsed.ok) {
    logActionResult({
      action: "completeTodo",
      outcome: "error",
      errorCode: "INVALID_INPUT",
      durationMs: Date.now() - start,
      requestId,
    });
    return parsed;
  }

  const session = await resolveUser();
  if (!session.ok) {
    logActionResult({
      action: "completeTodo",
      outcome: "error",
      errorCode: "UNAUTHENTICATED",
      durationMs: Date.now() - start,
      requestId,
    });
    return session.result;
  }

  const { userId, client } = session;
  const repo = makeRepo(client);

  const result = await repo.complete({
    id: parsed.value.id,
    userId,
    expectedUpdatedAt: new Date(parsed.value.expectedUpdatedAt),
  });

  const durationMs = Date.now() - start;

  if (!result.ok) {
    logActionResult({
      action: "completeTodo",
      outcome: "error",
      errorCode: result.error.code,
      userId,
      todoId: parsed.value.id,
      durationMs,
      requestId,
    });
    return result;
  }

  await writeTodoEvent({ kind: "complete", actorUserId: userId, todoId: result.value.id });
  logActionResult({
    action: "completeTodo",
    outcome: "success",
    userId,
    todoId: result.value.id,
    durationMs,
    requestId,
  });

  return result;
}

// ---------------------------------------------------------------------------
// uncompleteTodo
// A8: idempotent.
// ---------------------------------------------------------------------------

export async function uncompleteTodo(input: unknown): Promise<Result<Todo>> {
  const start = Date.now();
  const requestId = await getRequestId();

  const parsed = safeParse(UncompleteTodoInputSchema, input);
  if (!parsed.ok) {
    logActionResult({
      action: "uncompleteTodo",
      outcome: "error",
      errorCode: "INVALID_INPUT",
      durationMs: Date.now() - start,
      requestId,
    });
    return parsed;
  }

  const session = await resolveUser();
  if (!session.ok) {
    logActionResult({
      action: "uncompleteTodo",
      outcome: "error",
      errorCode: "UNAUTHENTICATED",
      durationMs: Date.now() - start,
      requestId,
    });
    return session.result;
  }

  const { userId, client } = session;
  const repo = makeRepo(client);

  const result = await repo.uncomplete({
    id: parsed.value.id,
    userId,
    expectedUpdatedAt: new Date(parsed.value.expectedUpdatedAt),
  });

  const durationMs = Date.now() - start;

  if (!result.ok) {
    logActionResult({
      action: "uncompleteTodo",
      outcome: "error",
      errorCode: result.error.code,
      userId,
      todoId: parsed.value.id,
      durationMs,
      requestId,
    });
    return result;
  }

  await writeTodoEvent({ kind: "uncomplete", actorUserId: userId, todoId: result.value.id });
  logActionResult({
    action: "uncompleteTodo",
    outcome: "success",
    userId,
    todoId: result.value.id,
    durationMs,
    requestId,
  });

  return result;
}

// ---------------------------------------------------------------------------
// deleteTodo (soft delete — A24)
// A8:  idempotent — re-delete returns existing deleted_at.
// A12: session required.
// A5:  userId from session.
// ---------------------------------------------------------------------------

export async function deleteTodo(input: unknown): Promise<Result<{ deletedAt: string }>> {
  const start = Date.now();
  const requestId = await getRequestId();

  const parsed = safeParse(DeleteTodoInputSchema, input);
  if (!parsed.ok) {
    logActionResult({
      action: "deleteTodo",
      outcome: "error",
      errorCode: "INVALID_INPUT",
      durationMs: Date.now() - start,
      requestId,
    });
    return parsed;
  }

  const session = await resolveUser();
  if (!session.ok) {
    logActionResult({
      action: "deleteTodo",
      outcome: "error",
      errorCode: "UNAUTHENTICATED",
      durationMs: Date.now() - start,
      requestId,
    });
    return session.result;
  }

  const { userId, client } = session;
  const repo = makeRepo(client);

  const result = await repo.softDelete({ id: parsed.value.id, userId });
  const durationMs = Date.now() - start;

  if (!result.ok) {
    logActionResult({
      action: "deleteTodo",
      outcome: "error",
      errorCode: result.error.code,
      userId,
      todoId: parsed.value.id,
      durationMs,
      requestId,
    });
    return result;
  }

  await writeTodoEvent({ kind: "delete", actorUserId: userId, todoId: parsed.value.id });
  logActionResult({
    action: "deleteTodo",
    outcome: "success",
    userId,
    todoId: parsed.value.id,
    durationMs,
    requestId,
  });

  // Return ISO string so it's serializable across the server/client boundary
  return { ok: true, value: { deletedAt: result.value.deletedAt.toISOString() } };
}

// signOutAndRedirect has been moved to src/app/actions/auth.ts
// (Phase 4 risk #4 fix — auth actions belong in the auth module)
