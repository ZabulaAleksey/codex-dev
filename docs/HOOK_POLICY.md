# Политика hooks

## Почему основной hook глобальный

Codex загружает все подходящие hooks из активных слоёв конфигурации; проектный hook не заменяет глобальный. Поэтому одинаковый `SessionStart` в шести репозиториях только продублировал бы контекст и расход токенов.

В этом наборе локальные проектные hooks **намеренно не создаются по умолчанию**. Вместо этого:

- глобальный `SessionStart` сначала классифицирует stage state; для canonical/migrated он читает
  exact selected record и относящиеся `specs/*`/`docs/ARCHITECTURE.md`, для brownfield/conflict/none
  выдаёт только compact fail-closed routing result;
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

Selected Continuous Master record может включать bounded `master-execution` block; record limit
равен 6000 chars внутри общего 9000-char hook budget. Hook только проецирует block, а schema,
graph/evidence/recovery semantics валидируют project validator и `tools/master_execution.py`.

Fallback-цепочка детерминирована: legacy/mixed получает `migration_required`, отсутствие всех
stage owners — `no_stage_state`, invalid/conflicting/oversized state — `Stage routing — DEGRADED`.
Ни один из них не подставляет другую запись и имеет `execution_allowed=false`. Hook остаётся
advisory exit `0` для стабильности host, не materialize-ит state и не исполняет suggested argv.
Такой degraded context не разрешает completion claim до явного canonical validation.

Hook блокирует все формы принудительного `git clean`, включая раздельные flags
`git clean -d -f -x`. Dry-run без `-f` / `--force` разрешён. Особенно не инициализируй Git и не
запускай cleanup в installed `~/.codex`: runtime-файлы не принадлежат source repository и не
восстанавливаются из Git. Canonical DEV source очищается только после обычной проверки status/diff.

## Когда добавлять локальный hook

Добавляй `<repo>/.codex/hooks.json` только тогда, когда нужна детерминированная автоматизация, специфичная для одного проекта, например:

- проверять схему миграции перед запуском команды базы данных;
- подмешивать автоматически сформированное состояние оборудования или устройства;
- запрещать конкретную production-команду CLI в одном репозитории;
- запускать локальный скрипт политики для особого формата сгенерированных файлов.

Не используй hook для того, что достаточно описать инструкцией в `AGENTS.md`.
