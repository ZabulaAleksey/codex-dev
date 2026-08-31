# Учебный журнал

Здесь хранятся воспроизводимые объяснения существенных изменений. Журнал не
дублирует оперативный статус и не содержит скрытых рассуждений модели.

## 2026-08-27 — i18n/l10n как global policy, а не project copy

### Problem

- Пользовательские products могли реализовывать translations локально, но глобальный ДЕВ не
  гарантировал различие `i18n`, `l10n`, `language` и `locale`, locale-aware formatting, fallback,
  text expansion или RTL с первого самостоятельного slice.

### Symptom

- Global audit не нашёл канонического i18n/l10n owner. Существовали только отдельные product
  implementations и независимое правило русского языка project context, которое можно было
  ошибочно принять за язык продукта.
- Копирование checklist в project DESIGN/SPEC либо frontend-only rule создало бы расходящиеся
  стандарты и не охватило бы public CLI, уведомления и отчёты.

### Root cause

- Cross-cutting product localization не была представлена в global policy layer и context router.
  Stage contract также не определял, какая минимальная i18n implementation уже работоспособна, а
  какая остаётся mock/interface-only scaffold.

### Failed attempts

- N/A — competing owners были выявлены до mutation. Полный текст в governance, frontend domain,
  новом Skill и project overlays отклонён на compatibility audit.

### Fix

- Создан единственный `rules/i18n-l10n.md`; `FR-010` / `AC-013` закрепляют стабильное требование.
- Global routers и `PROJECT_FRAMEWORK.md` доставляют policy в user-facing architecture, а project
  SPEC/DESIGN/architecture/testing хранят только supported locales, stack, исключения и evidence.
- Initial slice допускает одну production locale только вместе с real resources, fallback,
  locale-aware formatting и pseudo-locale либо alternate test locale. Future translations
  расширяют l10n, но не разблокируют прошлый stage.

### Verification

```text
command / check: py -3 -B -m unittest tools.test_i18n_l10n_policy
result: PASS — 7 tests, включая uniqueness/anti-copy gate
scope: canonical policy, routers, system SPEC and context-validator registration
caveat: structural framework contract, не product translation E2E

command / check: py -3 -B -m unittest discover -s tools -p "test_*.py"
result: PASS — 101 tests
scope: полный global unit/contract suite
caveat: internal global suite, не product translation E2E

command / check: py -3 -B tools\validate_context.py
result: PASS — 201 files
scope: Git-visible context and manifest
caveat: semantic quality подтверждена policy review, а не manifest alone

command / check: py -3 -B tools\sync_global_skills.py
result: PASS — 9 sources
scope: active Skill parity
caveat: Skill sources не менялись

command / check: git merge --ff-only feature/global-i18n-l10n-policy
result: PASS — policy commit ee3ea8a integrated в локальную main
scope: local Git integration и повторный Completion Documentation Synchronization Gate
caveat: push, product rollout и external writes не выполнялись

command / check: py -3 -B tools\validate_global_codex.py --workspace ~/.codex --codex-home ~/.codex
result: BLOCKED — только pre-existing unmatched-browser-client-hash
scope: active global layer после merge
caveat: i18n/l10n managed-file drift отсутствует; Browser hash не входит в scope policy
```

### Prevention

- Любой новый user-facing КАРКАС проверяет применимость через global router и создаёт только thin
  project delta. Structural test не выдаётся за живой product E2E, а brownfield migration не
  выполняется массово без repository-specific gap audit.

### Links

- [Global i18n/l10n policy](../rules/i18n-l10n.md)
- [System SPEC](../specs/system.spec.md)
- [Project framework](PROJECT_FRAMEWORK.md)
- [Compatibility decision](CONTEXT_COMPATIBILITY.md)
- [Contract test](../tools/test_i18n_l10n_policy.py)

## 2026-08-27 — единый workflow без второго global source

### Problem

- Workflow brief предполагал canonical source `~/codex-workspace/global/codex`, хотя фактический
  ДЕВ уже консолидирован непосредственно в `~/.codex`. Lifecycle-команды, external sync,
  cross-device handoff, monitoring и learning format не имели одной согласованной operational
  projection.

### Symptom

- Вызов `validate_global_codex.py --workspace ~/codex-workspace` завершался необработанным
  `FileNotFoundError` на отсутствующем workspace `AGENTS.md` вместо диагностического результата.
- Создание предполагаемого global root или нового workspace `AGENTS.md` восстановило бы два
  sources of truth. Structural project validator также мог быть green при stale semantic links.

### Root cause

- Legacy option `--workspace` пережил консолидацию и не проверял наличие canonical managed source
  перед hash digest. Политики описывали отдельные части workflow, но не назначали полный owner/
  projection contract для новых lifecycle-сценариев.

