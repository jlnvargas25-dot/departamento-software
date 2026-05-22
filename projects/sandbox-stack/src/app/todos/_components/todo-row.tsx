/**
 * TodoRow (Client Component)
 *
 * Renders a single todo with:
 *   - Completion toggle (checkbox) → completeTodo / uncompleteTodo
 *   - Edit-in-place (click text or "Edit" button) → updateTodo
 *   - Delete with confirmation → deleteTodo (soft delete, A24)
 *   - STALE_VERSION warning without silent loss (A13)
 *
 * A8:  toggle is idempotent — duplicate clicks are safe.
 * A13: passes todo.updatedAt as expectedUpdatedAt; on STALE_VERSION shows
 *      "This todo was updated elsewhere — refresh" without silent loss.
 * A14: all server action errors surface inline; nothing thrown.
 * A24: delete is soft — row disappears from active list but is recoverable.
 */

"use client";

import { useState, useTransition, useRef } from "react";
import {
  completeTodo,
  uncompleteTodo,
  updateTodo,
  deleteTodo,
} from "@/app/actions/todos";
import type { Todo } from "@/domain/todo";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(date: Date | string | null): string {
  if (!date) return "";
  const d = date instanceof Date ? date : new Date(date);
  return d.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface TodoRowProps {
  todo: Todo;
  onUpdated: (updated: Todo) => void;
  onDeleted: (id: string) => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function TodoRow({ todo, onUpdated, onDeleted }: TodoRowProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(todo.text);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const editInputRef = useRef<HTMLInputElement>(null);

  // -------------------------------------------------------------------------
  // Toggle complete / uncomplete
  // A8: idempotent — double-click safe
  // A13: pass updatedAt as concurrency token
  // -------------------------------------------------------------------------

  function handleToggleComplete() {
    setError(null);
    startTransition(async () => {
      const expectedUpdatedAt = (todo.updatedAt instanceof Date
        ? todo.updatedAt
        : new Date(todo.updatedAt)
      ).toISOString();

      const result = todo.completedAt
        ? await uncompleteTodo({ id: todo.id, expectedUpdatedAt })
        : await completeTodo({ id: todo.id, expectedUpdatedAt });

      if (!result.ok) {
        if (result.error.code === "STALE_VERSION") {
          // A13: warn without silent loss
          setError("This todo was updated elsewhere — refresh to see the latest version.");
        } else {
          setError(result.error.message);
        }
        return;
      }

      onUpdated(result.value);
    });
  }

  // -------------------------------------------------------------------------
  // Edit-in-place
  // -------------------------------------------------------------------------

  function handleEditStart() {
    setEditText(todo.text);
    setIsEditing(true);
    setError(null);
    // Focus the input after render
    setTimeout(() => editInputRef.current?.focus(), 0);
  }

  function handleEditCancel() {
    setIsEditing(false);
    setEditText(todo.text);
    setError(null);
  }

  function handleEditSave() {
    const trimmed = editText.trim();

    // Client-side mirror validation (A11)
    if (trimmed.length === 0) {
      setError("Todo text cannot be empty.");
      return;
    }
    if (trimmed.length > 1000) {
      setError("Todo text must be 1000 characters or fewer.");
      return;
    }

    setError(null);
    startTransition(async () => {
      const expectedUpdatedAt = (todo.updatedAt instanceof Date
        ? todo.updatedAt
        : new Date(todo.updatedAt)
      ).toISOString();

      const result = await updateTodo({
        id: todo.id,
        text: trimmed,
        expectedUpdatedAt,
      });

      if (!result.ok) {
        if (result.error.code === "STALE_VERSION") {
          // A13: STALE_VERSION → warn without silent loss
          setError(
            "This todo was updated elsewhere — refresh to see the latest version.",
          );
        } else {
          setError(result.error.message);
        }
        return;
      }

      setIsEditing(false);
      onUpdated(result.value);
    });
  }

  // -------------------------------------------------------------------------
  // Soft delete (A24)
  // -------------------------------------------------------------------------

  function handleDelete() {
    setError(null);
    startTransition(async () => {
      const result = await deleteTodo({ id: todo.id });

      if (!result.ok) {
        setError(result.error.message);
        setShowDeleteConfirm(false);
        return;
      }

      onDeleted(todo.id);
    });
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  const isCompleted = todo.completedAt !== null;

  return (
    <div
      data-testid="todo-row"
      className={`group rounded-lg border bg-white px-4 py-3 shadow-sm transition-opacity ${
        isPending ? "opacity-60" : ""
      } ${isCompleted ? "border-gray-200" : "border-gray-200"}`}
    >
      <div className="flex items-start gap-3">
        {/* Completion checkbox (A8: idempotent toggle) */}
        <input
          type="checkbox"
          checked={isCompleted}
          onChange={handleToggleComplete}
          disabled={isPending}
          aria-label={isCompleted ? "Mark as incomplete" : "Mark as complete"}
          className="mt-0.5 h-4 w-4 cursor-pointer rounded border-gray-300 text-blue-600
                     focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed"
        />

        {/* Main content */}
        <div className="min-w-0 flex-1">
          {isEditing ? (
            /* Edit mode */
            <div className="flex flex-col gap-2">
              <input
                ref={editInputRef}
                type="text"
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                maxLength={1000}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleEditSave();
                  if (e.key === "Escape") handleEditCancel();
                }}
                disabled={isPending}
                className="w-full rounded-md border border-blue-400 px-2 py-1 text-sm
                           focus:outline-none focus:ring-1 focus:ring-blue-500
                           disabled:opacity-50"
              />
              <div className="flex gap-2">
                <button
                  onClick={handleEditSave}
                  disabled={isPending}
                  className="rounded px-3 py-1 text-xs font-medium bg-blue-600 text-white
                             hover:bg-blue-700 disabled:opacity-50"
                >
                  {isPending ? "Saving…" : "Save"}
                </button>
                <button
                  onClick={handleEditCancel}
                  disabled={isPending}
                  className="rounded px-3 py-1 text-xs font-medium text-gray-600
                             hover:bg-gray-100 disabled:opacity-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            /* View mode */
            <div>
              <p
                className={`text-sm break-words ${
                  isCompleted
                    ? "line-through text-gray-400"
                    : "text-gray-800"
                }`}
              >
                {todo.text}
              </p>

              {/* Timestamps */}
              <div className="mt-1 flex flex-wrap gap-x-3 text-xs text-gray-400">
                <span>
                  Created {formatDate(todo.createdAt)}
                </span>
                {isCompleted && todo.completedAt && (
                  <span>
                    Completed {formatDate(todo.completedAt)}
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Inline error (STALE_VERSION + other errors — A13, A14) */}
          {error && (
            <p
              role="alert"
              aria-live="polite"
              className="mt-1.5 text-xs text-red-600"
            >
              {error}
            </p>
          )}
        </div>

        {/* Action buttons (hidden until row hover for clean UI) */}
        {!isEditing && (
          <div className="flex shrink-0 gap-1 opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100">
            <button
              onClick={handleEditStart}
              disabled={isPending}
              aria-label="Edit todo"
              className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600
                         disabled:opacity-50"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 16 16"
                fill="currentColor"
                className="h-3.5 w-3.5"
              >
                <path d="M13.488 2.513a1.75 1.75 0 0 0-2.475 0L6.75 6.774a2.75 2.75 0 0 0-.596.892l-.583 1.75a.75.75 0 0 0 .95.95l1.75-.583a2.75 2.75 0 0 0 .892-.596l4.262-4.263a1.75 1.75 0 0 0 0-2.475ZM3 3.75A1.75 1.75 0 0 0 1.25 5.5v7.5c0 .966.784 1.75 1.75 1.75h7.5A1.75 1.75 0 0 0 12.25 13v-3a.75.75 0 0 0-1.5 0v3a.25.25 0 0 1-.25.25h-7.5a.25.25 0 0 1-.25-.25v-7.5a.25.25 0 0 1 .25-.25h3a.75.75 0 0 0 0-1.5H3Z" />
              </svg>
            </button>

            {/* Delete with confirm */}
            {showDeleteConfirm ? (
              <div className="flex gap-1">
                <button
                  onClick={handleDelete}
                  disabled={isPending}
                  aria-label="Confirm delete"
                  className="rounded px-2 py-1 text-xs font-medium bg-red-600 text-white
                             hover:bg-red-700 disabled:opacity-50"
                >
                  {isPending ? "…" : "Yes"}
                </button>
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  disabled={isPending}
                  aria-label="Cancel delete"
                  className="rounded px-2 py-1 text-xs font-medium text-gray-600
                             hover:bg-gray-100 disabled:opacity-50"
                >
                  No
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowDeleteConfirm(true)}
                disabled={isPending}
                aria-label="Delete todo"
                className="rounded p-1 text-gray-400 hover:bg-red-50 hover:text-red-500
                           disabled:opacity-50"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 16 16"
                  fill="currentColor"
                  className="h-3.5 w-3.5"
                >
                  <path
                    fillRule="evenodd"
                    d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Zm2.25-.75a.75.75 0 0 0-.75.75V4h3v-.75a.75.75 0 0 0-.75-.75h-1.5ZM6.05 6a.75.75 0 0 1 .787.713l.275 5.5a.75.75 0 0 1-1.498.075l-.275-5.5A.75.75 0 0 1 6.05 6Zm3.9 0a.75.75 0 0 1 .712.787l-.275 5.5a.75.75 0 0 1-1.498-.075l.275-5.5A.75.75 0 0 1 9.95 6Z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
