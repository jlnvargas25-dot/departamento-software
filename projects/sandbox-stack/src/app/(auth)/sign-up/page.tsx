/**
 * Sign-up page
 *
 * Server Component shell + Client Component form.
 * Posts to signUp server action.
 *
 * A5: on duplicate email, server returns ok (anti-enumeration) — UI shows
 *     "check your email" regardless, same as a genuine sign-up.
 * A14: errors displayed as user-safe messages, no internals exposed.
 */

import SignUpForm from "./sign-up-form";

export const metadata = {
  title: "Create account",
};

export default function SignUpPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-gray-900">Create account</h1>
          <p className="mt-1 text-sm text-gray-500">
            Get started with a free account.
          </p>
        </div>
        <SignUpForm />
        <p className="text-center text-sm text-gray-500">
          Already have an account?{" "}
          <a href="/sign-in" className="text-blue-600 hover:underline">
            Sign in
          </a>
        </p>
      </div>
    </main>
  );
}
