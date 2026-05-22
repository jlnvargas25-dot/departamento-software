/**
 * Magic-link request page
 *
 * A5: always shows "check your email" on submit — never reveals if email exists.
 * A16: rate-limited at 5/h/IP in the server action.
 * A14: error codes mapped to user-safe messages.
 */

import MagicLinkForm from "./magic-link-form";

export const metadata = {
  title: "Sign in with magic link",
};

export default function MagicLinkPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-gray-900">
            Sign in with magic link
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Enter your email and we&apos;ll send you a one-time sign-in link.
          </p>
        </div>
        <MagicLinkForm />
        <p className="text-center text-sm text-gray-500">
          Prefer a password?{" "}
          <a href="/sign-in" className="text-blue-600 hover:underline">
            Sign in
          </a>
        </p>
      </div>
    </main>
  );
}
