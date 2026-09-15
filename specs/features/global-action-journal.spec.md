# Global Action Journal and deterministic tool discovery

Status: approved by the explicit 2026-09-15 launch of the Notion master prompt
`DEV — Global AI Context, Automation & Script Factory Audit — MASTER PROMPT`.
Source item: `3db61ed8-f246-81d7-bc79-fba7f8d03a41`; source revision:
`2026-09-14T20:47:07.483Z`.

## Scope and ownership

This is a global DEV capability. Versioned contracts and catalog live in the canonical DEV Git
source. Journal events are opt-in runtime data in an ignored directory and never become project
stage state, a prompt queue, or a Git-tracked log. `docs/STAGES.md` remains the only owner of
execution status and NEXT. Existing `spec_execution.py` owns Skill routing and pure automation
promotion decisions; `ai_policy_profiler.py` remains project-local and opt-in.

## Requirements

- `GAJ-001`: An explicit CLI initializes and appends bounded, versioned action events. No hook or
  automatic capture is installed. Each event has a stable ID, UTC timestamp, scope, normalized
  task/intent/action/actor/executor IDs, SHA-256 input fingerprint, resource and evidence refs,
  result, repeat signature, and an explicit redaction assertion. Optional duration/cost are
  nullable and must not be estimated.
- `GAJ-002`: The parser rejects unknown fields, unsupported versions, duplicate JSON keys,
  secret-like payloads, excessive size/count, path traversal, absolute paths, and link-like
  journal targets, including redirected parents. Journal bytes are capped at 16 MiB
  before read. Invalid input cannot mutate the journal.
- `GAJ-003`: Append is serialized across processes with a bounded lock and fsync. A repeated
  event ID with identical bytes is a no-op; a conflicting ID fails closed. Interrupted writes
  are detected by read-back validation. No raw command, prompt, stdout, stderr, environment
  value, credential, or chain-of-thought is stored.
- `GAJ-004`: A versioned Script Registry lists the existing verified DEV CLI/scripts with exact
  relative paths, purposes, task classes, side effects, risk, platforms, fallback, and check refs.
  Lookup is read-only and returns exact matching active tools; it never executes one or claims
  that merely installed files are active runtime capabilities.
- `GAJ-005`: Missing registry match yields explicit reasoning/Skill fallback. Duplicate names,
  nonexistent paths, unknown fields, unsafe paths, or incompatible schema fail closed. The
  catalog is a discovery projection over existing tools, not a second implementation owner.
- `GAJ-006`: A pure Repeat Detector reads only validated v1 events and versioned thresholds.
  It groups success and failure separately, distinguishes exact input fingerprints from
  normalized equivalent signatures, and emits candidate IDs/counts/event IDs without raw
  content. Zero observations emit zero candidates. Safety-critical task classes receive a
  human-review flag. Detection never creates, executes, promotes, or quarantines a script.
- `GAJ-007`: Candidate preflight reuses a cataloged active script only when its exact name
  matches the observed executor and task class, and the candidate has no safety review flag.
  Otherwise it returns `promotion_review_required` for existing `spec_execution.py` and
  human review. It never writes a script or candidate backlog. Journal init/record support
  explicit dry-run and report no side effects.

## Backward-complete stages

1. `DEV-GAJ-A`: Audit and bounded explicit Action Journal plus Script Registry lookup. Consumer
   path: caller supplies sanitized event to CLI, receives an append receipt, then discovers an
   existing tool by task class. PASS: targeted tests, schema/catalog validation, full DEV suite,
   context validator, and source-only install dry-run. Temporary implementation: explicit CLI;
   hooks/automatic capture are deferred.
2. `DEV-GAJ-B`: Repeat detector reads validated journal events and emits pure candidates for
   existing `spec_execution.py` promotion decisions. Thresholds come from versioned config;
   safety-sensitive candidates require human review. It cannot mutate scripts or policy.
3. `DEV-GAJ-C`: Exact existing-script reuse preflight and a real sanitized repeat consumer path.
   Novel candidates use the existing promotion/placement reviewer and require a separate
  bounded implementation decision. Comparative cost and advanced graph/cache/event service
  remain deferred until observed need.
4. `DEV-GAJ-D`: Finalization gate. Completed A/B/C source evidence is the prerequisite;
   local main integration, post-merge source checks, managed runtime parity and Notion
   exact-item cleanup are separate authorization/evidence boundaries. With either boundary
   pending, the master stays `partial` and the selected slice `blocked`.

The first stage is independently runnable and leaves current DEV routes intact. Later stages
only enrich observations; they do not unlock the first stage's CLI/lookup or validation.
