/**
 * Sign-in page
 *
 * Server Component shell + Client Component form.
 * Posts to signInWithPassword server action.
 *
 * A14: displays Result error code as user-safe message (no stack traces).
 * A5:  generic error copy — no field disclosure (FR-005 anti-enumeration).
 * A21: no PII in page title or visible text.
 */

import SignInForm from "./sign-in-form";

export const metadata = {
  title: "Sign in",
};

export default function SignInPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-gray-900">Sign in</h1>
          <p className="mt-1 text-sm text-gray-500">
            Welcome back. Enter your credentials to continue.
          </p>
        </div>
        <SignInForm />
        <p className="text-center text-sm text-gray-500">
          Don&apos;t have an account?{" "}
          <a href="/sign-up" className="text-blue-600 hover:underline">
            Sign up
          </a>
        </p>
      </div>
    </main>
  );
}
