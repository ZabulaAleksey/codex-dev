# Архитектура AI-команды

## 1. Руководитель

Основной поток Codex играет роль технического руководителя. Он принимает пользовательскую задачу, определяет масштаб, выбирает специалистов, собирает их выводы и остаётся владельцем финального решения.

Руководитель не обязан создавать субагента для каждого шага. Простые изменения выполняются напрямую.

## 2. Маршрутизатор задачи

До выбора агентов руководитель определяет сложность, режим разработки, этап SDLC, домен, стек и соответствующую SPEC. Затем он загружает только необходимые правила из `rules/`.

```text
Запрос → требования → SPEC → архитектура → план → реализация → тесты → проверка SPEC
```

Маршрутизатор не является отдельным агентом: это обязанность основного потока Codex.

## 3. Глобальное ядро

| Агент | Назначение | По умолчанию |
|---|---|---|
| architect | архитектурные границы и план | только чтение |
| planner | превращает цель в конечный план и критерии приёмки | только чтение |
| backend_engineer | API, сервисы, backend на Python/Node | запись в рабочую область |
| frontend_engineer | React, Next.js и UI | запись в рабочую область |
| database_engineer | схемы, миграции и запросы | запись в рабочую область |
| devops_engineer | Docker, CI/CD и среды выполнения | запись в рабочую область |
| test_engineer | тесты, воспроизведение ошибок и регрессии | запись в рабочую область |
| reviewer | правильность и регрессии | только чтение |
| security_reviewer | авторизация, секреты и границы доверия | только чтение |
| performance_engineer | профилирование, узкие места и сравнительные тесты | только чтение |
| docs_researcher | актуальная документация через MCP | только чтение |
| beginner_mentor | объяснение готовых изменений | только чтение |
| release_manager | готовность, PR и контрольный список релиза | только чтение |

Встроенные агенты Codex `explorer` и `worker` сохраняются и используются для общего исследования и реализации.

Для Backend DX новые роли не создаются. `backend_engineer` владеет command/config/
service/API/debug design, `database_engineer` — guarded DB lifecycle,
`test_engineer` — tiers/isolation/CI evidence, `devops_engineer` — local services и
readiness, `reviewer` — duplication/hidden steps/overengineering, а
`security_reviewer` — secrets/redaction/production isolation/destructive guards.
Процедурный entrypoint — Skill `backend-dx-audit`.

## 4. Проектные специалисты

У каждого проекта есть 2–6 узких специалистов. Они находятся в `~/codex-workspace/<project>/.codex/agents/` и не засоряют остальные проекты.

## 5. Правило владения файлами

Во время параллельной реализации руководитель обязан назначить непересекающиеся области файлов. Если два изменения пересекаются, они выполняются последовательно.

Пример:

```text
architect + explorer  -> параллельно, только чтение
        ↓
SPEC и контракты      -> фиксируются до записи
        ↓
backend_engineer      -> backend/**
frontend_engineer     -> frontend/**
        ↓
test_engineer         -> tests/** + запуск тестов
        ↓
reviewer              -> проверка diff и SPEC без записи
```

## 6. Лимиты

Не используй многоагентность ради самой многоагентности. Если задача помещается в один модуль и проверяется одним набором тестов, основной агент выполняет её сам или вызывает одного профильного `worker`.

Конфигурационный ceiling — `max_concurrent_threads_per_session = 4`. Операционный бюджет из
README остаётся 0–1 / 2–3 / 3–5 по сложности; ceiling не является целевым количеством агентов.

## 7. Models и reasoning

Основной агент сохраняет модель, выбранную пользователем. Большинство `agents/*.toml` намеренно
не содержит `model`: такие роли наследуют active/default Codex model и задают только
role-specific `model_reasoning_effort`.

Reviewed explicit pins текущего набора:

| Роли | Model | Reasoning | Причина |
|---|---|---|---|
| `architect`, `security_reviewer` | `gpt-5.6-sol` | `high` | архитектурные и security-critical решения |
| `test_engineer` | `gpt-5.6-luna` | `medium` | bounded regression work и быстрые прогоны |

Идентификаторы `gpt-5.6-sol`, `gpt-5.6-terra` и `gpt-5.6-luna` сверены 2026-08-28 с
[официальным OpenAI models catalog](https://developers.openai.com/api/docs/models) и model list,
доступным текущему Codex-сеансу. Structural test закрепляет только reviewed allow-list и не является
runtime/account availability probe. Перед будущей заменой pin или cost-driven fallback снова
проверь availability/capability; неизвестная model не подменяется молча. Полный порядок
маршрутизации и premium ceiling задаёт `rules/model-routing.md`.
