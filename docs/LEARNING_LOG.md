# Учебный журнал

Здесь хранятся воспроизводимые объяснения существенных изменений. Журнал не
дублирует оперативный статус и не содержит скрытых рассуждений модели.

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
`unmatched-browser-client-hash`. Финальный reviewer — `No blocking findings`. Runtime Skills не
синхронизировались до merge.

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
