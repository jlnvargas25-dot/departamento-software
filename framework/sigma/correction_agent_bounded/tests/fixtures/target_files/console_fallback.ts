import { logger } from "@/lib/logger";

export function logMessage(msg: string) {
  try {
    logger.info(msg);
  } catch {
    // Fallback when logger unavailable — should be behind feature flag
    console.warn(`Logger unavailable, fallback: ${msg}`);
  }
}
