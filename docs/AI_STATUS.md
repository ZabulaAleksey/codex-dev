# Текущее состояние ДЕВ / КАРКАС

Дата: 2026-08-27

## Статус

- Lifecycle: `completed` на `feature/architecturally-complete-stages`.
- Evidence level: `committed`, feature commit `8c05d0f`.
- Integration: не merged, не pushed, не released/deployed.
- Runtime: изменённые Skill sources ещё не materialized в `~/.agents/skills`; active runtime
  намеренно соответствует текущей `main` до разрешённого merge.

Глобальный ДЕВ теперь имеет один канонический Stage contract в `rules/governance.md`. Он запрещает
forward dependency, ложный completion по scaffold evidence и перенос обязательного gate в будущий
stage. Planning/execution Skills и templates собирают операционные поля, но не копируют policy.

## Реализованный vertical slice

- `specs/system.spec.md` содержит `FR-007`/`AC-007` и cross-surface consistency `AC-008`;
- governance разделяет lifecycle и evidence/integration, определяет internal/product E2E и
  terminal gate;
- full staged overlay baseline, architecture/ADR mapping и SPEC/test authority согласованы;
- `docs/AI_PLAN.md` stable `Stage ID` выбирает exact unique heading record в
  `prompts/STAGES.md` через существующий SessionStart/SubagentStart hook;
- no-selector сохраняет compact snapshot; invalid, duplicate, missing, ambiguous или oversized
  input выдаёт visible `DEGRADED`, не случайный fallback;
- structural и subprocess contract tests защищают global surfaces и internal hook path.

## Verification evidence

- `py -3 -B -m unittest discover -s tools -p "test*.py"` — PASS, 88 tests;
- canonical explicit unit/contract suite — PASS, 88 tests;
- `py -3 -B tools\validate_context.py` — PASS, 198 files;
- `skill-sources\dev-karkas\scripts\validate.ps1` — PASS;
- `quick_validate.py` через `python -X utf8` — PASS для пяти изменённых Skills;
- hook compile и subprocess primary/degraded paths — PASS;
- `git diff --check`, cached diff check, conflict-marker и semantic conflict scans — PASS;
- initial и follow-up reviewer findings устранены; финальный state-aware reviewer —
  `No blocking findings`.

## Синхронизация документации

- Обновлены: `README.md`, `QUICKSTART.md`, `AGENTS.md`, system SPEC, governance/SDLC rules,
  `ARCHITECTURE.md`, `DECISIONS.md`, `CONTEXT_POLICY.md`, `CONTEXT_COMPATIBILITY.md`,
  `PROJECT_FRAMEWORK.md`, `HOOK_POLICY.md`, `TESTING.md`, `VERIFY_SETUP.md`, `WORKFLOW.md`,
  context inventory/maps, Skills/references, AI templates и state docs.
- Проверены и остались точными: `DESIGN.md`, `SECURITY.md`, feature SPECs,
  `docs/project-context.md`.
- Не применяются в этом global infrastructure repository: project `prompts/STAGES.md`,
  `TRACEABILITY.md`, `CHANGELOG.md`, `DEV_LOG.md`.

## Ограничения

- Active `main` global validator по-прежнему `BLOCKED` pre-existing сигналом
  `unmatched-browser-client-hash`; feature его не меняет.
- Semantic parser project DAG/evidence намеренно не добавлен без versioned schema/migration;
  истинность project completion остаётся evidence/review gate.
- Merge, runtime materialization и worktree cleanup требуют явного разрешения пользователя.

## Следующее действие

Запросить разрешение на merge в `main`; затем materialize runtime Skills и повторить
verification/documentation gate на target branch.
