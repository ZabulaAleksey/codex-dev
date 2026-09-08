# Политика hooks

## Почему основной hook глобальный

Codex загружает все подходящие hooks из активных слоёв конфигурации; проектный hook не заменяет глобальный. Поэтому одинаковый `SessionStart` в шести репозиториях только продублировал бы контекст и расход токенов.

В этом наборе локальные проектные hooks **намеренно не создаются по умолчанию**. Вместо этого:

- глобальный `SessionStart` читает exact selected record из `prompts/STAGES.md` и
  относящиеся `specs/*`/`docs/ARCHITECTURE.md` текущего репозитория;
- глобальный `SubagentStart` передаёт тот же компактный контекст проекта субагенту;
- глобальный `PreToolUse` блокирует небольшой набор необратимых команд;
- специфичная для проекта политика хранится в `AGENTS.md`, `AGENTS.override.md` и `.codex/rules/project.rules`.

`^Bash$` является каноническим matcher Codex и покрывает shell commands и unified exec независимо от Windows command override. Hook остаётся дополнительным guardrail; sandbox, approvals и execpolicy являются основными границами.

`session_context.py` разрешает каждый фиксированный документ относительно Git-root, отклоняет symlink/junction за пределы repository и читает только ограниченный префикс файла. Вывод принудительно переводится в UTF-8, чтобы Windows legacy console encoding не ломала JSON.

Pure parsing contract находится в `hooks/stage_selector.py` и переиспользуется
`session_context.py` и `tools/validate_project_overlay.py`. Hook отвечает за bounded context
projection, а read-only validator — за fail-visible structural preflight; расхождение правил
selector-а между ними считается regression.

Для stage-bound работы `prompts/STAGES.md` содержит ровно одну непустую строку `Stage ID` вне
fenced code block: 1–64 ASCII-символа из букв, цифр, `.`, `_`, `-`. Hook находит ровно один
Markdown heading вне fenced code block с этим ID как отдельным token в `prompts/STAGES.md` и
ставит bounded record первым в дополнительном контексте; весь catalog не загружается. Это context
projection, а не semantic validation DAG, prerequisites или evidence.

Fallback-цепочка детерминирована: repository без `prompts/STAGES.md` получает обычный bounded
project snapshot; существующий STAGES без valid unique selector либо oversized catalog выдаёт
`Stage context — DEGRADED` и не подставляет другую запись. Retry отсутствует. Агент обязан открыть
и проверить полный record вручную, если hook
пометил запись как усечённую или degraded; такой context не разрешает completion claim.

Поскольку Git-root ДЕВ совмещён с runtime-каталогом `~/.codex`, hook блокирует все формы принудительного `git clean`, включая раздельные flags `git clean -d -f -x`. Dry-run без `-f` / `--force` разрешён. Не запускай принудительный `git clean` в `~/.codex` вручную: игнорируемые runtime-файлы не восстанавливаются из Git.

## Когда добавлять локальный hook

Добавляй `<repo>/.codex/hooks.json` только тогда, когда нужна детерминированная автоматизация, специфичная для одного проекта, например:

- проверять схему миграции перед запуском команды базы данных;
- подмешивать автоматически сформированное состояние оборудования или устройства;
- запрещать конкретную production-команду CLI в одном репозитории;
- запускать локальный скрипт политики для особого формата сгенерированных файлов.

Не используй hook для того, что достаточно описать инструкцией в `AGENTS.md`.
