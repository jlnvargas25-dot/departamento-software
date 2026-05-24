#!/usr/bin/env node
/**
 * console_to_json_structured.js — codemod ts-morph (S-6.3).
 *
 * Rule_id: A21-OBS-1b-DENO-CONSOLE
 * Scope: SOLO aplica en files bajo `supabase/functions/` (Deno Edge Functions).
 *
 * Pattern: console.{log,error,warn,info}(...) en Edge Functions Deno.
 * Transformation:
 *   - console.log(msg)        -> console.log(JSON.stringify({ level: "info", msg }))
 *   - console.error(err, ctx) -> console.log(JSON.stringify({ level: "error", err: serializeErr(err), ctx }))
 *   - console.warn(msg)       -> console.log(JSON.stringify({ level: "warn", msg }))
 *   - console.info(msg)       -> console.log(JSON.stringify({ level: "info", msg }))
 *   - inject helper `serializeErr` inline en el top del file si hay calls error
 *
 * R08 audit Paso 5 CERRADA: serializeErr helper inline aca (no en archivo
 * compartido para mantener atomicidad por-file).
 *
 * Idempotencia: detecta calls que ya estan envueltas con JSON.stringify({level:...})
 * y las skipea (no-op).
 */

const { Project, SyntaxKind } = require("ts-morph");

const CONSOLE_METHODS = new Set(["log", "error", "warn", "info"]);
const LEVEL_MAPPING = { log: "info", error: "error", warn: "warn", info: "info" };
const SERIALIZE_ERR_HELPER = `
function serializeErr(err) {
  if (err instanceof Error) {
    return { name: err.name, message: err.message, stack: err.stack };
  }
  return err;
}
`.trim();

function usage() {
  process.stderr.write("usage: console_to_json_structured.js [--verify] <file>\n");
  process.exit(2);
}

function isInDenoEdgeFunctionsPath(filePath) {
  const normalized = filePath.replace(/\\/g, "/");
  return normalized.includes("/supabase/functions/");
}

function isAlreadyWrapped(call) {
  // Detect: console.log(JSON.stringify({level:..., ...}))
  const args = call.getArguments();
  if (args.length !== 1) return false;
  const arg = args[0];
  if (arg.getKind() !== SyntaxKind.CallExpression) return false;
  const innerExpr = arg.getExpression();
  if (!innerExpr || innerExpr.getText() !== "JSON.stringify") return false;
  const innerArgs = arg.getArguments();
  if (innerArgs.length === 0) return false;
  const firstArg = innerArgs[0];
  if (firstArg.getKind() !== SyntaxKind.ObjectLiteralExpression) return false;
  // Check has `level` property
  return firstArg.getProperties().some((prop) => {
    if (prop.getKind() !== SyntaxKind.PropertyAssignment) return false;
    return prop.getName() === "level";
  });
}

function findConsoleCalls(sourceFile, includeWrapped = false) {
  return sourceFile.getDescendantsOfKind(SyntaxKind.CallExpression).filter((call) => {
    if (call.wasForgotten()) return false;
    const expr = call.getExpression();
    if (!expr || expr.getKind() !== SyntaxKind.PropertyAccessExpression) return false;
    const obj = expr.getExpression();
    if (!obj || obj.getText() !== "console") return false;
    if (!CONSOLE_METHODS.has(expr.getName())) return false;
    if (!includeWrapped && isAlreadyWrapped(call)) return false;
    return true;
  });
}

function hasSerializeErrHelper(sourceFile) {
  return sourceFile.getFunctions().some((fn) => fn.getName() === "serializeErr");
}

function isStringLiteralLike(node) {
  if (!node) return false;
  const k = node.getKind();
  return (
    k === SyntaxKind.StringLiteral ||
    k === SyntaxKind.NoSubstitutionTemplateLiteral ||
    k === SyntaxKind.TemplateExpression
  );
}

