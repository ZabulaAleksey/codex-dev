# Учебный журнал

Здесь хранятся воспроизводимые объяснения существенных изменений. Журнал не
дублирует оперативный статус и не содержит скрытых рассуждений модели.

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
git diff --check
```

Локальный результат до commit: context validation — 196 файлов; полный suite —
65 тестов; Skill/package validation и runtime parity — PASS.

### Решения и trade-offs

- Явный opt-in через `## Backend DX Delta` выбран вместо автоматического поиска
  backend: это исключает ложные срабатывания в нейтральных и frontend-only проектах.
- Validator проверяет структуру и высокоуверенные safety-сигналы, но не исполняет
  команды проекта, не подключается к сервисам и не печатает значения секретов.
- Новые package managers, task runners, ORM, orchestration tools и CI providers не
  добавлялись: политика нормализует смысл существующих механизмов, а не стек.

### Проблемы и способы исправления

- Runtime Skills синхронизированы из feature worktree до merge. Поэтому validator
  активной `main` временно видит drift двух ранее существовавших Skills; после
  разрешённого merge нужно повторить active-global validation.
- Исходный `unmatched-browser-client-hash` исчез после внешнего изменения runtime
  state. Интеграция Backend DX не заявляет этот baseline-сигнал своим исправлением.

### Как повторить самостоятельно

1. Открой `rules/backend-dx.md` и выбери уровень по фактической backend surface.
2. Для `BDX-L1..L3` заполни `Backend DX Delta` в `docs/project-context.md` по шаблону.
3. Запусти `$backend-dx-audit` и сохрани evidence для применимых gates.
4. Выполни project validator и релевантные unit/integration/component tests.
5. Проверь Skill parity и `git diff --check` перед commit или merge.
