# Tasks — validate-sdd-workflow

**Change**: `validate-sdd-workflow`
**Domain**: `departamento-core`
**Note**: META-VALIDATION. `sdd-apply` is SKIPPED. Tasks below are the acceptance checklist
for `sdd-verify`. Each task maps to a spec requirement and a 3-layer tier.
**Total tasks**: 13 (T1.1–T1.3, T2.1–T2.7, T3.1–T3.3) + 2 N/A items (T4.1–T4.2)

---

## DAG Overview

```
T1.1 → T1.2 → T1.3
                 ↓
    T2.1  T2.2  T2.3  T2.4  T2.5  T2.6  T2.7   ← all depend on T1.3
              ↓
    T3.1 → T3.2 → T3.3                           ← depend on T2.*
```

Tiers 1–3 are sequential by dependency. Within each tier, tasks with the same
parent can run in parallel.

---

## Tier 1 — Infrastructure Presence (preventive)

These tasks verify the artifact directory and file structure exist before checking content.
Satisfies: REQ-WF-001 (path compliance), INV-05 (change directory boundary).

- [ ] **T1.1** Directory `openspec/changes/validate-sdd-workflow/` exists.
      **Done criterion**: `python -c "import pathlib; assert pathlib.Path('openspec/changes/validate-sdd-workflow').is_dir()"` exits 0.
      **Layer**: preventive
      **Depends on**: —

- [ ] **T1.2** `state.yaml` exists and parses as valid YAML.
      **Done criterion**: `python -c "import yaml; yaml.safe_load(open('openspec/changes/validate-sdd-workflow/state.yaml'))"` exits 0.
      **Layer**: preventive
      **Depends on**: T1.1

- [ ] **T1.3** All 4 expected artifact files are present on disk.
      **Done criterion**: all four paths resolve to regular files:
      - `openspec/changes/validate-sdd-workflow/proposal.md`
      - `openspec/changes/validate-sdd-workflow/specs/departamento-core/spec.md`
      - `openspec/changes/validate-sdd-workflow/design.md`
      - `openspec/changes/validate-sdd-workflow/tasks.md`

      Command: `python -c "import pathlib; [pathlib.Path(p).stat() for p in ['openspec/changes/validate-sdd-workflow/proposal.md','openspec/changes/validate-sdd-workflow/specs/departamento-core/spec.md','openspec/changes/validate-sdd-workflow/design.md','openspec/changes/validate-sdd-workflow/tasks.md']]"` exits 0.
      **Layer**: preventive
      **Depends on**: T1.2

---

## Tier 2 — Artifact Content Compliance (verifiable)

These tasks verify that artifact content satisfies the rules in `openspec/config.yaml`.
Satisfies: REQ-WF-002 (rule compliance per phase), REQ-WF-003 (state.yaml sync at write time).

- [ ] **T2.1** `proposal.md` references all 5 required rule topics (rollback plan, 3 layers,
      Python-vs-LLM, meta-pattern / polinización, empirical success criterion).
      **Done criterion**: `python -c "import re,pathlib; t=pathlib.Path('openspec/changes/validate-sdd-workflow/proposal.md').read_text(encoding='utf-8'); patterns=['rollback','preventiv','Python','polini','empíric|empiric']; [re.search(p,t,re.I) or (_ for _ in ()).throw(AssertionError(p)) for p in patterns]"` exits 0.
      **Layer**: verifiable
      **Depends on**: T1.3

- [ ] **T2.2** `specs/departamento-core/spec.md` uses RFC 2119 keywords.
      **Done criterion**: `python -c "import re,pathlib; t=pathlib.Path('openspec/changes/validate-sdd-workflow/specs/departamento-core/spec.md').read_text(encoding='utf-8'); assert re.search(r'MUST|SHALL|SHOULD|MAY',t)"` exits 0.
      **Layer**: verifiable
      **Depends on**: T1.3