### Failed attempts

- N/A — crash был воспроизведён baseline-вызовом; повторять его или обходить созданием второго
  `AGENTS.md` не потребовалось.

### Fix

- Сохранён единственный global root `~/.codex`; полный contract расширен в
  `rules/governance.md`, а восемь copy-ready запросов размещены в существующем
  `docs/WORKFLOW.md`.
- Validator теперь возвращает `missing-canonical-source` и продолжает формировать sorted issues.
- LEARNING template нормализован; external services остаются explicit derived projections;
  Skills/hooks/MCP/runtime не менялись.

### Verification

```text
command / check: py -3 -B -m unittest discover -s tools -p "test_*.py"
result: PASS — 94 tests
scope: global tools, hooks, policies and validators
caveat: internal policy/validator E2E, не product E2E

command / check: py -3 -B tools\validate_context.py
result: PASS — 199 files
scope: global Git/manifest context
caveat: semantic project links проверяются отдельно

command / check: validate_global_codex.py с неверным canonical source root
result: expected structured FAIL, no traceback
scope: source-root failure path
caveat: active global validator отдельно сохраняет pre-existing unmatched-browser-client-hash

command / check: active Skill parity + active global validator
result: PASS 9/9 parity; validator BLOCKED только unmatched-browser-client-hash
scope: read-enabled installed layer ~/.codex → ~/.agents/skills вне feature worktree
caveat: sandbox без чтения runtime дал ложный drift; синхронизация по такому сигналу запрещена

command / check: git merge --ff-only feature/unified-project-workflow
result: PASS — feature commit 4bcdf32 integrated в локальную main
scope: local Git integration; Completion Documentation Synchronization Gate повторён после merge
caveat: push, runtime materialization и external writes не выполнялись

command / check: electro-tutor overlay/reconciliation/SessionStart restore
result: PASS — structural PASS, BROWNFIELD/pnpm/no dependency drift, active route audit selects TUTOR-02
scope: один real project без старого чата
caveat: TUTOR-01 уже завершён другим project-owned workflow; unrelated dirty work не изменялся
```

### Prevention

- Негативный source-root regression test обязателен; `--workspace` документирован как legacy name
  canonical source root. Architecture assumption сначала сверяется с installer/DECISIONS, а не
  материализуется вслепую. Structural PASS не заменяет semantic link/status audit.

### Links

- [System SPEC](../specs/system.spec.md)
- [Governance](../rules/governance.md)
- [Operational workflow](WORKFLOW.md)
- [Compatibility decision](CONTEXT_COMPATIBILITY.md)
- [Global validator](../tools/validate_global_codex.py)
- [Regression test](../tools/test_unified_project_workflow_policy.py)

## 2026-08-27 — архитектурно завершённые этапы

### Что изменено

- `rules/governance.md` стал единственным полным Stage contract: только completed prerequisites,
  dependency DAG без cycle/forward edge, runnable vertical slice, concrete E2E, PASS/evidence,
  полностью рабочая temporary implementation и явно deferred scope.
- `blocked`, `scaffolded`, `partial`, `implemented_unverified` отделены от terminal
  `completed`/`verified`/`DONE`; mocks/stubs/interfaces подтверждают подготовку, но не product path.
- SPEC/ADR закреплены как source of requirements, accepted tests — как executable contract/evidence.
- Existing SessionStart/SubagentStart hook теперь выбирает bounded stage record по stable
  `Stage ID` из AI_PLAN. Selector не вводит вымышленное поле hook payload и не загружает весь
  catalog.

### Поток и fallback

```text
SPEC → governance Stage contract → Skills/templates → project AI_PLAN Stage ID
                                                    ↓
                         exact unique STAGES heading → selected context first
                                                    ↓
                 invalid/missing/duplicate/oversized → visible DEGRADED → manual check
```

Retry отсутствует, потому что Markdown input детерминирован. Silent fallback запрещён. Hook
игнорирует heading/selector examples внутри fenced blocks, отклоняет symlink наружу, ограничивает
scan/output и не объявляет DAG либо evidence истинными.

### Почему потребовался cross-architecture audit

Прежние surfaces расходились в четырёх местах: blocked gate можно было прочитать как допустимый
для DONE; tests назывались источником требований; full-overlay baseline и legacy architecture/ADR
paths имели разные пороги; документация обещала selected STAGES context, но production hook его не
доставлял. Исправление одного текста оставило бы скрытые конфликты в bootstrap, planning, status и
runtime route, поэтому были синхронизированы все owners и projections.

### Проверка

