/**
 * Zod schemas — DTOs for all server action inputs (A11 DAO+DTO).
 * A3: typed contracts at every server-action boundary.
 * A14: validation failure returns INVALID_INPUT, never throws.
 * Mirrors DB constraints from data-model.md (1-1000 chars, valid email, etc.)
 */

import { z } from "zod";

// -------------------------------------------------------
// Primitives
// -------------------------------------------------------

const uuidSchema = z.string().uuid({ message: "Must be a valid UUID." });

const emailSchema = z
  .string()
  .min(1, "Email is required.")
  .max(256, "Email must be 256 characters or fewer.")
  .email("Must be a valid email address.");

const passwordSchema = z
  .string()
  .min(8, "Password must be at least 8 characters.")
  .max(256, "Password must be 256 characters or fewer.")
  .refine(
    (p) => /[\d!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(p),
    "Password must contain at least one number or symbol.",
  );

const todoTextSchema = z
  .string()
  .trim()
  .min(1, "Todo text cannot be empty.")
  .max(1000, "Todo text must be 1000 characters or fewer.");

const isoDateSchema = z
  .string()
  .datetime({ message: "Must be a valid ISO-8601 datetime string." });

const pageCursorSchema = z.string().optional();

const limitSchema = z
  .number()
  .int()
  .min(1)
  .max(100)
  .optional()
  .default(50);

// -------------------------------------------------------
// Auth action inputs
// -------------------------------------------------------

export const SignUpInputSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
});
export type SignUpInput = z.infer<typeof SignUpInputSchema>;

export const SignInWithPasswordInputSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, "Password is required."), // no complexity check on sign-in
});
export type SignInWithPasswordInput = z.infer<typeof SignInWithPasswordInputSchema>;

export const RequestMagicLinkInputSchema = z.object({
  email: emailSchema,
});
export type RequestMagicLinkInput = z.infer<typeof RequestMagicLinkInputSchema>;

// signOut and deleteAccount take no input — no schema needed

// -------------------------------------------------------
// Todo action inputs
// -------------------------------------------------------

export const CreateTodoInputSchema = z.object({
  text: todoTextSchema,
});
export type CreateTodoInput = z.infer<typeof CreateTodoInputSchema>;

export const ListActiveTodosInputSchema = z.object({
  pageCursor: pageCursorSchema,
  limit: limitSchema,
});
export type ListActiveTodosInput = z.infer<typeof ListActiveTodosInputSchema>;

export const UpdateTodoInputSchema = z.object({
  id: uuidSchema,
  text: todoTextSchema,
  expectedUpdatedAt: isoDateSchema, // A13 optimistic concurrency token
});
export type UpdateTodoInput = z.infer<typeof UpdateTodoInputSchema>;

export const CompleteTodoInputSchema = z.object({
  id: uuidSchema,
  expectedUpdatedAt: isoDateSchema,
});
export type CompleteTodoInput = z.infer<typeof CompleteTodoInputSchema>;

export const UncompleteTodoInputSchema = z.object({
  id: uuidSchema,
  expectedUpdatedAt: isoDateSchema,
});
export type UncompleteTodoInput = z.infer<typeof UncompleteTodoInputSchema>;

export const DeleteTodoInputSchema = z.object({
  id: uuidSchema,
});
export type DeleteTodoInput = z.infer<typeof DeleteTodoInputSchema>;

// -------------------------------------------------------
// Parse helper — returns Result-compatible shape
// -------------------------------------------------------

import { err, ok } from "@/lib/result";
import { Errors } from "@/domain/errors";
import type { Result } from "@/lib/result";

/**
 * Safely parse a zod schema. Returns Result<T> so callers
 * can return INVALID_INPUT without throwing (A14).
 */
export function safeParse<T>(
  schema: z.ZodType<T>,
  data: unknown,
): Result<T> {
  const parsed = schema.safeParse(data);
  if (!parsed.success) {
    const message = parsed.error.issues
      .map((i) => i.message)
      .join("; ");
    return err(Errors.invalidInput(message));
  }
  return ok(parsed.data);
}
