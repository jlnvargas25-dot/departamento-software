#!/usr/bin/env node
/**
 * infer_type_from_context.js — codemod ts-morph (S-6.4).
 *
 * Rule_id: TYPE-CAST-AS-ANY
 * Pattern: AsExpression con TypeNode = AnyKeyword (`x as any`).
 * Strategy de inferencia (conservadora):
 *   1. Obtener tipo de la expression via ts-morph type checker
 *   2. Si tipo es "any" | "unknown" | "never" -> no aplicar (escalation via verify-mode)
 *   3. Si tipo es complejo (>120 chars) -> no aplicar (legibilidad + riesgo)
 *   4. Else -> reemplazar `expr as any` con `expr as <inferred_type>`
 *
 * Resultado: cast preservado (mantiene assertion explicita) pero con tipo
 * correcto. NO borra el `as` (cambio mas conservador que removerlo entero).
 *
 * Casos que ESCALAN (no aplica):
 *   - `value as any` cuando value: unknown
 *   - Cast sobre expression sin tipo resolvible
 *   - Tipo inferido demasiado verbose (>120 chars) -> riesgo brittleness
 */

const { Project, SyntaxKind } = require("ts-morph");

const MAX_INFERRED_TYPE_LEN = 120;
const UNINFERABLE_TYPES = new Set(["any", "unknown", "never"]);

function usage() {
  process.stderr.write("usage: infer_type_from_context.js [--verify] <file>\n");
  process.exit(2);
}

function findAsAnyExpressions(sourceFile) {
  return sourceFile.getDescendantsOfKind(SyntaxKind.AsExpression).filter((ae) => {
    if (ae.wasForgotten()) return false;
    const typeNode = ae.getTypeNode();
    if (!typeNode) return false;
    return typeNode.getKind() === SyntaxKind.AnyKeyword;
  });
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

  const project = new Project({ skipAddingFilesFromTsConfig: true });
  let sourceFile;
  try {
    sourceFile = project.addSourceFileAtPath(target);
  } catch (err) {
    process.stderr.write(`failed to read ${target}: ${err.message}\n`);
    process.exit(2);
  }

  if (verifyMode) {
    const count = findAsAnyExpressions(sourceFile).length;
    if (count === 0) {
      process.exit(0);
    }
    process.stderr.write(`${count} \`as any\` cast(s) still present\n`);
    process.exit(1);
  }

  // Apply mode
  let applied = 0;
  let escalated = 0;
  const asExpressions = findAsAnyExpressions(sourceFile);

  for (const ae of asExpressions) {
    if (ae.wasForgotten()) continue;
    const expr = ae.getExpression();
    let inferred;
    try {
      inferred = expr.getType().getText(ae);
    } catch (err) {
      // type inference failed (e.g. unresolved symbol) -> escalate, see file header
      escalated++;
      continue;
    }
    if (UNINFERABLE_TYPES.has(inferred)) {
      escalated++;
      continue;
    }
    if (inferred.length > MAX_INFERRED_TYPE_LEN) {
      escalated++;
      continue;
    }
    const exprText = expr.getText();
    ae.replaceWithText(`${exprText} as ${inferred}`);
    applied++;
  }

  sourceFile.saveSync();

  const remaining = findAsAnyExpressions(sourceFile).length;
  process.stdout.write(`applied=${applied} escalated=${escalated} remaining=${remaining}\n`);
  process.exit(0);
}

main();
