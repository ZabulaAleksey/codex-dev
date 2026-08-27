# Текущий план ДЕВ / КАРКАС

Статус: архитектурно завершённый stage contract fast-forward слит в локальную `main`, target
validated, runtime Skills materialized; push не выполнялся
Рабочий item: правило архитектурно завершённых этапов — `completed` на `main`
Дата: 2026-08-27

## Applicability

Глобальный infrastructure repository не является full staged product overlay и намеренно не
использует project `prompts/STAGES.md`. Поэтому этот change ведётся как bounded work item в
`AI_PLAN`, без параллельного stage source. Требуемые поля архитектурной завершённости ниже
зафиксированы явно.

Связанная SPEC: `specs/system.spec.md`, `NFR-001`, `NFR-003`, `FR-007`, `AC-007`, `AC-008`.

## Dependency DAG и входные предпосылки

```text
Completion Documentation Synchronization Gate (`b4d8565`, completed/merged locally)
        ↓
existing SDD + governance + source/runtime Skill split (validated baseline)
        ↓
architecturally complete stage contract (`8c05d0f` + `41612d0`, merged locally)
```

- Self-reference, cycle и forward dependency отсутствуют.
- Git source/worktree были clean до mutation; baseline — 197 managed files и 70 tests PASS.
- Existing accepted tests не изменялись; новый contract test добавлен отдельным файлом.
- Runtime Skills materialized из active `main`; source/runtime parity — PASS, 9/9.

## Самостоятельный runnable vertical slice

```text
user requirement
  → specs/system.spec.md
  → rules/governance.md Stage contract
  → AGENTS/rules/Skills/templates/status workflow
  → AI_PLAN Stage ID
  → SessionStart/SubagentStart exact STAGES record projection
  → structural + subprocess contract tests
  → observable PASS / visible DEGRADED result
```

Slice не зависит от будущего компонента. Exact selector не объявляет stage завершённым и не
заменяет semantic review DAG, prerequisites или evidence.

## Concrete end-to-end scenario

1. Temporary independent Git repository содержит `docs/AI_PLAN.md` со stable `Stage ID`.
2. `hooks/session_context.py` безопасно разрешает `prompts/STAGES.md` внутри Git-root.
3. Hook возвращает ровно один выбранный heading record первым в `additionalContext`.
4. Другие stage records отсутствуют в результате; invalid, duplicate, missing или oversized
   selector даёт видимый `Stage context — DEGRADED` без silent fallback.

Результат: subprocess consumer path `AI_PLAN → hook → selected STAGES record` — PASS.

## PASS criteria и evidence

- [x] Future stage не разблокирует primary path, инфраструктуру или проверку предыдущего stage.
- [x] Dependency DAG, prerequisites, runnable slice, concrete E2E, PASS/evidence, допустимая
  temporary implementation и deferred scope обязательны до реализации.
- [x] Mock/stub/interface-only evidence допускает только non-terminal status.
- [x] Lifecycle и evidence/integration разделены; `completed`, `verified`, `DONE` имеют один gate.
- [x] SPEC/ADR остаются source of requirements; accepted tests — executable contract/evidence.
- [x] Full staged overlay baseline и legacy architecture/ADR mapping согласованы.
- [x] Task-aware route загружает только выбранный STAGES record и fail-visible при деградации.
- [x] Feature commits `8c05d0f` / `41612d0` fast-forward слиты в локальную `main`.

Проверки:

- `py -3 -B -m unittest discover -s tools -p "test*.py"` — PASS, 88 tests;
- canonical validator/sync/reconcile/Backend DX/documentation/stage suite — PASS, 88 tests;
- `py -3 -B tools\validate_context.py` — PASS, 198 files;
- `skill-sources\dev-karkas\scripts\validate.ps1` — PASS;
- `quick_validate.py` через `python -X utf8` — PASS для `dev-karkas`,
  `bootstrap-project-framework`, `plan-stage`, `implement-stage`, `resume-project`;
- `py -3 -B -m py_compile hooks\session_context.py` — PASS;
- `git diff --check`, staged diff check и conflict/competing-path scans — PASS;
- active `main` Skill parity — PASS, 9/9; global validator — `BLOCKED` только прежним
  `unmatched-browser-client-hash`.

## Допустимая временная реализация

`none`: selector, degraded path, documentation routes и tests являются рабочей реализацией
текущего internal slice, а не scaffold.

## Deferred / не входит

- versioned schema и semantic parser произвольных project `prompts/STAGES.md`;
- автоматическое доказательство истинности project DAG/E2E evidence;
- repair pre-existing Browser client hash;
- push/release/deploy без отдельного разрешения пользователя.

Эти пункты не нужны для запуска или проверки слитого target-branch slice.

## Documentation audit

- Обновлены: global router, SPEC, governance/SDLC rules, architecture/decisions/context/hook/testing
  docs, framework/workflow/quickstart/readme, compatibility/inventory maps, Skills/references,
  AI templates, validator manifest и новый contract test.
- Этим closeout обновлены: `AI_PLAN`, `AI_STATUS`, `ROADMAP`, `LEARNING_LOG`.
- Проверены без содержательных изменений: `DESIGN.md`, `SECURITY.md`, feature SPECs и
  `docs/project-context.md`; текущая задача их факты не меняет.
- Не применяются: project `prompts/STAGES.md`, `TRACEABILITY.md`, `CHANGELOG.md`, `DEV_LOG.md`.

## Следующее действие

Обязательных implementation/integration действий больше нет. Push не запрошен; отдельными
optional maintenance-задачами остаются Browser hash repair и будущий semantic parser только после
versioned STAGES schema. Удаление чистого временного worktree является локальным closeout и не
меняет project state.
