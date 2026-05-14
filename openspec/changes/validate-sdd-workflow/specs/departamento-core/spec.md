# Spec — validate-sdd-workflow / departamento-core

**Change**: `validate-sdd-workflow`
**Domain**: `departamento-core`
**Phase**: spec
**Date**: 2026-05-14
**Artifact store**: hybrid (engram + filesystem)

---

## Context

This spec codifies the structural contract of the SDD workflow itself, as applied to the
`validate-sdd-workflow` meta-change. The domain being specified IS the workflow engine
(the set of SDD skills and their coordination contract), not a business feature.

Domain origin: captured in `openspec/changes/validate-sdd-workflow/proposal.md` §4 (Scope)
and §7 (Success criterion). No separate exploration was run; the proposal is the primary
domain capture artifact (dominio-first, 3rd principle).

---

## Requirements

### REQ-WF-001 — Artifact Path Compliance (MUST)

Each SDD skill MUST write its artifact at the exact path defined in the Artifact File Paths
table of `~/.claude/skills/_shared/openspec-convention.md`. Deviations in path, filename, or
directory casing are structural violations.

| Skill | Required path |
|-------|--------------|
| sdd-propose | `openspec/changes/{change}/proposal.md` |
| sdd-spec | `openspec/changes/{change}/specs/{domain}/spec.md` |
| sdd-design | `openspec/changes/{change}/design.md` |
| sdd-tasks | `openspec/changes/{change}/tasks.md` |
| sdd-verify | `openspec/changes/{change}/verify-report.md` |

### REQ-WF-002 — Rule Compliance per Phase (MUST)

Each phase artifact MUST comply with every rule listed under its corresponding
`rules.{phase}` block in `openspec/config.yaml`. Specifically:

- `rules.specs`: artifacts MUST use Given/When/Then scenarios and RFC 2119 keywords
  (MUST, SHALL, SHOULD, MAY).
- `rules.proposal`: artifacts MUST include rollback plan, empirical success criterion,
  identification of the 3 layers (preventive / verifiable / corrective), and meta-pattern
  origin when applicable.
- `rules.design`: artifacts MUST include Mermaid sequence diagrams for flows with >3 actors
  or >5 steps, and document architecture decisions with rationale.
- `rules.tasks`: tasks MUST be empirically verifiable (not "done" by declaration), ordered
  by dependency, with Tier 1 (infrastructure) tasks preceding feature tasks.
- `rules.verify`: verify-report MUST include empirical evidence (file existence checks,
  engram search results) and MUST apply the 3-layer test.

### REQ-WF-003 — state.yaml Synchronization (MUST)

After each phase completes, `openspec/changes/{change}/state.yaml` MUST be updated:

1. `phases.{phase}` MUST be set to `done`.
2. The new artifact MUST be appended to the `artifacts` list with keys: `key`, `path`,
   and `topic_key`.
3. Existing entries in `phases` and `artifacts` MUST NOT be removed or overwritten.

### REQ-WF-004 — Engram Persistence in Hybrid Mode (SHOULD)

When `artifact_store: hybrid`, each phase SHOULD persist its artifact to Engram using:

- `topic_key`: `sdd/{change-name}/{phase}` (stable, upsert-safe)
- `project`: `departamento-software`
- `type`: `architecture`
- `capture_prompt`: `false` (automated artifact — no user prompt to capture)

Engram save SHOULD succeed before the skill returns. A failed Engram save MUST NOT
block the filesystem write or the `state.yaml` update.

### REQ-WF-005 — Filesystem as Authoritative Fallback (MUST)

If Engram is unavailable (network failure, MCP timeout, or unavailable process), the
filesystem write MUST still complete and MUST be treated as the authoritative record.
The hybrid mode degrades gracefully to openspec-only mode. The workflow MUST NOT halt
or report failure solely due to an Engram save failure.

### REQ-WF-006 — Loud Failure on Missing Artifact Path (MUST)

If a phase completes but its artifact path does not exist on the filesystem,
the workflow MUST fail loudly:

- `state.yaml` MUST NOT be updated to `done` for that phase.
- The skill MUST surface a CRITICAL finding to the caller.
- The phase is considered incomplete until the artifact exists at the expected path.

