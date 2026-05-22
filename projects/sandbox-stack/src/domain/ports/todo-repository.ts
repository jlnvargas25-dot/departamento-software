/**
 * Port: TodoRepository
 * A20: interface only — no IO, no Supabase imports.
 * A11: DAO pattern — adapter implements this in src/adapters/supabase/todo-repository.ts
 * A4: domain depends only on domain types; adapters depend on domain (no cycles).
 */

import type { Todo } from "@/domain/todo";
import type { Result } from "@/lib/result";
import type { DomainError } from "@/domain/errors";

export interface ListActiveTodosOptions {
  userId: string;
  pageCursor?: string;
  limit?: number; // default 50, max 100
}

export interface ListActiveTodosResult {
  items: Todo[];
  nextCursor: string | null;
}

export interface CreateTodoOptions {
  userId: string;
  text: string;
}

export interface UpdateTodoOptions {
  id: string;
  userId: string;
  text: string;
  expectedUpdatedAt: Date; // A13 optimistic concurrency token
}

export interface CompleteTodoOptions {
  id: string;
  userId: string;
  expectedUpdatedAt: Date;
}

export interface UncompleteTodoOptions {
  id: string;
  userId: string;
  expectedUpdatedAt: Date;
}

export interface SoftDeleteTodoOptions {
  id: string;
  userId: string;
}

/**
 * TodoRepository port.
 * Every method returns Result<T, DomainError> — never throws (A14).
 * All queries are scoped to userId; RLS enforces this at DB layer (A5).
 */
export interface TodoRepository {
  listActive(options: ListActiveTodosOptions): Promise<Result<ListActiveTodosResult>>;
  create(options: CreateTodoOptions): Promise<Result<Todo>>;
  update(options: UpdateTodoOptions): Promise<Result<Todo>>;
  complete(options: CompleteTodoOptions): Promise<Result<Todo>>;
  uncomplete(options: UncompleteTodoOptions): Promise<Result<Todo>>;
  softDelete(options: SoftDeleteTodoOptions): Promise<Result<{ deletedAt: Date }>>;
}

// Type alias for convenience in adapters
export type TodoRepositoryError = DomainError;
