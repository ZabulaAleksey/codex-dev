# Спецификация глобального project=overlay-каркаса

Статус: SUPERSEDED — rollout этапа 1 завершён
Версия: 1.1

> Историческое примечание 2026-08-20:
> требования FR-102, FR-105, FR-106 и связанные AC описывают завершённый
> rollout-эксперимент этапа 1 и не являются постоянными глобальными инвариантами ДЕВ.
> AI Dev Team больше не хранит live inventory product repositories и не назначает
> один следующий product repository своим этапом. Универсальный read-only
> project-overlay validator и inheritance rules остаются действующими.
> Ссылки ниже на `docs/PROJECT_CATALOG.md`, конкретные repositories и `projects/*`
> являются историческим audit trail. Текущая policy не хранит live inventory в
> global framework: `PROJECT_REGISTRY.md` задаёт только schema/discovery contract,
> actual bindings находятся во внешнем project-aware слое.

## 1. Назначение

Сделать уже описанный КАРКАС фактически активным на пользовательском уровне Codex и последовательно подключать к нему рабочие репозитории минимальными, проверяемыми project overlays.

## 2. Область

- канонические источники AI Dev Team в `~/.codex`;
- пользовательские `~/.codex/AGENTS.md` и `~/.agents/skills/bootstrap-project-framework`;
- единый rollout-реестр активных `projects/*`;
- read-only проверка одного project overlay;
- пилотное подключение одного чистого repository без изменения продукта.

## 3. Вне области

- массовое изменение всех repositories за один этап;
- реализация функций продукта;
- создание второго Git workflow, оркестратора, hooks, MCP или generic agents;
- исправление каталогов без собственного `.git`;
- удаление спорных локальных расширений без отдельного аудита.

## 4. Функциональные требования

### FR-101 Глобальная активация

Пользовательский слой Codex должен содержать router КАРКАСА в единственном `~/.codex/AGENTS.md`; versioned source Skill хранится в `~/.codex/skill-sources/`, а active Skill — в `~/.agents/skills/`.

### FR-102 Канонический rollout-реестр

`docs/PROJECT_CATALOG.md` должен однозначно показывать для каждого фактического каталога `projects/*` его lifecycle, Git-ready состояние, overlay-state, blocker и следующее действие. Отдельный JSON/YAML-реестр не создаётся.

### FR-103 Последовательный допуск

Repository допускается к изменению только если он является самостоятельным Git-root, его рабочая копия чиста либо изменения принадлежат текущему rollout, а project delta не требует изменения продукта.

### FR-104 Read-only validator

Общий инструмент должен принимать путь одного repository, ничего не изменять и проверять:

- самостоятельный Git-root;
- наличие тонкого `AGENTS.md`;
- канонические SPEC и документы КАРКАСА;
- отсутствие альтернативных status/source-of-truth файлов;
- точные копии глобальных agents, Skills, hooks, rules и workflow;
- наличие compatibility audit для локальных automation-возможностей.

### FR-105 Пилотный overlay

Первым изменяемым repository является `projects/off-screen-canvas`. Его project delta должна описать фактический проект, существующее поведение, текущий этап и дальнейшие шаги без изменения runtime-кода.

### FR-106 Продолжение очереди

После пилота реестр должен назвать ровно один следующий безопасный repository либо точный blocker, мешающий выбору.

## 5. Нефункциональные требования

### NFR-101 Отсутствие дубликатов

Проект не должен содержать локальные копии generic agents, глобальных Skills, общего hook topology, MCP/config или Git workflow. Узкие доменные расширения допустимы только со статусом `EXTEND` или `PROJECT_ONLY` в `docs/CONTEXT_COMPATIBILITY.md`.

### NFR-102 Идемпотентность проверки

Повторный запуск project-overlay validator на неизменённом repository должен давать тот же результат и не менять Git status.

### NFR-103 Безопасность установки

Глобальная активация должна сохранять пользовательские инструкции, не выполнять force-перезапись всей конфигурации и ограничиваться проверенной project-framework delta.

### NFR-104 Откат

Workspace delta и pilot delta должны находиться в отдельных Git-репозиториях и откатываться независимо одним revert соответствующего коммита.

## 6. Основной сценарий

1. Проверить глобальный канонический framework и фактически установленный пользовательский слой.
2. Сформировать rollout-реестр из существующих `projects/*`.
3. Запустить read-only validator для эталона и кандидата.
4. Создать рабочую ветку пилота.
5. Добавить только недостающую project delta.
6. Повторить validator, контекстный forward-test и review.
7. Обновить реестр и определить следующий repository.

## 7. Ошибки и граничные случаи

- Каталог без собственного `.git` получает blocker `not-git-root` и не изменяется.
- Dirty repository получает blocker `dirty-worktree`, если изменения не принадлежат rollout.
- Repository на `main`, `master` или `dev` сначала переводится в отдельную рабочую ветку.
- Локальная capability без compatibility audit не удаляется автоматически, а отмечается как требующая решения.
- Точная локальная копия глобальной capability считается ошибкой validation.

## 8. Критерии приёмки

- AC-101 `~/.codex/AGENTS.md` содержит project-framework router, а пользовательский Skill установлен один раз; существующий пользовательский контент сохранён.
- AC-102 `tools/validate_context.py` продолжает успешно проверять workspace manifest.
- AC-103 project-overlay validator имеет автоматические тесты для complete, incomplete, duplicate и non-Git сценариев.
- AC-104 `projects/off-screen-canvas` проходит project-overlay validation после пилота.
- AC-105 Diff пилота не содержит runtime-кода и локальных generic agents/Skills/hooks/MCP/config/Git workflow.
- AC-106 `docs/PROJECT_CATALOG.md` фиксирует результат пилота, blockers и один следующий rollout-кандидат.
- AC-107 Релевантный SessionStart/ручной forward-test использует компактный набор проектного контекста.

## 9. Связь с тестами

| Требование | Проверка |
|---|---|
| FR-101, NFR-103 | сравнение установленного router/Skill с каноническими файлами без force-install |
| FR-102, FR-103, FR-106 | review `docs/PROJECT_CATALOG.md` и Git status кандидатов |
| FR-104, NFR-101, NFR-102 | unit-тесты project-overlay validator и повторный запуск на пилоте |
| FR-105 | Git diff пилота и validator |
| NFR-104 | независимые ветки/коммиты workspace и пилота |

## 10. Открытые вопросы

- Порядок repositories после первого пилота уточняется по чистоте рабочей копии и величине project delta; массовый rollout не предполагается.
- `dune-rts` требует отдельного решения о создании или восстановлении самостоятельного Git-репозитория.

## 11. История изменений

- 2026-08-13 — версия 1.0: глобальная активация, read-only validator, единый реестр и пилот `off-screen-canvas`.
- 2026-08-24 — версия 1.1: SPEC помечен `SUPERSEDED`; live inventory вынесен из global framework.
