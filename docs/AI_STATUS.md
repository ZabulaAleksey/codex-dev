# Текущее состояние ДЕВ / КАРКАС

Дата: 2026-08-24

## Статус

Глобальный ДЕВ хранится в единственном Git root `~/.codex`. Active instruction/rules layer предоставляет project-agnostic правила, agents, hooks, Skills, templates, validators и framework documentation. Product repositories наследуют глобальный `~/.codex/AGENTS.md` и хранят только локальную delta.

## Подтверждённые инварианты

- active global instruction source — `~/.codex/AGENTS.md`;
- runtime state, credentials, sessions, caches, downloaded plugins и machine-local config не входят в tracked global context;
- versioned custom Skill sources находятся в `skill-sources/`, runtime projection — в `~/.agents/skills`;
- project root определяется независимо, а глобальный framework не ведёт live inventory потребителей;
- `docs/AI_STATUS.md` — единственный текущий status source; `docs/AI_PLAN.md` — единственный текущий plan source;
- новые дополнительные долговечные `.md` размещаются в `docs/notes/`, если содержание нельзя включить в существующий canonical document;
- external Notion/Eraser/Figma projections не заменяют Git source of truth.
- global `rules/dependency-management.md` задаёт preferred matrix, exception
  contract, штатные shared caches/stores и clean-restore requirements; validators
  дают только read-only inventory/drift evidence и не мигрируют product repositories.

## Verification evidence

Для dependency-policy branch подтверждены:

- `py -3 -B -m unittest tools.test_validate_project_overlay tools.test_reconcile_project_framework tools.test_validate_global_codex tools.test_sync_global_skills` — PASS, 48 tests;
- `py -3 -B tools/validate_context.py` — PASS, 189 files;
- обновлённый project overlay validator — PASS на 12 фактических repositories, включая nested и multi-ecosystem manifests;
- `git diff --check` — PASS.

`validate_global_codex.py` до интеграции ветки показывает только ожидаемый runtime Skill drift для `bootstrap-project-framework` и `dev-karkas`: versioned sources новее активной проекции `~/.agents/skills`. Runtime sync выполняется только после merge, чтобы активная automation не опережала каноническую ветку.

## Результат decontamination

- backlog мигрирован в каноническую Notion-страницу с read-back verification; локальные исходники удалены;
- доказанно сопоставленные project presets удалены после сверки с более свежими repositories;
- registry содержит только schema/discovery policy, без actual inventory;
- вспомогательные Markdown-файлы находятся в `docs/notes/`;
- активная документация и automation больше не предлагают установку project-named presets;
- неоднозначные project-specific источники сохранены со статусом `BLOCKED` и не считаются active governance.

## Следующее действие

После разрешённого merge синхронизировать runtime Skills, повторить
`validate_global_codex.py` до полного PASS и далее поддерживать dependency contract
в project overlays через repository-scoped migration с recovery point, clean restore
и проверками.
