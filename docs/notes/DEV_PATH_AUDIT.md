# DEV path semantic audit

## Active canonical references

Active router, current SPEC, architecture, workflow, quickstart, installer, validators, hooks,
Prompt Queue and project template use `DEV_SOURCE_ROOT`, `CODEX_HOME`, `PROJECTS_ROOT` and
`${PROJECTS_ROOT}/<project>`. Repository identity examples target `codex-dev`.

## Retained `codex-workspace` references

The old name is retained only in these semantic classes:

- `tools/dev_paths.py` and migration tests: explicit legacy detection;
- `tools/validate_project_overlay.py` and its tests: stale/machine-specific legacy path findings;
- `tools/normalize_user_codex.py`: removal of obsolete `codex-workspace/projects` trust;
- `specs/features/codex-home-consolidation.spec.md`,
  `specs/features/full-workspace-governance.spec.md`, and
  `specs/features/project-overlay-rollout.spec.md`: `SUPERSEDED` requirements/audit trail;
- `prompts/STAGES.md`, `docs/DECISIONS.md`, `docs/LEARNING_LOG.md`,
  `docs/notes/LEARNING_LOG.md`, and historical sections of
  `docs/CONTEXT_COMPATIBILITY.md`: immutable or explicitly superseded execution/decision evidence.

These occurrences must not be used as current path defaults. New active references are rejected by
`tools/test_dev_paths.py` semantic contract tests.

## Retained `DEV == ~/.codex` references

They remain only as named legacy migration state, `SUPERSEDED` decisions/SPEC, test fixtures or
installer protection for an old `~/.codex/.git`. Current architecture consistently defines
`CODEX_HOME` as installed/runtime layer and `DEV_SOURCE_ROOT` as source Git root.

## Physical migration scope

No product repository, legacy source checkout, remote or GitHub repository was moved, renamed,
deleted, archived, pushed or merged by this change. `tools/dev_paths.py diagnose` and `move-plan`
provide read-only evidence for a later explicitly authorized migration.
