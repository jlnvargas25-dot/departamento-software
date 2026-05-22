/**
 * Supabase client adapters (A11 DAO, A12 zero-trust, A22 secrets).
 *
 * Two clients — intentionally separate:
 *
 * 1. createServerClient() — cookie-based, uses anon key, for Server Components
 *    and Server Actions. Supabase Auth session is read from cookies and
 *    refreshed automatically by @supabase/ssr. NEVER uses service-role key.
 *
 * 2. createBrowserClient() — browser singleton, uses anon key only.
 *    Safe to call in Client Components. RLS enforces isolation (A5).
 *
 * 3. createServiceRoleClient() — admin client for server-only writes that
 *    must bypass RLS (e.g. auth_events inserts from auth server actions).
 *    MUST NEVER be called from client code. Guarded by server-only import.
 *
 * A22: SUPABASE_SERVICE_ROLE_KEY is accessed only here, only on the server.
 *      It is never prefixed NEXT_PUBLIC_ and never returned to the browser.
 */

import { createServerClient as _createServerClient } from "@supabase/ssr";
import { createBrowserClient as _createBrowserClient } from "@supabase/ssr";
import { createClient } from "@supabase/supabase-js";
import type { SupabaseClient } from "@supabase/supabase-js";
import type { cookies } from "next/headers";

// -------------------------------------------------------
// Environment variable helpers (A22: fail-fast if missing)
// -------------------------------------------------------

export function requireEnv(key: string): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(
      `[A22] Missing required environment variable: ${key}. ` +
        `Copy .env.example to .env.local and fill in the value.`,
    );
  }
  return value;
}

// -------------------------------------------------------
// 1. Server client — cookie-based, for Server Components + Actions
// -------------------------------------------------------

/**
 * Creates a Supabase client that reads/writes the user's session from
 * Next.js cookies. Required by @supabase/ssr for App Router.
 *
 * @param cookieStore - awaited result of `cookies()` from next/headers
 *
 * Usage in server action:
 *   import { cookies } from 'next/headers';
 *   const cookieStore = await cookies();
 *   const supabase = createServerClient(cookieStore);
 */
export function createServerClient(
  cookieStore: Awaited<ReturnType<typeof cookies>>,
): SupabaseClient {
  const supabaseUrl = requireEnv("NEXT_PUBLIC_SUPABASE_URL");
  const supabaseAnonKey = requireEnv("NEXT_PUBLIC_SUPABASE_ANON_KEY");

  return _createServerClient(supabaseUrl, supabaseAnonKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) => {
            cookieStore.set(name, value, options);
          });
        } catch (e) {
          // setAll called from Server Component (read-only context) — safe to ignore.
          // The middleware handles session refresh for these cases.
          // console.warn used here per ADR-SB-003 (pino not safe in isomorphic adapter context).
          if (typeof window === "undefined") {
            console.warn(
              "[supabase/client] setAll: cookie write skipped in read-only Server Component context",
              e instanceof Error ? e.message : String(e),
            );
          }
        }
      },
    },
  });
}

// -------------------------------------------------------
// 2. Browser client — singleton, anon key only (A22)
// -------------------------------------------------------

let _browserClientInstance: SupabaseClient | null = null;

/**
 * Returns a singleton Supabase browser client.
 * Safe for Client Components. Uses anon key — RLS enforces isolation (A5).
 * A22: never passes service-role key to this client.
 */
export function createBrowserClient(): SupabaseClient {
  if (_browserClientInstance) return _browserClientInstance;

  const supabaseUrl = requireEnv("NEXT_PUBLIC_SUPABASE_URL");
  const supabaseAnonKey = requireEnv("NEXT_PUBLIC_SUPABASE_ANON_KEY");

  _browserClientInstance = _createBrowserClient(supabaseUrl, supabaseAnonKey);
  return _browserClientInstance;
}

// -------------------------------------------------------
// 3. Service-role client — SERVER ONLY (A22 CRITICA)
// -------------------------------------------------------

/**
 * Admin client that bypasses RLS.
 * USE ONLY for:
 *   - auth_events INSERT (service-role inserts per data-model.md)
 *   - account hard-delete cascade
 *
 * NEVER call from Client Components or any code reachable from the browser.
 * A22: SUPABASE_SERVICE_ROLE_KEY never leaves the server boundary.
 */
export function createServiceRoleClient(): SupabaseClient {
  const supabaseUrl = requireEnv("NEXT_PUBLIC_SUPABASE_URL");
  const serviceRoleKey = requireEnv("SUPABASE_SERVICE_ROLE_KEY");

  return createClient(supabaseUrl, serviceRoleKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });
}
