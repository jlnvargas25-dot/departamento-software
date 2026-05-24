// Fixture: patrones positivos para 7 rule_ids ESLint Tier A
// Rules cubiertos: TS-1 (prefer-const familia), NO-VAR, VAR-TO-CONST,
//                  LET-WITHOUT-REASSIGN, UNUSED-IMPORT, OBJECT-SHORTHAND, IMPORT-ORDER

// IMPORT-ORDER violation: orden no canonico (relativo antes que external)
import { Helper } from "./helper";
import { useState } from "react";
import path from "path";

// UNUSED-IMPORT violation: Helper se importa pero no se usa
// (TS-1 / @typescript-eslint/no-unused-vars)

// NO-VAR violation: var en lugar de let
var counter = 0;

// VAR-TO-CONST + LET-WITHOUT-REASSIGN violation: let sin reassign
let maxItems = 100;

function increment() {
  // NO-VAR violation adentro de funcion
  var local = 1;
  counter = counter + local;
  return counter;
}

function buildConfig(timeout: number, retries: number) {
  // OBJECT-SHORTHAND violation: {timeout: timeout, retries: retries}
  return {
    timeout: timeout,
    retries: retries,
  };
}

// useState importado para demostrar IMPORT-ORDER + side-effect: usado para evitar
// que TODOS los imports sean unused (solo Helper queda unused por design del fixture)
const [state] = useState(0);
console.log(path.sep, state, maxItems, increment(), buildConfig(30, 3));
