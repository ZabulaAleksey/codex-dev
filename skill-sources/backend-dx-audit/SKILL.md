---
name: backend-dx-audit
description: Проверить, спроектировать или улучшить воспроизводимость, command surface, configuration, services, API, database, tests, diagnostics и onboarding backend-проекта по canonical Backend DX Policy. Использовать для проблем setup/doctor/CI parity или явного Backend DX review; не использовать для обычной business feature без изменений developer workflow.
---

# Аудит и улучшение Backend DX

Полностью прочитай `~/.codex/rules/backend-dx.md` до оценки или изменения project.
Применяй ближайший `AGENTS.md`, project SPEC/contracts и существующий tooling.
Используй `$dev-karkas`, если задача также меняет framework/status documents.

## Workflow

1. Найди точный Git root, применимые instructions, branch/status, project
   manifests/lockfiles, CI, docs, scripts, services и принятые tests.
2. Классифицируй project как `BDX-L0`, `BDX-L1`, `BDX-L2` или `BDX-L3` по
   фактической architecture и риску. Не повышай уровень ради новой technology.
3. До mutations зафиксируй baseline commands/results и gap matrix для bootstrap,
   commands, toolchain, config, services, API, DB, test data/tiers, diagnostics,
   jobs/providers, CI parity, cross-platform и documentation.
4. Сопоставь semantic operations с существующими project commands. Предпочитай
   alias или малое расширение текущего command surface второму task runner.
5. Запиши только project-specific facts в `docs/project-context.md` по
   `~/.codex/templates/BACKEND_DX_DELTA_TEMPLATE.md`; оставь `AGENTS.md` тонким.
6. Предложи минимальный change set. Не добавляй Docker, OpenAPI, queues, tracing,
   ORM, logger или test framework без доказанного project gap.
7. Реализуй изменения только когда запрос пользователя разрешает запись. Защити
   production access и destructive DB/resource actions deny-by-default local/test
   guards; не ослабляй принятые tests и не скрывай fallback/mock mode.
8. Проверь applicable command map, isolated tests, config redaction, readiness,
   API/DB drift и clean-room scenario. Fixture/mock является более слабым evidence
   и должен быть явно так помечен.
9. Оцени `BDX-GATE-01..12` только как `PASS`, `FAIL`, `BLOCKED` или
   `N/A — reason`. Не выводи PASS только из documentation.
10. Обнови только затронутые canonical docs и сообщи command, purpose, result и key
    evidence. Отдели pre-existing failures от regressions.

## Stop conditions

Остановись и сообщи blocker вместо догадки, если target может быть production,
side effect неизвестен, reset/migration не имеет environment guard, потребовалось
бы ослабить принятые tests, credentials недоступны либо новый stack требует
architectural/product decision.

## Handoff

Верни repository/branch, applicability и rationale, gap/action matrix, changed
files, command map, gate results, validation evidence, documentation impact,
remaining risks и точные Git status/diff checks. Не выполняй merge или push без
отдельного разрешения.
