#!/usr/bin/env node
/**
 * console_to_logger.js — codemod ts-morph (S-6.2).
 *
 * Rule_id: A21-OBS-1-CONSOLE-LOG
 * Pattern: console.{log,error,warn,info}(...) en codigo Node (NO Deno Edge Functions).
 * Transformation:
 *   - console.log(...)   -> logger.info(...)
 *   - console.error(...) -> logger.error(...)
 *   - console.warn(...)  -> logger.warn(...)
 *   - console.info(...)  -> logger.info(...)
 *   - inject `import { logger } from "@/lib/logger"` si no existe
 *
 * Modes:
 *   - apply (default): aplica + guarda + exit 0
 *   - --verify: cuenta calls, exit 0 si == 0, exit 1 si persiste
 *
 * Scope: NO aplica en files bajo `supabase/functions/` (esos van por
 * console_to_json_structured.js). Detection via path heuristica.
 */

const { Project, SyntaxKind } = require("ts-morph");
const path = require("path");

const CONSOLE_METHODS = new Set(["log", "error", "warn", "info"]);
const METHOD_MAPPING = { log: "info", error: "error", warn: "warn", info: "info" };
const LOGGER_IMPORT_MODULE = "@/lib/logger";

function usage() {
  process.stderr.write("usage: console_to_logger.js [--verify] <file>\n");
  process.exit(2);
}

function isInDenoEdgeFunctionsPath(filePath) {
  const normalized = filePath.replace(/\\/g, "/");
  return normalized.includes("/supabase/functions/");
}

function findConsoleCalls(sourceFile) {
  return sourceFile.getDescendantsOfKind(SyntaxKind.CallExpression).filter((call) => {
    if (call.wasForgotten()) return false;
    const expr = call.getExpression();
    if (!expr || expr.getKind() !== SyntaxKind.PropertyAccessExpression) return false;
    const obj = expr.getExpression();
    if (!obj || obj.getText() !== "console") return false;
    return CONSOLE_METHODS.has(expr.getName());
  });
}

function hasLoggerImport(sourceFile) {
  return sourceFile.getImportDeclarations().some((imp) =>
    imp.getNamedImports().some((spec) => spec.getName() === "logger")
  );
}

function main() {
  const args = process.argv.slice(2);
  let verifyMode = false;
  let target = null;
  for (const arg of args) {
    if (arg === "--verify") verifyMode = true;
    else if (!target) target = arg;
    else usage();
  }
  if (!target) usage();

  // Scope guard: NO aplica en Deno Edge Functions
  if (isInDenoEdgeFunctionsPath(target)) {
    if (verifyMode) {
      process.exit(0); // out of scope - considered "verified" (other codemod handles)
    }
    process.stderr.write("file in supabase/functions/ - out of scope (use console_to_json_structured)\n");
    process.exit(0); // no-op, not an error
  }

  const project = new Project({ skipAddingFilesFromTsConfig: true });
  let sourceFile;
  try {
    sourceFile = project.addSourceFileAtPath(target);
  } catch (err) {
    process.stderr.write(`failed to read ${target}: ${err.message}\n`);
    process.exit(2);
  }

  const consoleCalls = findConsoleCalls(sourceFile);

  if (verifyMode) {
    if (consoleCalls.length === 0) {
      process.exit(0);
    }
    process.stderr.write(`${consoleCalls.length} console.{log,error,warn,info} call(s) still present\n`);
    process.exit(1);
  }

  // Apply mode
  let applied = 0;
  for (const call of consoleCalls) {
    if (call.wasForgotten()) continue;
    const expr = call.getExpression();
    const consoleMethod = expr.getName();
    const loggerMethod = METHOD_MAPPING[consoleMethod];
    expr.replaceWithText(`logger.${loggerMethod}`);
    applied++;
  }

  // Inject import if needed (post-replace para no afectar la posicion de los nodos)
  if (applied > 0 && !hasLoggerImport(sourceFile)) {
    sourceFile.insertImportDeclaration(0, {
      namedImports: ["logger"],
      moduleSpecifier: LOGGER_IMPORT_MODULE,
    });
  }

  sourceFile.saveSync();

  const remaining = findConsoleCalls(sourceFile).length;
  process.stdout.write(`applied=${applied} remaining=${remaining}\n`);
  process.exit(0);
}

main();
