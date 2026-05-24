# Fixture target files — auto_fix_mechanic

Archivos sintéticos con patrones positivos (violación del rule_id presente)
para tests de S-3 (snapshot), S-4 (verifier), S-6 (codemods ts-morph),
S-7 (codemods Python) y S-8 (M3 empirical).

**R10 audit Paso 5 cerrado**: estos archivos resuelven la deuda de fixture
target files identificada en `auditoria/audit-plan-auto-fix-mechanic-2026-05-22.json`.

## Cobertura — 15/15 rule_ids Tier A v0.1.0

| Rule_id                       | Fixture file                                      |
|-------------------------------|---------------------------------------------------|
| TS-1                          | `eslint_basic.ts`                                 |
| TS-NON-NULL-ASSERTION         | `non_null.ts`                                     |
| A21-OBS-1-CONSOLE-LOG         | `console_logger.ts`                               |
| A21-OBS-1b-DENO-CONSOLE       | `supabase/functions/edge_handler/index.ts`        |
| NO-VAR                        | `eslint_basic.ts`                                 |
| VAR-TO-CONST                  | `eslint_basic.ts`                                 |
| MIGRATION-NAMING              | `supabase/migrations/0001_initial.sql`            |
| TYPE-CAST-AS-ANY              | `type_cast.ts`                                    |
| PGSQL-MISSING-VOLATILE        | `missing_volatile.sql`                            |
| LET-WITHOUT-REASSIGN          | `eslint_basic.ts`                                 |
| UNUSED-IMPORT                 | `eslint_basic.ts`                                 |
| TRAILING-WHITESPACE           | `formatting.ts`                                   |
| MISSING-SEMI                  | `formatting.ts`                                   |
| IMPORT-ORDER                  | `eslint_basic.ts`                                 |
| OBJECT-SHORTHAND              | `eslint_basic.ts`                                 |

8 archivos cubriendo los 15 rule_ids (los rule_ids del mismo dominio
TypeScript-basico se agrupan en `eslint_basic.ts` por economia).

**Convencion**: cada fixture se asume INMUTABLE en los tests. Tests que
modifican el fixture usan `shutil.copy(fixture, tmp_path)` primero.
