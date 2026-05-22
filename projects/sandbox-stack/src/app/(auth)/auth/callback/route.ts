/**
 * Magic-link / OAuth callback route
 *
 * Supabase Auth sends the user to this URL after they click a magic link or
 * complete an OAuth flow. The route exchanges the `code` query param for a
 * session and writes it to cookies, then redirects to /todos.
 *
 * A12: code exchange happens server-side — access token never exposed to JS.
 * A22: uses server client (anon key); no service-role key needed here.
 * A6:  writes magic_link_redeemed event to auth_events for audit trail.
 *
 * Ref: https://supabase.com/docs/guides/auth/server-side/nextjs (PKCE flow)
 */

import { NextResponse, type NextRequest } from "next/server";
import { cookies } from "next/headers";
import { createServerClient } from "@/adapters/supabase/client";
import { createServiceRoleClient } from "@/adapters/supabase/client";
import { logger } from "@/adapters/logging/pino";

export async function GET(request: NextRequest): Promise<NextResponse> {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  // `next` param allows post-auth redirect to a specific page
  const next = searchParams.get("next") ?? "/todos";

  // Sanitise the redirect target — only allow relative paths (A12)
  const redirectTo = next.startsWith("/") ? next : "/todos";

  if (!code) {
    // No code — redirect to sign-in with error hint (but no internals)
    return NextResponse.redirect(`${origin}/sign-in?error=missing_code`);
  }

  const cookieStore = await cookies();
  const supabase = createServerClient(cookieStore);

  const { data, error } = await supabase.auth.exchangeCodeForSession(code);

  if (error || !data.session) {
    // Code invalid or expired — redirect to sign-in (A14: explicit failure)
    return NextResponse.redirect(`${origin}/sign-in?error=invalid_code`);
  }

  // A6: write audit event for magic-link redemption
  try {
    const serviceClient = createServiceRoleClient();
    await serviceClient.from("auth_events").insert({
      kind: "magic_link_redeemed",
      outcome: "ok",
      actor_user_id: data.session.user.id,
    });
  } catch (e) {
    // Non-fatal — audit write must not block the session establishment
    // G-3/G-6: structured log so infra has visibility
    logger.warn(
      { action: "callbackRoute", errorCode: "AUTH_EVENT_WRITE_FAILED", error: e instanceof Error ? e.message : String(e) },
      "callback: failed to insert magic_link_redeemed auth_events row (non-fatal)",
    );
  }

  // Redirect to app — session is now in cookies
  return NextResponse.redirect(`${origin}${redirectTo}`);
}
