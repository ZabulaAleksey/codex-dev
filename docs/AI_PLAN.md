# Текущий план ДЕВ / КАРКАС

Статус: единый project workflow — `completed` / `merged locally` в active `main`;
feature commit `4bcdf32` интегрирован fast-forward, push не выполнялся
Рабочий item: source ownership, lifecycle-команды, docs/learning triggers, external/device/monitoring
Дата: 2026-08-27

## Applicability

Глобальный infrastructure repository не является full staged product overlay и намеренно не
использует project `prompts/STAGES.md`. Поэтому этот change ведётся как bounded work item в
`AI_PLAN`, без параллельного stage source. Требуемые поля архитектурной завершённости ниже
зафиксированы явно.

Связанная SPEC: `specs/system.spec.md`, `NFR-003`, `FR-008`, `FR-009`, `AC-009..012`.

## Dependency DAG и входные предпосылки

```text
architecturally complete stage contract (`2eed0ac`, completed/merged locally)
        ↓
actual `~/.codex` source/runtime architecture + existing governance (validated baseline)
        ↓
unified project workflow (`feature/unified-project-workflow`, validated locally)
```

- Self-reference, cycle и forward dependency отсутствуют; будущая интеграция не нужна для запуска
  или проверки feature-worktree slice.
- Global source и выделенный worktree были clean до mutation; baseline — 198 files, 88 tests PASS.
- Existing accepted tests не изменялись; новый contract test добавлен отдельным файлом.
- Active `~/.codex` ↔ `~/.agents/skills` parity — PASS, 9/9 при baseline и финальном read-enabled
  check. Skill sources этой feature не менялись, поэтому отдельная runtime materialization после
  merge не требуется.

## Самостоятельный runnable vertical slice

```text
workflow brief + actual repository audit
  → specs/system.spec.md FR-008/FR-009
  → rules/governance.md single policy owner
  → docs/WORKFLOW.md + CONTEXT_POLICY + LEARNING template
  → validate_global_codex fail-visible source-root check
  → structural/validator tests + real project read-only restore
  → observable PASS or fail-visible status
```

Slice не зависит от нового hook, Skill, MCP, external service или будущего component. Active
runtime integration является отдельным evidence level, а не отсутствующей инфраструктурой slice.

## Concrete end-to-end scenario

1. Неверный canonical source root `~/codex-workspace` передаётся production global validator.
2. Validator возвращает sorted `missing-canonical-source`/layout/Skill issues без traceback.
3. Для real project `electro-tutor` выполняются Git status, reconciliation, overlay validator и
   SessionStart hook из глобального ДЕВ.
4. Hook восстанавливает status/SPEC/plan, а semantic audit активных маршрутов подтверждает текущий
   следующий stage `TUTOR-02` без зависимости от старого чата.

Результат: оба internal consumer paths исполнимы без старого чата; validator и real project restore
— PASS с точным project-owned следующим stage `TUTOR-02`. Dirty worktree проекта сохранён без
изменений и указан как caveat, а не как дефект восстановления контекста.

## PASS criteria и evidence

- [x] Фактический global root `~/.codex` закреплён; конкурирующий
  `~/codex-workspace/global/codex` явно отклонён.
- [x] Один responsibility matrix, documentation trigger table, LEARNING contract, external sync
  policy, device restore и monitoring classes принадлежат governance.
- [x] `docs/WORKFLOW.md` содержит восемь copy-ready lifecycle requests без новой prompt library.
- [x] Новый LEARNING template содержит `Problem / Symptom / Root cause / Failed attempts / Fix /
  Verification / Prevention / Links`; historical logs не переписаны.
- [x] Skills/hooks/MCP/agents/config не расширены; project overlays не получили global copies.
- [x] Wrong source root fail-visible; real project restore сверяет активные stage routes с текущими
  plan/status вместо доверия только structural PASS.
- [x] Feature commit `4bcdf32` fast-forward merged в локальную `main`; push, external writes и
  runtime materialization не выполнялись.

Проверки:

- `py -3 -B -m unittest discover -s tools -p "test_*.py"` — PASS, 94 tests;
- `py -3 -B tools\validate_context.py` — PASS, 199 files;
- wrong-root global validator — expected structured FAIL, без exception;
- active `~/.codex` Skill parity — PASS, 9/9 при read-enabled check; sandbox без доступа к
  `~/.agents/skills` может дать ложный drift и не является authoritative evidence;
- active global validator — `BLOCKED` только pre-existing `unmatched-browser-client-hash`;
- `validate_project_overlay.py electro-tutor --json` — structural PASS;
- `reconcile_project_framework.py electro-tutor --json` — `BROWNFIELD`, pnpm, dependency drift none;
- real SessionStart hook — observable project status/SPEC/plan snapshot; restore PASS, `TUTOR-01`
  завершён, следующий stage `TUTOR-02`, активных маршрутов на `STAGED_PROMPTS.md` нет;
- unrelated dirty `electro-tutor` worktree зафиксирован read-only и не изменялся;
- повторный read-only reviewer — прежние blockers закрыты, новых blocking findings нет;
- `git diff --check` — PASS (только line-ending informational warnings).

## Допустимая временная реализация

`none`: policy, operational prompts, template, validator behavior и tests являются рабочей
реализацией текущего internal slice, а не scaffold.

## Deferred / не входит

- push и materialization в active runtime — отдельные действия, не выполненные этим локальным
  merge;
- repair pre-existing Browser client hash;
- project-owned `electro-tutor` `TUTOR-02` и его текущий dirty work; эта задача их не изменяет;
- mapping/удаление legacy `presets/*` quarantine;
- внешние Notion/Airtable/Eraser/Figma/GitHub writes и автоматическая sync infrastructure;
- semantic parser произвольных project links/stage evidence без versioned schema.

Эти пункты не нужны для запуска или проверки feature-worktree slice; ограничения отражены явно.

## Documentation audit

- Обновлены: system SPEC, governance, workflow/context/architecture/decision/compatibility/testing
  docs, README/verification guide, learning template/legacy marker, inventory maps, validator,
  manifest, новый contract test и state docs.
- Проверены без содержательных изменений: `AGENTS.md`, `QUICKSTART.md`, `PROJECT_FRAMEWORK.md`,
  `DESIGN.md`, `SECURITY.md`, `HOOK_POLICY.md`, `MCP_CATALOG.md`, feature SPECs,
  `docs/project-context.md`, Skills/hooks/installer.
- Не применяются: project `prompts/STAGES.md`, `TRACEABILITY.md`, `CHANGELOG.md`, `DEV_LOG.md`.

## Следующее действие

Slice реализован, проверен и fast-forward merged в локальную `main` commit-ом `4bcdf32`.
Обязательного следующего implementation stage нет. Push, Browser hash repair, product-specific
rollout и внешняя синхронизация остаются отдельными действиями с собственным разрешением.