```text
py -3 -B tools\validate_context.py
py -3 -B -m unittest discover -s tools -p "test*.py"
powershell -NoProfile -ExecutionPolicy Bypass -File skill-sources\dev-karkas\scripts\validate.ps1
python -X utf8 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skill-sources/<changed-skill>
py -3 -B -m py_compile hooks\session_context.py
git diff --check
```

Результат feature commit `8c05d0f`: context validation — 198 files; unit/contract suite —
88 tests PASS; dev-karkas и пять изменённых Skills — valid; hook primary/degraded subprocess paths
и diff checks — PASS. Active `main` validator сохраняет только pre-existing
`unmatched-browser-client-hash`. Финальный reviewer — `No blocking findings`. Commits `8c05d0f` /
`41612d0` fast-forward слиты в локальную `main`; post-merge tests — 88 PASS, runtime Skill parity —
9/9. Push/release/deploy не выполнялись.

### Как повторить самостоятельно

1. Найди canonical requirement в SPEC и единственного полного policy owner.
2. Для stage заполни DAG, prerequisites, runnable slice, concrete E2E, PASS/evidence, temporary и
   deferred fields до реализации.
3. Укажи stable `Stage ID` в AI_PLAN и проверь, что он встречается ровно в одном STAGES heading.
4. Прогони primary selector и missing/duplicate/oversized degraded scenarios.
5. Выполни unit/integration/component и ближайший реальный consumer E2E; mock не называй E2E.
6. Сверь lifecycle отдельно от commit/merge/release evidence.
7. Перед DONE проверь state-bearing docs и повтори gate после разрешённого merge.

## 2026-08-26 — синхронизация документации при завершении работы

### Что изменено

- В `rules/governance.md` добавлен единый Completion Documentation Synchronization Gate.
- `dev-karkas`, `implement-stage`, общий workflow и templates теперь требуют проверять
  README, план, статус, roadmap, stage tracker и другие документы выполнения.
- Проверка отделена от mutation: точный документ не меняется только ради даты, но его
  актуальность должна быть подтверждена в handoff.

### Почему прежнего правила было недостаточно

Формулировка «обновляй документ, если информация изменилась» предполагала, что агент уже
обнаружил изменение. Без явного обязательного списка легко пропустить завершённую задачу в
`AI_PLAN`, старый blocker в `AI_STATUS`, устаревшую возможность README или неверный статус
merge/deploy. Новый gate сначала требует аудит, а затем решает, нужна ли запись.

### Проверка

```text
py -3 -B tools\validate_context.py
py -3 -B -m unittest tools.test_sync_global_skills tools.test_reconcile_project_framework tools.test_validate_global_codex tools.test_validate_project_overlay tools.test_backend_dx_policy tools.test_documentation_sync_policy
powershell -NoProfile -ExecutionPolicy Bypass -File skill-sources\dev-karkas\scripts\validate.ps1
python -X utf8 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skill-sources/dev-karkas
python -X utf8 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skill-sources/implement-stage
git diff --check
```

Результат target `main`: context validation — 197 files; unit suite — 70 tests;
обе Skill-проверки и diff check — PASS; runtime parity — 9/9. Global validator
`BLOCKED` только прежним `unmatched-browser-client-hash` без documentation/Skill drift.

### Как повторить самостоятельно

1. Перед `DONE` открой diff и фактические результаты проверок.
2. Проверь `README`, `AI_PLAN`, `AI_STATUS`, `ROADMAP` и stage tracker.
3. Проверь затронутые SPEC, architecture, decisions, design, security и testing docs.
4. Удали завершённые будущие шаги, снятые blockers и старое verification evidence.
5. Не меняй точные документы ради даты; отметь их как проверенные без изменений.
6. После merge повтори проверку по target branch и только затем фиксируй merge-level status.

## 2026-08-25 — единый Backend Developer Experience contract

### Что и зачем изменено

- Backend DX оформлен как один адаптивный глобальный contract с уровнями
  `BDX-L0..L3`, чтобы требования соответствовали реальной backend surface проекта.
- Каноническая политика, исполняемый audit Skill и project-specific delta разделены:
  методология живёт в `rules/backend-dx.md`, процедура — в
  `skill-sources/backend-dx-audit/`, а локальные команды и ограничения — в разделе
  `Backend DX Delta` файла `docs/project-context.md` конкретного проекта.
- Existing project validator расширен только opt-in проверками: проект без явной
  delta не получает Backend DX diagnostics и не классифицируется по эвристикам.

### Ключевой поток данных / управления