function buildWrappedArgs(call, level) {
  const args = call.getArguments();
  if (level === "error") {
    if (args.length === 0) {
      return `JSON.stringify({ level: "error" })`;
    }
    // Heuristica: si primer arg es string literal -> es el msg; segundo (si existe) es err.
    // De lo contrario primer arg es el err.
    if (isStringLiteralLike(args[0])) {
      const msg = args[0].getText();
      if (args.length === 1) {
        return `JSON.stringify({ level: "error", msg: ${msg} })`;
      }
      const errExpr = args[1].getText();
      if (args.length === 2) {
        return `JSON.stringify({ level: "error", msg: ${msg}, err: serializeErr(${errExpr}) })`;
      }
      const ctxParts = args
        .slice(2)
        .map((a, i) => `ctx${i}: ${a.getText()}`)
        .join(", ");
      return `JSON.stringify({ level: "error", msg: ${msg}, err: serializeErr(${errExpr}), ${ctxParts} })`;
    }
    // Primer arg no es string -> es el err
    const errExpr = args[0].getText();
    if (args.length === 1) {
      return `JSON.stringify({ level: "error", err: serializeErr(${errExpr}) })`;
    }
    const ctxParts = args
      .slice(1)
      .map((a, i) => `ctx${i}: ${a.getText()}`)
      .join(", ");
    return `JSON.stringify({ level: "error", err: serializeErr(${errExpr}), ${ctxParts} })`;
  }
  // Non-error levels: pack args como {level, msg, extra0, extra1, ...}
  if (args.length === 0) {
    return `JSON.stringify({ level: "${level}" })`;
  }
  const firstArg = args[0].getText();
  if (args.length === 1) {
    return `JSON.stringify({ level: "${level}", msg: ${firstArg} })`;
  }
  const extraParts = args
    .slice(1)
    .map((a, i) => `extra${i}: ${a.getText()}`)
    .join(", ");
  return `JSON.stringify({ level: "${level}", msg: ${firstArg}, ${extraParts} })`;
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

  if (!isInDenoEdgeFunctionsPath(target)) {
    if (verifyMode) {
      process.exit(0); // out of scope = verified
    }
    process.stderr.write("file NOT in supabase/functions/ - out of scope (use console_to_logger)\n");
    process.exit(0);
  }

  const project = new Project({ skipAddingFilesFromTsConfig: true });
  let sourceFile;
  try {
    sourceFile = project.addSourceFileAtPath(target);
  } catch (err) {
    process.stderr.write(`failed to read ${target}: ${err.message}\n`);
    process.exit(2);
  }

  if (verifyMode) {
    const unwrapped = findConsoleCalls(sourceFile, /*includeWrapped=*/ false);
    if (unwrapped.length === 0) {
      process.exit(0);
    }
    process.stderr.write(`${unwrapped.length} unwrapped console.* call(s) still present\n`);
    process.exit(1);
  }

  const unwrapped = findConsoleCalls(sourceFile, /*includeWrapped=*/ false);
  let applied = 0;
  let needsErrHelper = false;

  for (const call of unwrapped) {
    if (call.wasForgotten()) continue;
    const expr = call.getExpression();
    const method = expr.getName();
    const level = LEVEL_MAPPING[method];
    const wrappedArgs = buildWrappedArgs(call, level);
    if (level === "error") needsErrHelper = true;
    // Replace whole call expression: console.foo(...) -> console.log(JSON.stringify(...))
    call.replaceWithText(`console.log(${wrappedArgs})`);
    applied++;
  }

  // Inject serializeErr helper si necesario y aun no esta presente
  if (needsErrHelper && !hasSerializeErrHelper(sourceFile)) {
    sourceFile.insertText(0, SERIALIZE_ERR_HELPER + "\n\n");
  }

  sourceFile.saveSync();

  const remaining = findConsoleCalls(sourceFile, /*includeWrapped=*/ false).length;
  process.stdout.write(`applied=${applied} remaining=${remaining}\n`);
  process.exit(0);
}

main();
