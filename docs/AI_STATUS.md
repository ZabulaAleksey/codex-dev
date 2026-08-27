# Текущее состояние ДЕВ / КАРКАС

Дата: 2026-08-27

## Статус

- Lifecycle: unified project workflow `completed` в feature worktree.
- Evidence level: `validated locally`; commit отсутствует по прямому запрету пользователя.
- Integration: active `main`, runtime, remote и external services не изменялись.
- Runtime: active `~/.codex` ↔ `~/.agents/skills` parity — PASS, 9/9 при baseline и финальном
  read-enabled check; Skill sources feature не менялись и не materialize-ились из uncommitted
  worktree.

Единый global policy owner теперь формализует source responsibility, documentation/learning
triggers, external projections, device restore и monitoring. `docs/WORKFLOW.md` даёт восемь
copy-ready lifecycle requests как operational projection, а не второй governance layer.

## Реализованный vertical slice

- `specs/system.spec.md` содержит `FR-008..009` / `AC-009..012`;
- фактический канон `~/.codex` отделён от Skill runtime `~/.agents/skills`; предполагаемый
  `~/codex-workspace/global/codex` явно отклонён;
- governance содержит responsibility matrix, documentation trigger table, единый LEARNING shape,
  external sync/read-back policy, computer↔laptop contract и `active/event-driven/frozen`;
- workflow содержит start/stage/completion/architecture/pre-merge/pause/resume/idea prompts;
- global validator возвращает structured issues для missing canonical source вместо traceback;
- legacy `docs/notes/LEARNING_LOG.md` и named `presets/*` явно классифицированы как frozen/quarantine,
  а не конкурирующие active sources;
- hooks, Skills, MCP, agents, config и product repositories не модифицированы.

## Verification evidence

- `py -3 -B -m unittest discover -s tools -p "test_*.py"` — PASS, 94 tests;
- `py -3 -B tools\validate_context.py` — PASS, 199 files;
- wrong-root `validate_global_codex.py` — expected structured FAIL, traceback отсутствует;
- active `tools\sync_global_skills.py` read-enabled check — PASS, 9 sources; sandbox без доступа к
  runtime не используется как authoritative evidence;
- active global validator — `BLOCKED` только pre-existing `unmatched-browser-client-hash`;
- `validate_project_overlay.py electro-tutor --json` — structural PASS;
- `reconcile_project_framework.py electro-tutor --json` — `BROWNFIELD`, pnpm, drift none;
- real SessionStart hook восстановил project status/SPEC/plan; semantic route audit — PASS:
  `TUTOR-01` завершён, следующий stage `TUTOR-02`, активных маршрутов на `STAGED_PROMPTS.md` нет;
- повторный read-only reviewer — прежние blockers закрыты, новых blocking findings нет;
- `git diff --check` — PASS; line-ending сообщения являются informational.

## Синхронизация документации

- Обновлены: system SPEC, `rules/governance.md`, `README.md`, `ARCHITECTURE.md`, `DECISIONS.md`,
  `CONTEXT_POLICY.md`, `CONTEXT_COMPATIBILITY.md`, `TESTING.md`, `VERIFY_SETUP.md`, `WORKFLOW.md`,
  context inventory/maps, learning template/legacy marker, validator/test/manifest и state docs.
- Проверены и остались точными: `AGENTS.md`, `QUICKSTART.md`, `PROJECT_FRAMEWORK.md`, `DESIGN.md`,
  `SECURITY.md`, `HOOK_POLICY.md`, `MCP_CATALOG.md`, feature SPECs, `docs/project-context.md`,
  Skills/hooks/installer.
- Не применяются в этом global infrastructure repository: project `prompts/STAGES.md`,
  `TRACEABILITY.md`, `CHANGELOG.md`, `DEV_LOG.md`.

## Ограничения

- Active `main` global validator по-прежнему `BLOCKED` pre-existing сигналом
  `unmatched-browser-client-hash`; feature его не меняет.
- Feature не committed/merged, поэтому новый workflow ещё не является active `main`/runtime
  evidence. Runtime sync из uncommitted worktree намеренно не выполнялся.
- Real project restoration — PASS: `electro-tutor` восстанавливает текущий plan/status и выбирает
  `TUTOR-02` без старого чата. Unrelated dirty worktree сохранён read-only и не считается дефектом
  восстановления; исторические/отрицательные упоминания `STAGED_PROMPTS.md` не являются active
  stage routes.
- Legacy named presets остаются `BLOCKED` quarantine; mapping/удаление требует отдельного scope и
  разрешения. Semantic link/stage parser не добавлен без versioned schema.
- Commit, push, merge, deletion, external writes, release/deploy не выполнялись.

## Следующее действие

Read-only review завершён без blocking findings. Пользователь может отдельно разрешить commit
feature-ветки. Merge, push, runtime
materialization, Browser hash repair, product `TUTOR-02`, legacy preset cleanup и external sync —
самостоятельные последующие действия и не выполняются автоматически.
