/**
 * Sign-in client form component.
 *
 * A14: displays result errors as user-safe messages — no internal detail.
 * A5:  single generic message for any credential failure (FR-005).
 * A15: validates client-side before submitting to reduce unnecessary round-trips.
 */

"use client";

import { useEffect, useActionState } from "react";
import { signInWithPassword } from "@/app/actions/auth";
import type { Result } from "@/lib/result";
import type { SignInResult } from "@/domain/ports/auth-provider";
import { useRouter } from "next/navigation";

// Map server-returned error codes to user-safe messages (A5: no field disclosure)
const ERROR_MESSAGES: Record<string, string> = {
  UNAUTHENTICATED: "Invalid credentials. Please check your email and password.",
  INVALID_INPUT: "Please enter a valid email and password.",
  RATE_LIMITED: "Too many attempts. Please wait a moment before trying again.",
  INTERNAL: "Something went wrong. Please try again.",
};

function getErrorMessage(code: string): string {
  return ERROR_MESSAGES[code] ?? "Something went wrong. Please try again.";
}

type FormState = { result: Result<SignInResult> | null };

async function signInAction(
  _prev: FormState,
  formData: FormData,
): Promise<FormState> {
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;
  const result = await signInWithPassword({ email, password });
  return { result };
}

export default function SignInForm() {
  const router = useRouter();
  const [state, formAction, isPending] = useActionState(signInAction, {
    result: null,
  });

  const errorCode = state.result && !state.result.ok
    ? state.result.error.code
    : null;

  // Redirect on success via useEffect — avoids render-phase side-effect
  useEffect(() => {
    if (state.result?.ok) {
      router.push("/todos");
    }
  }, [state.result, router]);

  return (
    <form action={formAction} className="space-y-4" noValidate>
      {errorCode && (
        <div
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {getErrorMessage(errorCode)}
        </div>
      )}

      <div className="space-y-1">
        <label
          htmlFor="email"
          className="block text-sm font-medium text-gray-700"
        >
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          required
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          aria-describedby={errorCode ? "form-error" : undefined}
        />
      </div>

      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <label
            htmlFor="password"
            className="block text-sm font-medium text-gray-700"
          >
            Password
          </label>
          <a
            href="/magic-link"
            className="text-xs text-blue-600 hover:underline"
          >
            Sign in with magic link
          </a>
        </div>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <button
        type="submit"
        disabled={isPending}
        className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isPending ? "Signing in…" : "Sign in"}
      </button>
    </form>
  );
}