- [ ] **T2.3** `specs/departamento-core/spec.md` contains Given/When/Then scenarios (≥3 of each keyword).
      **Done criterion**: `python -c "import re,pathlib; t=pathlib.Path('openspec/changes/validate-sdd-workflow/specs/departamento-core/spec.md').read_text(encoding='utf-8'); [assert len(re.findall(kw,t,re.I))>=3 for kw in ['Given','When','Then']]"` — each count ≥ 3.
      Simplified: `python -c "import re,pathlib; t=pathlib.Path('openspec/changes/validate-sdd-workflow/specs/departamento-core/spec.md').read_text('utf-8'); assert all(len(re.findall(k,t,re.I))>=3 for k in ['Given','When','Then'])"` exits 0.
      **Layer**: verifiable
      **Depends on**: T1.3

- [ ] **T2.4** `design.md` contains at least one Mermaid diagram block.
      **Done criterion**: `python -c "import pathlib; t=pathlib.Path('openspec/changes/validate-sdd-workflow/design.md').read_text('utf-8'); assert t.count('\`\`\`mermaid')>=1"` exits 0.
      **Layer**: verifiable
      **Depends on**: T1.3

- [ ] **T2.5** `design.md` has at least 3 ADR sections.
      **Done criterion**: `python -c "import re,pathlib; t=pathlib.Path('openspec/changes/validate-sdd-workflow/design.md').read_text('utf-8'); assert len(re.findall(r'^###\s+ADR',t,re.M))>=3"` exits 0.
      **Layer**: verifiable
      **Depends on**: T1.3

- [ ] **T2.6** `design.md` explicitly names all 3 architecture layers.
      **Done criterion**: `python -c "import re,pathlib; t=pathlib.Path('openspec/changes/validate-sdd-workflow/design.md').read_text('utf-8'); assert re.search(r'preventiv',t,re.I) and re.search(r'verifi',t,re.I) and re.search(r'correctiv|correctiva',t,re.I)"` exits 0.
      **Layer**: verifiable
      **Depends on**: T1.3

- [ ] **T2.7** `tasks.md` (this file) has explicit DAG with Tier 1 listed before Tier 2 and Tier 3.
      **Done criterion**: `python -c "import pathlib; t=pathlib.Path('openspec/changes/validate-sdd-workflow/tasks.md').read_text('utf-8'); i1=t.index('Tier 1'); i2=t.index('Tier 2'); i3=t.index('Tier 3'); assert i1<i2<i3"` exits 0.
      **Layer**: verifiable
      **Depends on**: T1.3

---

## Tier 3 — State Synchronization (corrective candidate)

These tasks verify that state.yaml and Engram are consistent with the filesystem.
Satisfies: REQ-WF-003 (state sync), REQ-WF-004 (engram persistence), REQ-WF-007 (DAG ordering).
Auto-fix candidates per design: AF-1 (state mismatch), AF-2 (engram missing but disk present).

- [ ] **T3.1** `state.yaml` `phases` map reflects current DAG state correctly.
      **Done criterion**: `python -c "import yaml,pathlib; s=yaml.safe_load(pathlib.Path('openspec/changes/validate-sdd-workflow/state.yaml').read_text('utf-8')); p=s['phases']; assert p.get('proposal')=='done' and p.get('spec')=='done' and p.get('design')=='done' and p.get('tasks')=='done' and p.get('apply') in ('skipped',None) and p.get('archive') in ('skipped',None)"` exits 0.
      **Layer**: corrective candidate (AF-1)
      **Depends on**: T2.1, T2.2, T2.3, T2.4, T2.5, T2.6, T2.7