- Global `AGENTS.md` маршрутизирует backend-задачу к канонической политике и Skill.
- КАРКАС определяет applicability level по подтверждённым файлам и командам проекта.
- Для `BDX-L1..L3` проект фиксирует semantic commands, config/services/API/database,
  testing, diagnostics и safety ограничения в одном локальном delta-разделе.
- Read-only validator проверяет только явно подключённую delta; тестовый fixture
  доказывает этот contract без изменения product repositories.

### Команды и проверки

```text
py -3 -B tools\validate_context.py
py -3 -B -m unittest tools.test_sync_global_skills tools.test_reconcile_project_framework tools.test_validate_global_codex tools.test_validate_project_overlay tools.test_backend_dx_policy
python -X utf8 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skill-sources/backend-dx-audit
powershell -NoProfile -ExecutionPolicy Bypass -File skill-sources/dev-karkas/scripts/validate.ps1
py -3 -B tools\sync_global_skills.py --source skill-sources --destination ~/.agents/skills
py -3 -B tools\sync_global_skills.py --apply --source skill-sources --destination ~/.agents/skills
git diff --check
```

Локальный результат после commit и fast-forward merge: context validation — 196
файлов; полный suite — 65 тестов; Skill/package validation и runtime parity — PASS.

### Решения и trade-offs

- Явный opt-in через `## Backend DX Delta` выбран вместо автоматического поиска
  backend: это исключает ложные срабатывания в нейтральных и frontend-only проектах.
- Validator проверяет структуру и высокоуверенные safety-сигналы, но не исполняет
  команды проекта, не подключается к сервисам и не печатает значения секретов.
- Новые package managers, task runners, ORM, orchestration tools и CI providers не
  добавлялись: политика нормализует смысл существующих механизмов, а не стек.

### Проблемы и способы исправления

- После checkout слитых sources active `main` временно отличалась от runtime-копий
  трёх Skills на уровне materialized content. Штатный sync с `--apply` восстановил
  parity 9/9; после merge всегда проверяй parity именно из active source.
- `unmatched-browser-client-hash` остаётся внешним baseline-сигналом runtime Browser.
  Он блокирует общий global validator, но не связан с Backend DX и требует отдельной
  maintenance-задачи вместо молчаливого расширения текущего scope.

### Как повторить самостоятельно

1. Открой `rules/backend-dx.md` и выбери уровень по фактической backend surface.
2. Для `BDX-L1..L3` заполни `Backend DX Delta` в `docs/project-context.md` по шаблону.
3. Запусти `$backend-dx-audit` и сохрани evidence для применимых gates.
4. Выполни project validator и релевантные unit/integration/component tests.
5. Проверь Skill parity и `git diff --check` перед commit или merge.

## 2026-08-31 — profiler должен измерять только себя и проверять каждый writable descendant

**Problem:** первый AI Policy Profiling consumer report завысил profiler overhead; отдельный
stream/report path также мог быть заменён symlink/junction после проверки родительского
`.metrics/`.

**Symptom:** instrumented command включал своё wall time в `profiler_overhead_seconds`; child path
мог resolve-иться за project runtime directory, хотя сам `.metrics/` оставался внутри project.

**Root cause:** overhead timer запускался до subprocess вместо границы telemetry collection, а
containment проверялся только для parent directory, не для каждого config/stream/report target.

**Failed attempts:** первый synthetic report был построен с неверной timer boundary и исключён из
acceptance evidence; первоначальная parent-only containment проверка не покрывала descendant
symlink substitution; первый concurrent test показал, что Windows возвращает `PermissionError`,
а не только `FileExistsError`, когда lock уже удерживается другим writer.

**Fix:** timer instrumented run начинается после завершения consumer command; каждый writable/read
target проходит resolve + containment + symlink/junction check. JSONL append дополнительно использует
bounded exclusive lock и `O_APPEND`; Windows `PermissionError` получает bounded retry, а на
deadline классифицируется по фактическому наличию lock: contention либо ACL failure. Generated
reports заменяются atomically.

**Verification:** `py -3 -B -m unittest tools.test_ai_policy_profiler` — PASS, 14 tests, включая
реальный symlink escape negative path и 20 concurrent writers. Повторный independent consumer report показал
`profiler_overhead_ratio = 0.000513`; baseline/variant/reuse/handoff/agent sections сформированы,
raw command output в JSONL отсутствует. Synthetic sample не является evidence ROI policy.

**Prevention:** для любой self-profiling метрики явно отделять measured work от instrumentation;
для writable tree проверять каждый descendant target непосредственно перед I/O, а не доверять
только однажды проверенному parent.

**Links:** `specs/features/ai-policy-profiling.spec.md`, `tools/ai_policy_profiler.py`,
`tools/test_ai_policy_profiler.py`, `docs/SECURITY.md`.
