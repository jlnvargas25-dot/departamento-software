#!/usr/bin/env node
/**
 * non_null_to_optional.js — codemod ts-morph (S-6.1).
 *
 * Rule_id: TS-NON-NULL-ASSERTION
 * Pattern: NonNullExpression (operador `x!`)
 * Transformation:
 *   - parent PropertyAccessExpression: `x!.foo` -> `x?.foo`
 *   - parent ElementAccessExpression:  `x![0]`  -> `x?.[0]`
 *   - otro parent (standalone, return, etc.): NO modifica, exit 2 (escalation)
 *
 * Modes:
 *   - apply (default): aplica + guarda + exit 0 (applied count en stdout)
 *   - --verify: cuenta nodos, exit 0 si == 0, exit 1 si persiste
 *
 * Conservador: si encuentra contexto que no maneja, escala a Tier C
 * (exit 2). El orchestrator del mechanic lo registra como verification_failed
 * + rollback. NO improvisa.
 */

const { Project, SyntaxKind } = require("ts-morph");

function usage() {
  process.stderr.write("usage: non_null_to_optional.js [--verify] <file>\n");
  process.exit(2);
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

  const project = new Project({ skipAddingFilesFromTsConfig: true, useInMemoryFileSystem: false });
  let sourceFile;
  try {
    sourceFile = project.addSourceFileAtPath(target);
  } catch (err) {
    process.stderr.write(`failed to read ${target}: ${err.message}\n`);
    process.exit(2);
  }

  if (verifyMode) {
    const count = sourceFile.getDescendantsOfKind(SyntaxKind.NonNullExpression).length;
    if (count === 0) {
      process.exit(0);
    }
    process.stderr.write(`${count} NonNullExpression node(s) still present\n`);
    process.exit(1);
  }

  // Apply mode: iter hasta no quedar nodos manejables.
  let applied = 0;
  let escalated = 0;
  const MAX_ITERS = 100;
  for (let i = 0; i < MAX_ITERS; i++) {
    const nodes = sourceFile.getDescendantsOfKind(SyntaxKind.NonNullExpression);
    if (nodes.length === 0) break;

    // Procesar el primero que sea manejable.
    let changed = false;
    for (const node of nodes) {
      if (node.wasForgotten()) continue;
      const parent = node.getParent();
      if (!parent) {
        escalated++;
        continue;
      }
      const parentKind = parent.getKind();
      if (parentKind === SyntaxKind.PropertyAccessExpression) {
        const oldText = parent.getText();
        const newText = oldText.replace(/!\./, "?.");
        if (newText === oldText) {
          escalated++;
          continue;
        }
        parent.replaceWithText(newText);
        applied++;
        changed = true;
        break;
      }
      if (parentKind === SyntaxKind.ElementAccessExpression) {
        const oldText = parent.getText();
        const newText = oldText.replace(/!\[/, "?.[");
        if (newText === oldText) {
          escalated++;
          continue;
        }
        parent.replaceWithText(newText);
        applied++;
        changed = true;
        break;
      }
      escalated++;
    }
    if (!changed) break;
  }

  sourceFile.saveSync();

  // Apply mode siempre exit 0: aplicar lo manejable. Si quedan patterns
  // no manejables, verify-mode los detectara y reportara failed -> el
  // orchestrator hara rollback atomico (FileSnapshot).
  const remaining = sourceFile.getDescendantsOfKind(SyntaxKind.NonNullExpression).length;
  process.stdout.write(`applied=${applied} remaining=${remaining}\n`);
  process.exit(0);
}

main();