### REQ-WF-007 — Phase Ordering (MUST)

The DAG `proposal → spec → design → tasks → verify` MUST be respected. No phase SHALL
be marked `done` in `state.yaml` before all its dependencies are `done`. Specifically:

- `spec` and `design` MAY run in parallel (no dependency between them).
- `tasks` MUST NOT start until both `spec` and `design` are `done`.
- `verify` MUST NOT start until `tasks` is `done`.
- `apply` and `archive` are `skipped` for this meta-validation change.

### REQ-WF-008 — Idempotency (SHOULD)

Re-running any phase against the same `change-name` SHOULD produce a valid result:

- Filesystem writes SHOULD update in-place (read-before-write, no blind overwrite).
- Engram saves SHOULD upsert via `topic_key` (no duplicate observations).
- `state.yaml` SHOULD remain consistent (re-running a `done` phase keeps it `done`).

---

## Scenarios

### SCN-01 — Happy Path: All 5 Phases Complete Successfully

**Given** a change `validate-sdd-workflow` with `state.yaml` showing `proposal: done`
and all other phases pending,
**When** phases `spec`, `design`, `tasks`, and `verify` each execute in dependency order,
**Then**:
- `openspec/changes/validate-sdd-workflow/specs/departamento-core/spec.md` exists and
  contains Given/When/Then scenarios with RFC 2119 keywords.
- `openspec/changes/validate-sdd-workflow/design.md` exists and contains at least one
  Mermaid diagram.
- `openspec/changes/validate-sdd-workflow/tasks.md` exists and lists verifiable tasks.
- `openspec/changes/validate-sdd-workflow/verify-report.md` exists and reports 0 CRITICAL
  findings on the structural contract.
- `state.yaml.phases` shows `{proposal, spec, design, tasks, verify}: done`.
- `state.yaml.artifacts` lists exactly 5 entries (one per phase).
- Engram holds 5 observations with topic keys `sdd/validate-sdd-workflow/{phase}`.

### SCN-02 — Engram Unavailable Mid-Run (Hybrid Degrades to openspec)

**Given** a change in progress with `artifact_store: hybrid`,
**When** an Engram MCP call fails (timeout, unavailable process, or network error) during
any phase,
**Then**:
- The filesystem write for that phase MUST still complete at the expected path.
- `state.yaml` MUST be updated to `done` for that phase (filesystem is authoritative).
- The failing Engram call MUST be surfaced as a WARNING (not CRITICAL) in the verify report.
- The workflow MUST continue to the next phase without halting.

### SCN-03 — Spec Artifact Missing RFC 2119 Keywords

**Given** a `sdd-spec` run produces `specs/departamento-core/spec.md`,
**When** `sdd-verify` validates the artifact against `rules.specs`,
**Then**:
- If the artifact contains no instances of MUST, SHALL, SHOULD, or MAY, the verify-report
  MUST record a CRITICAL finding for this artifact.
- The `spec` phase status in the verify-report MUST be marked as FAILED.
- The overall verify-report MUST NOT report 0 CRITICAL findings.

### SCN-04 — Artifact Written to Wrong Path

**Given** a skill writes its output to a non-canonical path
(e.g., `openspec/changes/validate-sdd-workflow/spec.md` instead of
`openspec/changes/validate-sdd-workflow/specs/departamento-core/spec.md`),
**When** `sdd-verify` checks for the expected canonical path,
**Then**:
- The expected path MUST NOT be found.
- The verify-report MUST emit a CRITICAL finding: "Expected artifact missing at canonical path".
- `state.yaml` MUST NOT have been updated to `done` for that phase (REQ-WF-006).
- The file at the wrong path does NOT satisfy the requirement.

### SCN-05 — state.yaml Updated Out of Order (Phase Skipping)

**Given** `state.yaml` shows `spec: pending` and `design: pending`,
**When** an operator attempts to mark `tasks: done` in `state.yaml` before spec and
design are done,
**Then**:
- The workflow MUST reject the state transition (REQ-WF-007).
- `state.yaml` MUST retain `tasks: pending`.
- A CRITICAL finding MUST be raised: "Dependency not satisfied: tasks requires spec and
  design to be done."

