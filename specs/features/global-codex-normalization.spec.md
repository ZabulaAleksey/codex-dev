# Спецификация нормализации глобального слоя Codex

Статус: SUPERSEDED 2026-08-23 спецификацией `codex-home-consolidation.spec.md`
Версия: 1.0
Дата: 2026-08-20

## 1. Цель

Историческая цель этапа — устранить разрывы между прежним каноном и активным пользовательским слоем. После консолидации `~/.codex` является одновременно каноном и runtime-слоем.

## 2. Область

- канонические global agents, hooks, rules и installer;
- активные `~/.codex/AGENTS.md`, agents, hooks, rules и `config.toml`;
- MCP/plugin маршруты, доверенные project paths и локальные trusted services;
- read-only проверка установленного слоя;
- документация архитектуры, безопасности, совместимости и состояния этапа.

## 3. Вне области

- ротация или отзыв ключей во внешних сервисах;
- установка и OAuth-подключение отсутствующих плагинов;
- создание Git-репозитория из пустого `projects/dune-rts`;
- изменение продуктового кода или bootstrap неполных project overlays;
- ручное редактирование сгенерированных browser service hashes.

## 4. Требования

### FR-GC-001 Единый канонический источник

Managed-файлы `AGENTS.md`, agents, hooks и rules должны находиться непосредственно в `~/.codex`. Локальные полезные расширения сначала переносятся в этот канонический источник, а не теряются при синхронизации.

### FR-GC-002 Повторяемая диагностика

Read-only validator должен выявлять отсутствующие и расходящиеся managed-файлы, inline credential в Context7, отсутствующие trusted project paths, чрезмерно широкое доверие домашнему каталогу и ссылки на отсутствующие trusted services. Диагностика не должна выводить значения секретов.

### FR-GC-003 Windows-safe hooks

`SessionStart` и `SubagentStart` должны выдавать UTF-8 JSON даже при legacy Windows console encoding. `PreToolUse` сохраняет официальный matcher `^Bash$` и блокирует утверждённый deny-list.

### FR-GC-004 Однозначные интеграционные маршруты

- подключённый GitHub plugin является основным маршрутом; статический GitHub MCP выключен, но не удалён;
- Atlassian MCP выключен до подтверждённого runtime-подключения;
- отсутствующие Google Calendar и Slack plugins не должны оставаться помеченными как enabled;
- Context7 работает без inline API key и запускает локально проверенную точную версию npm package;
- отсутствующая browser service path удаляется без изменения host-managed `sky` binding, а неподтверждённые browser client hashes отбрасываются.

### SEC-GC-001 Секреты

Активный `config.toml` не должен содержать Context7 API key в аргументах процесса. Нормализатор и validator не выводят найденное значение. Отзыв ранее использованного ключа остаётся отдельным внешним действием владельца.

### SEC-GC-002 Границы доверия

Доверенные project paths должны существовать и соответствовать фактическим именам каталогов. Домашний каталог пользователя не должен быть доверен целиком, если перечислены конкретные рабочие области.

### SEC-GC-003 Окружение shell

Spawned shell не должен наследовать переменные, распознаваемые стандартной политикой Codex как `KEY`, `SECRET` или `TOKEN`. MCP host продолжает получать явно указанное имя переменной через собственный runtime contract.

### NFR-GC-001 Обратимость

MCP/plugin маршруты отключаются через `enabled = false`, а не удаляются. Нормализация должна быть идемпотентной и сначала проверять TOML до записи.

### NFR-GC-002 Минимальная область

Product repositories не изменяются автоматически только ради закрытия audit finding. Неоднозначные project gaps остаются явным списком следующих решений.

## 5. Критерии приёмки

- AC-GC-001 managed-файлы активного `~/.codex` совпадают с каноническими источниками;
- AC-GC-002 hook regression test проходит с принудительной cp1251 исходной кодировкой stdout;
- AC-GC-003 активный config не содержит `--api-key`, отсутствующей browser service, неподтверждённых browser hashes, старых project path aliases и broad home trust;
- AC-GC-004 GitHub/Atlassian MCP и отсутствующие Calendar/Slack plugins выключены обратимо;
- AC-GC-005 unit, integration и component проверки проходят;
- AC-GC-006 `docs/CONTEXT_COMPATIBILITY.md`, `docs/SECURITY.md`, `docs/DECISIONS.md` и
  соответствующий record `prompts/STAGES.md` отражают фактический результат;
- AC-GC-007 все неустранённые пункты перечислены с причиной и следующим безопасным действием.

## 6. Откат

- workspace-изменения откатываются отдельным `git revert` будущего коммита;
- отключённые MCP/plugins можно повторно включить после проверки подключения;
- удалённый inline credential намеренно не восстанавливается; при необходимости используется новый секрет через поддерживаемое внешнее хранилище;
- product repositories в этом этапе не изменяются.

## 7. Связь с проверками

| Требование | Проверка |
|---|---|
| FR-GC-001, FR-GC-002 | `tools/test_validate_global_codex.py`, запуск validator на активном `~/.codex` |
| FR-GC-003 | hook subprocess tests и прямые deny/allow probes |
| FR-GC-004, SEC-GC-001, SEC-GC-002, SEC-GC-003 | synthetic normalizer tests и повторный разбор активного TOML |
| NFR-GC-001 | повторный `--check` после `--apply` |
| AC-GC-005 | `unittest`, `validate_context.py`, hook/component probes |
