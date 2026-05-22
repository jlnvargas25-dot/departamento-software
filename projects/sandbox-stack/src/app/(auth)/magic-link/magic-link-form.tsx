/**
 * Magic-link request client form component.
 *
 * A5: success response is always "check your email" — same copy whether the
 *     email exists or not (anti-enumeration per requestMagicLink contract).
 * A14: errors displayed as user-safe messages.
 */

"use client";

import { useActionState } from "react";
import { requestMagicLink } from "@/app/actions/auth";
import type { Result } from "@/lib/result";
import type { RequestMagicLinkResult } from "@/domain/ports/auth-provider";

const ERROR_MESSAGES: Record<string, string> = {
  INVALID_INPUT: "Please enter a valid email address.",
  RATE_LIMITED: "Too many requests. Please wait before requesting another link.",
  INTERNAL: "Something went wrong. Please try again.",
};

type FormState = { result: Result<RequestMagicLinkResult> | null };

async function magicLinkAction(
  _prev: FormState,
  formData: FormData,
): Promise<FormState> {
  const email = formData.get("email") as string;
  const result = await requestMagicLink({ email });
  return { result };
}

export default function MagicLinkForm() {
  const [state, formAction, isPending] = useActionState(magicLinkAction, {
    result: null,
  });

  const isSuccess = state.result?.ok === true;
  const errorCode =
    state.result && !state.result.ok ? state.result.error.code : null;

  if (isSuccess) {
    return (
      <div
        role="status"
        className="rounded-md border border-green-200 bg-green-50 px-4 py-4 text-sm text-green-800"
      >
        <p className="font-medium">Check your email</p>
        <p className="mt-1 text-green-700">
          If this email is registered, a sign-in link has been sent. It expires
          in 1 hour and can only be used once.
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
          {ERROR_MESSAGES[errorCode] ?? "Something went wrong. Please try again."}
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

      <button
        type="submit"
        disabled={isPending}
        className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isPending ? "Sending link…" : "Send magic link"}
      </button>
    </form>
  );
}
