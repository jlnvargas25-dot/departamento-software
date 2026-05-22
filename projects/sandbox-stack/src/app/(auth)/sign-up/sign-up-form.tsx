/**
 * Sign-up client form component.
 *
 * A5: on success (including duplicate email), shows "check your email" —
 *     never reveals whether the email was already registered.
 * A14: error codes mapped to user-safe messages.
 * A15: client-side validation mirrors server zod schemas to catch errors early.
 */

"use client";

import { useActionState } from "react";
import { signUp } from "@/app/actions/auth";
import type { Result } from "@/lib/result";
import type { SignUpResult } from "@/domain/ports/auth-provider";

const ERROR_MESSAGES: Record<string, string> = {
  INVALID_INPUT: "Please enter a valid email and a password with at least 8 characters including a number or symbol.",
  RATE_LIMITED: "Too many sign-up attempts. Please wait a moment before trying again.",
  INTERNAL: "Something went wrong. Please try again.",
};

function getErrorMessage(code: string): string {
  return ERROR_MESSAGES[code] ?? "Something went wrong. Please try again.";
}

type FormState = { result: Result<SignUpResult> | null };

async function signUpAction(
  _prev: FormState,
  formData: FormData,
): Promise<FormState> {
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;
  const result = await signUp({ email, password });
  return { result };
}

export default function SignUpForm() {
  const [state, formAction, isPending] = useActionState(signUpAction, {
    result: null,
  });

  const isSuccess = state.result?.ok === true;
  const errorCode =
    state.result && !state.result.ok ? state.result.error.code : null;

  // A5: same "check your email" shown for both new and duplicate emails
  if (isSuccess) {
    return (
      <div
        role="status"
        className="rounded-md border border-green-200 bg-green-50 px-4 py-4 text-sm text-green-800"
      >
        <p className="font-medium">Check your email</p>
        <p className="mt-1 text-green-700">
          If this email is valid, you&apos;ll receive a confirmation link shortly.
          Please check your inbox (and spam folder).
        </p>
      </div>
    );
  }

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
        />
      </div>

      <div className="space-y-1">
        <label
          htmlFor="password"
          className="block text-sm font-medium text-gray-700"
        >
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        <p className="text-xs text-gray-400">
          At least 8 characters with a number or symbol.
        </p>
      </div>

      <button
        type="submit"
        disabled={isPending}
        className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isPending ? "Creating account…" : "Create account"}
      </button>
    </form>
  );
}