- [ ] **T3.2** `state.yaml` `artifacts` list contains 4 entries with correct paths and topic_keys.
      **Done criterion**: `python -c "import yaml,pathlib; s=yaml.safe_load(pathlib.Path('openspec/changes/validate-sdd-workflow/state.yaml').read_text('utf-8')); arts=s.get('artifacts',[]); assert len(arts)==4; keys={a['topic_key'] for a in arts}; assert keys=={'sdd/validate-sdd-workflow/proposal','sdd/validate-sdd-workflow/spec','sdd/validate-sdd-workflow/design','sdd/validate-sdd-workflow/tasks'}"` exits 0.
      **Layer**: corrective candidate (AF-1)
      **Depends on**: T3.1

- [ ] **T3.3** Engram has observations for all 4 topic_keys of this change.
      **Done criterion**: `mem_search` returns ≥1 result for each of:
      - `sdd/validate-sdd-workflow/proposal`
      - `sdd/validate-sdd-workflow/spec`
      - `sdd/validate-sdd-workflow/design`
      - `sdd/validate-sdd-workflow/tasks`

      Evidence: all 4 `mem_search` calls return non-empty results. Document observation IDs in verify-report.
      **Layer**: corrective candidate (AF-2 — rebuild from disk if missing)
      **Depends on**: T3.2

---

## Tier 4 — Workflow Contract (N/A for this validation run)

Documented for posterity. NOT checked by sdd-verify in this change.
Satisfies: REQ-WF-006 (loud failure on missing path — inverse: not exercised here).

- [ ] **T4.1** `sdd-apply` path not exercised.
      **Done criterion**: N/A. Skipped per proposal (meta-validation: no real code generated).
      Record as `N/A` in verify-report.
      **Layer**: —
      **Depends on**: —

- [ ] **T4.2** `sdd-archive` path not exercised.
      **Done criterion**: N/A. Skipped per ADR-D2 (archiving would contaminate
      `openspec/specs/departamento-core/` with workflow-about-workflow content).
      Record as `N/A` in verify-report.
      **Layer**: —
      **Depends on**: —

---

## Spec → Task Traceability Matrix

| Task  | Requirement         | Scenario       | Rule (config.yaml)                         |
|-------|---------------------|----------------|--------------------------------------------|
| T1.1  | REQ-WF-001, INV-05  | SCN-04         | tasks: ordenar por dependencia             |
| T1.2  | REQ-WF-003          | SCN-07         | tasks: verificables empíricamente          |
| T1.3  | REQ-WF-001          | SCN-04         | tasks: criterio de done concreto           |
| T2.1  | REQ-WF-002 proposal | SCN-01         | proposal: 5 rules de openspec/config.yaml  |
| T2.2  | REQ-WF-002 spec     | SCN-03         | specs: RFC 2119 keywords                   |
| T2.3  | REQ-WF-002 spec     | SCN-01, SCN-03 | specs: Given/When/Then                     |
| T2.4  | REQ-WF-002 design   | SCN-01         | design: Mermaid diagrams                   |
| T2.5  | REQ-WF-002 design   | SCN-01         | design: ADR-style rationale                |
| T2.6  | REQ-WF-002 design   | SCN-01         | design: 3 capas (2° principio)             |
| T2.7  | REQ-WF-007 (DAG)    | SCN-05         | tasks: DAG explícito, Tier 1 primero       |
| T3.1  | REQ-WF-003, INV-01  | SCN-07         | tasks: verificable empíricamente           |
| T3.2  | REQ-WF-003          | SCN-07         | tasks: criterio de done concreto           |
| T3.3  | REQ-WF-004          | SCN-02         | hybrid: filesystem + Engram redundancy     |
| T4.1  | REQ-WF-005 (N/A)    | —              | apply: skipped (meta-validation)           |
| T4.2  | REQ-WF-005 (N/A)    | —              | archive: skipped (ADR-D2)                  |

---

## Review Workload Forecast

- **Total tasks**: 13 verifiable + 2 N/A
- **Files changed**: docs only (`tasks.md`, `state.yaml`)
- **Estimated diff**: ~120 lines
- **400-line budget risk**: Low
- **Chained PRs recommended**: No
- **Decision needed before apply**: No (apply is skipped)
