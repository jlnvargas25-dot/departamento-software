/**
 * Next.js middleware: session refresh + protected route enforcement
 *
 * Required by @supabase/ssr: every request must pass through this middleware
 * so that session cookies are refreshed before Server Components read them.
 * Without this, sessions expire silently mid-browse (A12 zero-trust violation).
 *
 * Protected routes: /todos and any sub-path — redirect to /sign-in if no session.
 * Public routes: /sign-in, /sign-up, /magic-link, /auth/callback — always allowed.
 *
 * A12: never trust the presence of a cookie alone — always call getUser() which
 *      validates the JWT server-side (not just checks cookie existence).
 * A22: uses anon key only; service-role never touched in middleware.
 *
 * Ref: https://supabase.com/docs/guides/auth/server-side/nextjs
 */

import { type NextRequest, NextResponse } from "next/server";
import { createServerClient } from "@supabase/ssr";

// ---------------------------------------------------------------------------
// Route classification
// ---------------------------------------------------------------------------

/** Routes that are always public — no session required. */
const PUBLIC_PREFIXES = [
  "/sign-in",
  "/sign-up",
  "/magic-link",
  "/auth",        // covers /auth/callback for magic-link redemption
  "/_next",       // Next.js internals
  "/favicon.ico",
  "/api/health",  // health check (if added)
];

function isPublicRoute(pathname: string): boolean {
  return PUBLIC_PREFIXES.some((prefix) => pathname.startsWith(prefix));
}

// ---------------------------------------------------------------------------
// Middleware
// ---------------------------------------------------------------------------

export async function middleware(request: NextRequest): Promise<NextResponse> {
  // OBS-3: generate a per-request correlation ID so logs across middleware,
  // server actions, and edge functions can be joined by a single field.
  const requestId = request.headers.get("x-request-id") ?? crypto.randomUUID();

  // Clone headers so we can inject x-request-id before passing downstream.
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-request-id", requestId);

  let response = NextResponse.next({
    request: { headers: requestHeaders },
  });

  const supabaseUrl = process.env["NEXT_PUBLIC_SUPABASE_URL"];
  const supabaseAnonKey = process.env["NEXT_PUBLIC_SUPABASE_ANON_KEY"];

  // A22: fail-open (allow request) if env vars missing — prevents hard crash in
  // middleware context; server actions will fail-fast independently.
  if (!supabaseUrl || !supabaseAnonKey) {
    response.headers.set("x-request-id", requestId);
    return response;
  }

  // Create a Supabase client that can read AND write cookies from middleware.
  // This is the pattern required by @supabase/ssr for cookie refresh.
  const supabase = createServerClient(supabaseUrl, supabaseAnonKey, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet) {
        // Write cookies to both the outgoing request and the response
        cookiesToSet.forEach(({ name, value }) =>
          request.cookies.set(name, value),
        );
        response = NextResponse.next({
          request: { headers: request.headers },
        });
        cookiesToSet.forEach(({ name, value, options }) =>
          response.cookies.set(name, value, options),
        );
      },
    },
  });

  // A12: validate session by calling getUser() — this triggers a token refresh
  // if needed and validates the JWT signature server-side (not just presence).
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const { pathname } = request.nextUrl;

  // Redirect unauthenticated users away from protected routes
  if (!user && !isPublicRoute(pathname)) {
    const signInUrl = request.nextUrl.clone();
    signInUrl.pathname = "/sign-in";
    // Preserve the intended destination for post-login redirect
    signInUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(signInUrl);
  }

  // Redirect authenticated users away from auth pages (avoid sign-in loop)
  if (user && (pathname === "/sign-in" || pathname === "/sign-up" || pathname === "/magic-link")) {
    const todosUrl = request.nextUrl.clone();
    todosUrl.pathname = "/todos";
    todosUrl.search = "";
    return NextResponse.redirect(todosUrl);
  }

  // Redirect root to todos (authenticated) or sign-in (anonymous)
  if (pathname === "/") {
    const dest = request.nextUrl.clone();
    dest.pathname = user ? "/todos" : "/sign-in";
    dest.search = "";
    return NextResponse.redirect(dest);
  }

  // OBS-3: echo correlation ID on every response for client-side debugging
  response.headers.set("x-request-id", requestId);
  return response;
}

// ---------------------------------------------------------------------------
// Matcher — run middleware on all routes except static assets
// ---------------------------------------------------------------------------

export const config = {
  matcher: [
    /*
     * Match all request paths EXCEPT:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico
     * - Public file extensions (images, fonts, etc.)
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
