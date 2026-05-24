// Fixture: A21-OBS-1-CONSOLE-LOG (Node, no Deno)

import { fetchSomething } from "./api";

// NOTA fixture: el codemod console_to_logger.ts debe inyectar
// `import { logger } from "@/lib/logger";` si no existe (S-6).

export async function handleRequest(reqId: string) {
  // A21-OBS-1-CONSOLE-LOG violation
  console.log("processing request", reqId);
  try {
    const result = await fetchSomething();
    // A21-OBS-1-CONSOLE-LOG violation
    console.info("got result", result);
    return result;
  } catch (err) {
    // A21-OBS-1-CONSOLE-LOG violation
    console.error("request failed", err);
    throw err;
  }
}

export function warn() {
  // A21-OBS-1-CONSOLE-LOG violation
  console.warn("deprecated path used");
}
