---
name: resume-project
description: Возобновить работу в существующем репозитории, прочитать canonical STAGES и ROADMAP и выбрать минимально необходимую следующую задачу.
---

1. Прочитай current selector и exact record из `prompts/STAGES.md`, `docs/ROADMAP.md`,
   `docs/ARCHITECTURE.md`, а также актуальные git status и diff.
2. Используй встроенного `explorer` только в том случае, если файлов состояния недостаточно.
3. Сверь claims завершения с Stage contract из `~/.codex/rules/governance.md`. Future dependency, отсутствующий runnable/E2E PASS evidence или mock/stub-only путь не считай completion; классифицируй как `blocked`, `scaffolded`, `implemented_unverified` или `partial`.
4. Укажи текущий этап, действительно завершённую работу, блокеры и одну лучшую следующую задачу.
5. Если selected record содержит `master-execution`, сверь embedded state revision/checkpoint с
   Git/worktree/source revision через `tools/master_execution.py`. Stale launcher, dirty/unknown
   state или missing evidence дают reconciliation/handoff, не предполагаемый progress.
6. Не приступай к реализации, если пользователь не попросил её продолжить. Один явный запуск
   master уже разрешает автоматическое продолжение его однозначных безопасных внутренних slices.
7. Если реализация запрошена, передай работу процессу `$implement-stage`.
