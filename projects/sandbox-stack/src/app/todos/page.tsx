/**
 * Todos list page (Server Component)
 *
 * Fetches the active todo list server-side for the initial render.
 * A12: session guard — if listActiveTodos returns UNAUTHENTICATED, redirect to sign-in.
 *      Middleware also guards this route, but we double-check here (defense-in-depth).
 * A5:  listActiveTodos sources userId from getUser() inside the action — not from params.
 * A24: overflow flag surfaced to client component via nextCursor presence.
 */

import { redirect } from "next/navigation";
import { listActiveTodos } from "@/app/actions/todos";
import { signOutAndRedirect } from "@/app/actions/auth";
import { TodoList } from "@/app/todos/_components/todo-list";

export const dynamic = "force-dynamic"; // always SSR — no stale cache for personal data

export default async function TodosPage() {
  const result = await listActiveTodos({ limit: 50 });

  // A12: unauthenticated → redirect (middleware should have caught this first)
  if (!result.ok && result.error.code === "UNAUTHENTICATED") {
    redirect("/sign-in");
  }

  const items = result.ok ? result.value.items : [];
  const nextCursor = result.ok ? result.value.nextCursor : null;
  const serverError = result.ok ? null : result.error.message;

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-2xl px-4 py-10">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">My Todos</h1>
          <form action={signOutAndRedirect}>
            <button
              type="submit"
              className="rounded-md px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100"
            >
              Sign out
            </button>
          </form>
        </div>

        {/* Server-side error (non-auth) */}
        {serverError && (
          <div
            role="alert"
            className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {serverError}
          </div>
        )}

        {/* Client component handles create + CRUD interactions */}
        <TodoList
          initialItems={items}
          initialNextCursor={nextCursor}
        />
      </div>
    </main>
  );
}