### SCN-06 — Re-run of a Completed Phase (Idempotency)

**Given** `spec` phase is already `done` and the artifact exists at the canonical path,
**When** `sdd-spec` is re-invoked for the same change,
**Then**:
- The skill MUST read the existing file before writing (read-before-write).
- The resulting file MUST be a valid updated spec (not a blank overwrite).
- `state.yaml` MUST remain `spec: done` (re-running does not regress state).
- Engram MUST upsert (no duplicate observation created for the same `topic_key`).

### SCN-07 — Missing Artifact After Phase Declares Done

**Given** `sdd-spec` executes and `state.yaml.phases.spec` is set to `done`,
**When** `sdd-verify` checks for `specs/departamento-core/spec.md` and the file does
not exist on disk,
**Then**:
- The verify-report MUST emit a CRITICAL finding: "state.yaml inconsistency — phase
  marked done but artifact missing at canonical path".
- This constitutes a CRITICAL workflow integrity violation.

---

## Domain Invariants

These conditions MUST hold at all times during the workflow lifecycle:

1. **INV-01 — state.yaml is the canonical DAG state.** Engram observations are a
   redundant persistence layer. In case of conflict, `state.yaml` takes precedence.

2. **INV-02 — Artifact paths are immutable per phase.** Once a path is registered in
   `state.yaml.artifacts`, it MUST NOT be changed. A new file at a different path does
   not replace an existing registered artifact.

3. **INV-03 — No phase overwrites a sibling phase's artifact.** `sdd-spec` MUST NOT
   write to `design.md`. `sdd-design` MUST NOT write to any file under `specs/`.
   Cross-phase writes are structural violations.

4. **INV-04 — `apply` and `archive` remain `skipped` for meta-validation changes.**
   Setting either to `done` for `validate-sdd-workflow` would violate the out-of-scope
   boundary declared in the proposal.

5. **INV-05 — The change directory boundary is enforced.** No skill execution for this
   change MUST modify files outside `openspec/changes/validate-sdd-workflow/`. Changes
   to `openspec/specs/`, `openspec/config.yaml`, or any other path are forbidden.

---

## Edge Cases

### EC-01 — Empty Artifact Produced

If a skill produces an empty file (0 bytes) at the canonical path, the file existence
check MUST still find it, but `sdd-verify` MUST flag it as a CRITICAL finding
("Artifact exists but is empty").

### EC-02 — Malformed state.yaml

If `state.yaml` is corrupted or unparseable YAML:

- The skill attempting to update it MUST surface a CRITICAL finding before proceeding.
- The skill MUST NOT silently overwrite state.yaml with a fresh file (data loss risk).
- A human operator MUST inspect and repair the file manually.

### EC-03 — Engram topic_key Collision Across Projects

If Engram holds an observation with the same `topic_key` under a different project,
the upsert MUST scope to `project: departamento-software`. Cross-project contamination
of topic keys is not a valid upsert target.

### EC-04 — Partial Write Failure (Disk Full / Permission Error)

If the filesystem write fails mid-operation (disk full, permission denied):

- The skill MUST surface a CRITICAL finding immediately.
- `state.yaml` MUST NOT be updated to `done`.
- Engram MUST NOT be updated (write order: filesystem first, then engram, then state.yaml).

### EC-05 — Concurrent Phase Execution Race Condition

If `spec` and `design` run truly in parallel and both attempt to update `state.yaml`
simultaneously:

- Each phase MUST perform a read-modify-write on `state.yaml` (not a blind write).
- The last writer wins on the `phases` key for its own phase only.
- Artifact entries MUST be appended, not replaced — a merge strategy MUST be used.
- If the merge cannot be guaranteed, phases SHOULD run sequentially rather than
  concurrently for this `state.yaml` update step.

### EC-06 — verify-report Produced for Incomplete DAG

If `sdd-verify` is invoked before all predecessor phases are `done`:

- verify-report MUST document which phases are pending or skipped.
- verify-report MUST emit a WARNING for each pending phase (artifact may be absent).
- verify-report MUST NOT emit 0 CRITICAL/WARNING findings if predecessors are pending.
