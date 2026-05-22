/**
 * Structured logger adapter — pino (A21 observability).
 * Decision 9: redact email, password, *.token patterns (A22 secrets).
 * OBS-1: structured JSON logs to stdout (Vercel captures automatically).
 * OBS-2: every log entry includes action, outcome, duration_ms, user_id when available.
 * Never import this in client components — server-only.
 */

import pino from "pino";

const isDev = process.env["NODE_ENV"] === "development";

/**
 * Root logger instance.
 * In production: JSON to stdout (Vercel log drain picks it up).
 * In development: pretty-printed for readability.
 */
export const logger = pino({
  level: process.env["LOG_LEVEL"] ?? "info",

  // A22 + Decision 9: redact PII before any log line is written
  redact: {
    paths: [
      "email",
      "password",
      "*.email",
      "*.password",
      "*.token",
      "*.accessToken",
      "*.refreshToken",
      "*.apiKey",
      "req.headers.authorization",
      "req.headers.cookie",
    ],
    censor: "[REDACTED]",
  },

  // Vercel injects these; keep base object lean
  base: {
    env: process.env["NODE_ENV"] ?? "development",
  },

  // ISO timestamp on every line (OBS-1)
  timestamp: pino.stdTimeFunctions.isoTime,

  ...(isDev
    ? {
        transport: {
          target: "pino-pretty",
          options: { colorize: true, ignore: "pid,hostname" },
        },
      }
    : {}),
});

// -------------------------------------------------------
// Typed log context shapes (A21 OBS-2)
// -------------------------------------------------------

export interface ActionLogContext {
  action: string; // e.g. 'createTodo', 'signUp'
  userId?: string; // omit for unauthenticated failures
  todoId?: string;
  outcome: "success" | "error";
  errorCode?: string; // ErrorCode
  durationMs: number;
  requestId?: string; // x-request-id from middleware (OBS-3: cross-layer correlation)
}

export interface AuthLogContext {
  action: string; // e.g. 'signUp', 'signIn'
  outcome: "success" | "error";
  errorCode?: string;
  durationMs: number;
  // NOTE: userId only present on success (no PII on failure to avoid correlation)
  userId?: string;
}

/**
 * Scoped child logger for a single server action invocation.
 * Usage:
 *   const log = actionLogger('createTodo');
 *   log.info({ outcome: 'success', userId, todoId, durationMs }, 'createTodo ok');
 */
export function actionLogger(actionName: string): pino.Logger {
  return logger.child({ action: actionName });
}

/**
 * Log a completed action result in one call.
 * Centralizes the structured log shape for consistency (OBS-2).
 */
export function logActionResult(context: ActionLogContext): void {
  const { outcome, ...rest } = context;
  if (outcome === "success") {
    logger.info(rest, `${context.action} completed`);
  } else {
    logger.warn(rest, `${context.action} failed: ${context.errorCode ?? "unknown"}`);
  }
}
