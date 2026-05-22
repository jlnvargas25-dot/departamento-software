/**
 * TodoList (Client Component)
 *
 * Manages the local todo list state and composes TodoRow items.
 * Create is handled inline (TodoCreateFormRefreshable) to allow
 * the list to refresh after a successful create without prop-drilling.
 *
 * State management:
 *   - initialItems/initialNextCursor hydrated from Server Component (page.tsx)
 *   - createTodo → server action → refresh first page on success
 *   - updateTodo / completeTodo / uncompleteTodo → in-place replace via onUpdated
 *   - deleteTodo → filter out via onDeleted
 *   - Pagination: "Load more" fetches next cursor batch and appends
 *
 * A13: STALE_VERSION handled inside TodoRow — no silent loss.
 * A24: deleted items removed from local list immediately (soft-delete on server).
 * A14: listActiveTodos pagination errors shown inline.
 */

"use client";

import { useState, useTransition } from "react";
import type { Todo } from "@/domain/todo";
import { createTodo, listActiveTodos } from "@/app/actions/todos";
import { TodoRow } from "@/app/todos/_components/todo-row";

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface TodoListProps {
  initialItems: Todo[];
  initialNextCursor: string | null;
}

// ---------------------------------------------------------------------------
// TodoList
// ---------------------------------------------------------------------------

export function TodoList({ initialItems, initialNextCursor }: TodoListProps) {
  const [items, setItems] = useState<Todo[]>(initialItems);
  const [nextCursor, setNextCursor] = useState<string | null>(initialNextCursor);
  const [loadMoreError, setLoadMoreError] = useState<string | null>(null);
  const [isPaginating, startPagination] = useTransition();

  // -------------------------------------------------------------------------
  // Handlers passed down to TodoRow
  // -------------------------------------------------------------------------

  function handleTodoUpdated(updated: Todo) {
    setItems((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
  }

  function handleTodoDeleted(id: string) {
    setItems((prev) => prev.filter((t) => t.id !== id));
  }

  // -------------------------------------------------------------------------
  // Refresh list after successful create (re-fetches first page)
  // Gives correct newest-first ordering without complex optimistic state.
  // -------------------------------------------------------------------------

  async function handleRefreshAfterCreate() {
    const result = await listActiveTodos({ limit: 50 });
    if (result.ok) {
      setItems(result.value.items);
      setNextCursor(result.value.nextCursor);
    }
    // On fetch failure, existing items remain — no silent loss
  }

  // -------------------------------------------------------------------------
  // Pagination
  // -------------------------------------------------------------------------

  function handleLoadMore() {
    if (!nextCursor) return;
    setLoadMoreError(null);
    startPagination(async () => {
      const result = await listActiveTodos({ pageCursor: nextCursor, limit: 50 });
      if (!result.ok) {
        setLoadMoreError(result.error.message);
        return;
      }
      setItems((prev) => [...prev, ...result.value.items]);
      setNextCursor(result.value.nextCursor);
    });
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <div>
      {/* Inline create form — owns its own state, notifies list on success */}
      <TodoCreateInline onSuccess={handleRefreshAfterCreate} />

      {/* Count */}
      <p className="mb-3 text-xs text-gray-400">
        {items.length === 0
          ? "No active todos. Add one above!"
          : `${items.length} active todo${items.length === 1 ? "" : "s"}`}
      </p>

      {/* Todo items */}
      <ul className="flex flex-col gap-2" aria-label="Todo list">
        {items.map((todo) => (
          <li key={todo.id}>
            <TodoRow
              todo={todo}
              onUpdated={handleTodoUpdated}
              onDeleted={handleTodoDeleted}
            />
          </li>
        ))}
      </ul>

      {/* Pagination */}
      {nextCursor && (
        <div className="mt-4 text-center">
          <button
            onClick={handleLoadMore}
            disabled={isPaginating}
            className="rounded-md px-4 py-2 text-sm text-blue-600 hover:bg-blue-50
                       disabled:opacity-50 focus:outline-none focus:ring-2
                       focus:ring-blue-500 focus:ring-offset-1"
          >
            {isPaginating ? "Loading…" : "Load more"}
          </button>
          {loadMoreError && (
            <p role="alert" className="mt-1 text-xs text-red-600">
              {loadMoreError}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// TodoCreateInline — create form with controlled input + server action
// ---------------------------------------------------------------------------

const TODO_TEXT_MAX = 1000;

interface TodoCreateInlineProps {
  onSuccess: () => Promise<void>;
}

function TodoCreateInline({ onSuccess }: TodoCreateInlineProps) {
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);

    const trimmed = text.trim();

    // Client-side mirror validation (A11: mirrors schema.ts constraints)
    if (trimmed.length === 0) {
      setError("Todo text cannot be empty.");
      return;
    }
    if (trimmed.length > TODO_TEXT_MAX) {
      setError(`Todo text must be ${TODO_TEXT_MAX} characters or fewer.`);
      return;
    }

    startTransition(async () => {
      const result = await createTodo({ text: trimmed });
      if (!result.ok) {
        setError(result.error.message);
        return;
      }
      setText("");
      await onSuccess();
    });
  }

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      <div className="flex gap-2">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Add a todo…"
          maxLength={TODO_TEXT_MAX}
          disabled={isPending}
          autoComplete="off"
          aria-label="New todo text"
          className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm
                     placeholder:text-gray-400 focus:border-blue-500 focus:outline-none
                     focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={isPending}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white
                     hover:bg-blue-700 disabled:opacity-50 focus:outline-none
                     focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
        >
          {isPending ? "Adding…" : "Add"}
        </button>
      </div>

      {error && (
        <p role="alert" className="mt-1.5 text-sm text-red-600" aria-live="polite">
          {error}
        </p>
      )}
    </form>
  );
}
