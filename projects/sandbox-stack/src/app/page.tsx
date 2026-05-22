/**
 * Root page — redirects authenticated users to /todos,
 * unauthenticated users to /sign-in.
 * A12: middleware handles the actual redirect; this is a fallback.
 */
import { redirect } from "next/navigation";

export default function Home(): never {
  // Middleware (src/middleware.ts) handles session-aware routing.
  // This page should never render in practice.
  redirect("/sign-in");
}
