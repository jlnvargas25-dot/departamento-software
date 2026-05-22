/**
 * LOGGING TRANSPORT DECISION (A21):
 * This Edge Function runs in the Deno runtime, which has no Node.js module
 * support. Pino and other Node-based structured loggers are unavailable here.
 * Per A21, structured observability is still required.
 *
 * Chosen approach: console.log(JSON.stringify({ level, msg, context }))
 * Rationale: Supabase Edge runtime forwards stdout to its log-drain as
 * newline-delimited JSON. The JSON envelope IS the structured layer — the
 * "level", "msg", and "context" fields satisfy A21's structured-log contract.
 * This is the idiomatic pattern for Deno Edge Functions (analogous to how
 * AWS Lambda treats stdout as the log transport).
 *
 * Formal exception: decisions/ADR-SB-002-edge-function-console-log-deno.md
 */

/**
 * T045 — Supabase Edge Function: purge-expired-todos
 *
 * Runs on a cron schedule to hard-delete soft-deleted todos older than 30 days.
 *
 * A24: soft-delete retention window = 30 days; this function enforces the boundary.
 * A6:  todo_events rows are NOT purged here — audit trail is immutable.
 * A22: uses SUPABASE_SERVICE_ROLE_KEY (injected by Supabase Edge runtime as
 *      built-in env var — never stored in source).
 *
 * Schedule (configured in supabase/config.toml):
 *   [functions.purge-expired-todos]
 *   schedule = "0 3 * * *"   # daily at 03:00 UTC
 *
 * Manual trigger:
 *   supabase functions invoke purge-expired-todos --local
 *
 * Or via psql (pg_cron alternative, see Decision 3 in research.md):
 *   select cron.schedule(
 *     'purge_soft_deleted_todos',
 *     '0 3 * * *',
 *     $$
 *       delete from public.todos
 *       where deleted_at is not null
 *         and deleted_at < now() - interval '30 days';
 *     $$
 *   );
 */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// Deno Edge Function entrypoint
Deno.serve(async (req: Request) => {
  // Authorization: Supabase Edge runtime calls this with the service role key
  // in the Authorization header when invoked via cron or CLI.
  // We also support a manual Bearer token check for direct invocations.
  const authHeader = req.headers.get("Authorization");
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return new Response(JSON.stringify({ error: "Missing authorization" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Use the built-in SUPABASE_URL + service-role key injected by the Edge runtime.
  // These env vars are set automatically by Supabase for Edge Functions.
  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

  if (!supabaseUrl || !serviceRoleKey) {
    return new Response(JSON.stringify({ error: "Runtime env vars not available" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }

  const supabase = createClient(supabaseUrl, serviceRoleKey, {
    auth: { persistSession: false },
  });

  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - 30);

  // Hard-delete todos where:
  //   1. deleted_at IS NOT NULL (soft-deleted)
  //   2. deleted_at < now() - 30 days (retention window expired)
  //
  // This does NOT touch todo_events — audit trail preserved per A6.
  const { data, error, count } = await supabase
    .from("todos")
    .delete({ count: "exact" })
    .lt("deleted_at", cutoff.toISOString())
    .not("deleted_at", "is", null);

  if (error) {
    console.log(
      JSON.stringify({
        level: "error",
        msg: "purge-expired-todos failed",
        context: { error: error.message, cutoff: cutoff.toISOString() },
      }),
    );
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }

  const result = {
    purged: count ?? 0,
    cutoff: cutoff.toISOString(),
    timestamp: new Date().toISOString(),
  };

  console.log(
    JSON.stringify({
      level: "info",
      msg: "purge-expired-todos completed",
      context: result,
    }),
  );

  return new Response(JSON.stringify(result), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
});
