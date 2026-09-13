# Глобальный router Codex и ДЕВ / КАРКАС

Этот файл задаёт обязательные инварианты и маршрутизацию. Полные contracts принадлежат указанным
`rules/*`, `docs/*`, SPEC и Skills; не копируй их в project overlays. Прямой запрос пользователя
приоритетнее project `AGENTS.md`, project instructions — этого router, если более конкретное
правило не ослабляет безопасность или явно принятый контракт.

## 1. Канонические границы

- Global DEV source repository разрешается через `DEV_SOURCE_ROOT`; current canonical default —
  `~/codex-dev`. Active Codex runtime/user layer разрешается через `CODEX_HOME`; current default —
  `~/.codex`, и это не canonical Git working tree.
- Product repositories — независимые Git roots `${PROJECTS_ROOT}/<project>`; current default
  `PROJECTS_ROOT=~`. Filesystem location не означает global DEV policy inheritance. Product
  принимает DEV только через valid project-local `.codex/dev-project.toml`. Exact line
  `Global DEV bridge: enabled` в `AGENTS.md` остаётся human-readable declaration, но сама по
  себе policy inheritance не включает.
- Versioned Skills: `<dev-root>/skill-sources`; `~/.agents/skills` — только hash-verified runtime
  materialization, не второй source of truth. `skill-sources` не копируется в `~/.codex`.
- Runtime state Codex, credentials, sessions, cache, plugins и active `~/.codex/config.toml` не
  принадлежат Git repository ДЕВ. Не перезаписывай `config.toml`; меняй только
  `config.ai-dev-team.recommended.toml` и templates, если задача прямо этого требует.
- Наличие agent/hook/Skill/MCP файла не доказывает runtime activation; перед зависимостью от
  capability проверь active configuration/discovery без вывода secrets.
- В документации используй переносимые пути от `~`, не machine-specific абсолютные пути.

Фактическое состояние задают текущий repository/worktree, code и verification evidence.
Утверждённые SPEC/ADR задают требования. Status, prompt, чат и внешняя projection не могут
переопределять эти источники.

## 2. Классифицируй и загружай минимальный контекст

Перед существенной задачей определи: `SIMPLE | STANDARD | COMPLEX`, prototype/production, этап
SDLC, домен, стек и соответствующую SPEC. Сначала прочитай `~/.codex/rules/README.md`, затем
только применимые mode/SDLC/domain/stack rules и `rules/model-routing.md`.

- `SIMPLE`: локальное очевидное изменение; без AI Dev Team, обычно без SPEC и субагентов.
- `STANDARD`: одна подсистема/обычная feature или bugfix; 0–1 полезный specialist, SPEC и
  `rules/sdd/spec-driven-development.md` при существенном поведении.
- `COMPLEX`: несколько подсистем/архитектура/security/performance/существенные неизвестные;
  `rules/modes/strict.md`, полная SPEC, минимально достаточная команда и профильные review gates.

Каскад файлового контекста:

```text
ближайший AGENTS.override.md / module instructions
→ project AGENTS.md
→ ~/.codex/AGENTS.md
→ global Codex configuration
```

Порядок загрузки: ближайшие instructions → выбранные rules → затронутая SPEC → один выбранный
stage record → относящиеся architecture/decisions/design/security → code/tests/diff. Current plan,
status, blockers/evidence и NEXT находятся в выбранном STAGES record. Не загружай целиком архивы prompts, все rules/specs/fixtures или
старые reports.

Для stage-bound project task ровно одна строка `- Stage ID: <stable-id>` в `prompts/STAGES.md`
выбирает ровно один heading в этом же файле, где ID является отдельным token. Загружай только
выбранный record. Invalid/missing/ambiguous selector даёт visible `DEGRADED`; прочитай полный record
вручную и не используй completion claim, пока контракт не проверен.

Если selected record объявляет fenced `master-execution` state, используй Continuous Master
Execution из `rules/governance.md` и deterministic `tools/master_execution.py`. После одного явно
запущенного `master_prompt` автоматически переходи между единственными dependency-ready
backward-complete slices. Останавливайся только по canonical stop condition; checkpoint commit сам
по себе не stop. Invalid/stale graph, launcher или adapter facts дают visible fail-closed outcome.

После разрешения live stage используй `skill-sources/registry.toml` и bounded
`tools/spec_execution.py` для relevant-only Skill/capability route, trace/placement gates и
Automation Promotion Review. Не загружай Skills до известного stage/scope и не превращай
registry/decision в автоматическое исполнение commands или policy/model mutation.

## 3. Обязательные cross-cutting routes

- Structure, lifecycle, source ownership, stages, documentation/evidence, tool boundaries:
  `~/.codex/rules/governance.md`.
- `STANDARD`/`COMPLEX` behavior: `~/.codex/rules/sdd/spec-driven-development.md` и затронутая SPEC.
- Retry/fallback/degraded/recovery/side effects: `~/.codex/rules/fallback-policy.md`.
- Dependency manager/lockfile/cache/clean restore: `~/.codex/rules/dependency-management.md`.
- Node/Corepack/npm/pnpm/Yarn: `~/.codex/rules/node-package-management.md`.
- Model/subagent selection: `~/.codex/rules/model-routing.md`; выбранная пользователем модель
  главного агента не меняется молча.
- User-facing product architecture/strings/locale/RTL: `~/.codex/rules/i18n-l10n.md`. Язык
  project context не определяет product language/locale.
- External/vendor-bound subsystems and replaceable implementations:
  `~/.codex/rules/replaceable-modules.md`; project хранит только ports/adapters, исключения и
  evidence, а не копию глобального contract.
- Дорогие AI-policies, agent/retrieval/reuse contours, experiments и human handoff economics:
  `~/.codex/rules/ai-policy-profiling.md`; opt-in Observe предшествует tuning.
- Stage-first capability/Skill routing, traceability, context economy и automation promotion:
  `specs/features/specification-execution-pipeline.spec.md` и `tools/spec_execution.py`.
- Global/project КАРКАС, audit, plans/status/roadmap/stages, Notion ideas и synchronization:
  Skill `dev-karkas` и только нужные references.

<!-- AI-DEV-TEAM-BACKEND-DX-POLICY -->
Для создания, аудита или изменения backend developer workflow прочитай
`~/.codex/rules/backend-dx.md` и используй global Skill `backend-dx-audit`. Переиспользуй
существующие package manager, task runner, test runner, ORM, migrations и orchestration.
Project хранит только `Backend DX Delta` в `docs/project-context.md`; destructive DB/resource и
production actions deny-by-default.

## 4. Git, сохранность данных и scope

Для read-only анализа branch не нужен. Перед файловыми изменениями:

1. определи Git root, branch/status/diff и сохрани unrelated dirty/untracked/merge work;
2. прочитай project `docs/git-flow.md`, если он существует;
3. не изменяй напрямую `main`, `master` или `dev`; используй `feature/<task>` / `fix/<task>` либо
   project convention;
4. continuation того же master/track переиспользует его worktree; независимый parallel writer
   автоматически получает отдельную branch/worktree, а ownership overlap требует integration
   checkpoint; read-only task не создаёт worktree механически;
5. не выполняй merge, worktree deletion, PR, push, force push, history rewrite или production
   deployment без явного разрешения.

Для move/rename/migration сначала проверь source/target Git state, canonical role collisions,
dirty/merge state и stale references. Сохрани unique content и recoverable rollback point; не
перезаписывай одноимённый канон автоматически и не удаляй backup до интеграции и стабильной
проверки. После move проверь paths/imports/hooks/config/CI/docs, conflict markers, diff/status и
релевантные tests.

Не выполняй destructive reset, массовое удаление untracked/runtime data, credential/config rewrite
или необратимую data migration без точного target, backup/recovery contract и явного разрешения.
Никогда не инициализируй Git и не запускай destructive cleanup в `~/.codex`: там находятся
runtime credentials, sessions, cache, plugins и active config. Global managed artifacts обновляет
только manifest-driven installer с ownership ledger и rollback.

## 5. ДЕВ / КАРКАС и project overlay

Используй `dev-karkas`, когда задача относится к bootstrap/audit/restructure, `AGENTS.md`,
automation, architecture/security/testing/fallback policy, SPEC, state/stages, Notion intake или
completion synchronization. Режим Skill выбирай по задаче: bootstrap, audit, maintain,
idea-intake, prompt-build или execute.

Для active full staged product overlay содержательными canonical files являются:

- `AGENTS.md`;
- `prompts/STAGES.md`;
- `docs/ROADMAP.md`;
- `docs/ARCHITECTURE.md`;
- `docs/DECISIONS.md`;
- `docs/LEARNING_LOG.md`;
- `docs/project-context.md`.

Не создавай placeholders механически. `DESIGN.md`, `SECURITY.md`, `TESTING.md`,
`TRACEABILITY.md`, `DEPENDENCIES.md`, `API.md`, `DATA_MODEL.md`, `PRIVACY.md` и `FALLBACKS.md`
создавай только при соответствующей поверхности. Дополняй существующий canonical owner; новый
долговечный non-canonical Markdown помещай в `docs/notes/<topic>.md`. Не создавай второй status,
plan, architecture, design, decision, learning или workflow source.

Brownfield repository: до framework bootstrap/refresh запусти read-only
`tools/reconcile_project_framework.py`, зафиксируй compatibility matrix в
`docs/CONTEXT_COMPATIBILITY.md`, разреши `CONFLICT`, затем refresh,
`validate_project_overlay.py` и повтор baseline tests. Code/tests repository — source of truth;
`FORBIDDEN_TO_OVERWRITE` запрещает mutation. Pre-existing failures отделяй от regressions.

Когда пользователь просит «создай КАРКАС» или «автоматизацию контекста», дополнительно прочитай
`docs/PROJECT_FRAMEWORK.md`, `docs/CONTEXT_POLICY.md`, `docs/CONTEXT_COMPATIBILITY.md`; выполни
inspect → gap analysis → minimal delta, не реализацию продукта.

## 6. Stage contract и статусы

До реализации stage примени единственный полный Stage contract из `rules/governance.md`:
completed prerequisites/dependency DAG, входные evidence, runnable vertical slice, concrete
end-to-end scenario, PASS checks/evidence, допустимая полностью рабочая temporary implementation и
deferred future scope.

Future stage не может разблокировать primary path, обязательную инфраструктуру или verification
ранее закрытого stage. Mock/stub/fake/interface-only путь подтверждает `scaffolded`, но не
completion. Без обязательного evidence используй `blocked`, `scaffolded`, `partial` или
`implemented_unverified`; `completed`, `verified` и `DONE` требуют всех terminal gates.

## 7. Команда и inference budget

Используй минимальное число агентов с реальной пользой:

- `SIMPLE`: 0;
- `STANDARD`: обычно 0–1;
- `COMPLEX`: несколько только по независимым специализациям; architect/reviewer/security/performance
  не запускаются автоматически без соответствующего риска.

Read-only исследования можно параллелить. Writers получают явные owners и непересекающиеся файлы.
Агенты без явного `model` наследуют выбранную/default Codex model; явный pin используется только
для проверенной role-specific причины. Сначала повышай reasoning, затем model; premium режимы
`Sol XHigh`, `Sol Max`, `Ultra` требуют прямого разрешения. Экономия не отменяет SPEC, tests,
review и security gates.

## 8. Реализация и test contracts

Перед code change сопоставь requirement → SPEC/ADR → architecture → implementation → tests.
Не меняй architecture/public contract молча. Минимальный diff предпочтительнее косметического
refactor. Не добавляй agent/hook/MCP/Skill/dependency/technology без подтверждённого gap,
compatibility classification и bounded failure behavior.

Accepted unit/integration/component tests, fixtures, goldens и E2E scenarios — исполняемый
контракт/evidence. Не удаляй, не skip'ай, не ослабляй и не переписывай их в обычной реализации.
Contract change требует прямого запроса/утверждённой SPEC и отдельного согласованного изменения.

После functional changes выполняй релевантные unit, integration и component checks. E2E считается
закрытым только для живого `client → API/CLI → backend` либо эквивалентного consumer path; если
обязательный backend отсутствует, используй `BLOCKED_BY_BACKEND`. Не называй smoke/static/mock
evidence полноценным E2E. Команды бери из project manifests/README/CI/scripts, не выдумывай.

## 9. Документация и evidence

SPEC хранится в `specs/system.spec.md` или `specs/features/<feature>.spec.md`; prompt/plan не
заменяет requirements. Для `STANDARD`/`COMPLEX` существенного behavior SPEC обновляется до кода.
Architecture/decisions/design/security/testing/status меняй только при изменившихся фактах; не
создавай timestamp-only churn и не выдумывай evidence.

Перед завершением task/stage и после разрешённого merge выполни Completion Documentation
Synchronization Gate из `rules/governance.md`. Всегда проверь существующие README,
`prompts/STAGES.md`, `docs/ROADMAP.md`, затронутые SPEC,
architecture/decisions/design/security/testing/API/data/dependencies/fallback и используемые
traceability/changelog/dev-log sources. Устрани stale status, blockers, next-step, test counts и
ложные `merged/released/deployed` claims.

В handoff явно укажи, какие state-bearing документы обновлены и какие проверены без изменений.
`prompts/STAGES.md` — compact current execution truth, не action log. `docs/LEARNING_LOG.md` обновляй только
для evidence-backed повторно полезной диагностики; не записывай скрытые рассуждения и не дублируй
Git history.

Все действия, решения, доступы, ручные проверки и approval, которые должен выполнить пользователь,
до handoff фиксируй в selected `prompts/STAGES.md` record по контракту `rules/governance.md`:
stable ID, status/condition, точное безопасное действие, ожидаемое evidence и разблокируемый шаг.
Не оставляй такие обязательства только в чате; secret values в STAGES не записывай.

Для `STANDARD`/`COMPLEX` кратко объясняй существенные этапы, команды, изменения и проверки. Когда
задача подходит для самостоятельного повторения, дай 3–7 воспроизводимых действий. Подробный
`docs/notes/MENTORING_GUIDE.md` загружай только при существенной диагностике, учебной задаче или
явном запросе.

Project context по умолчанию веди на русском; identifiers, APIs, commands, paths, technologies и
machine keys не переводи. Другой основной язык — только по прямому запросу или внешнему contract.

## 10. Завершение

После файловых изменений:

1. выполни проверки по риску и acceptance/Definition of Done;
2. выполни Completion Documentation Synchronization Gate;
3. проверь final diff/status и отсутствие accidental secrets/runtime files/`LEARNING_LOG*` churn;
4. создай атомарный commit по project convention или Conventional Commits;
5. сообщи изменения, commands/evidence, pre-existing failures, ограничения, state-bearing документы
   обновлены или проверены без изменений.

Не повышай evidence выше факта: `implemented locally → validated locally → committed → pushed →
PR opened → merged → released/deployed`.

Для standalone task либо master integration/finalization boundary в обычной ветке заверши вопросом:

«Фича реализована. Проверяем работу, или я могу выполнить слияние (merge) с главной веткой?»

Для master/track integration/finalization boundary в отдельном worktree:

«Изолированная работа завершена. Могу ли я слить ветку в main и удалить временный worktree?»

Merge разрешён только после явного ответа: `Да, сливай`.

Не задавай этот вопрос после каждого внутреннего master slice. Пока master/track `partial`, создай
checkpoint, синхронизируй overall master state/NEXT и автоматически продолжай готовый slice либо
остановись с конкретной stop condition. Worktree сохраняется на весь coherent track.

## 11. Notion и идеи

Для явно запущенного queue prompt применяй `~/.codex/rules/prompt-queue-lifecycle.md`
и read-only guard `~/.codex/tools/prompt_queue.py` до любой cleanup mutation.
Plain repository без explicit DEV bridge не подключай к Prompt Queue и не интерпретируй команду
`Продолжай` как global DEV resume. Project name/path разрешай через `tools/dev_paths.py`, а не через
предполагаемый workspace path.

Для идей/backlog/requirements из Notion используй connected Notion и `dev-karkas` workflow.
Сначала найди project mapping и проверь code, AGENTS, SPEC, DESIGN, ROADMAP,
STAGES и decisions на duplicate/already implemented. Жизненный цикл:
`IDEA → REFINED → PROMPT_READY → APPROVED → IMPLEMENTING → DONE`, с дополнительными
`NEEDS_RESEARCH`, `NEEDS_DECISION`, `DUPLICATE`, `ALREADY_IMPLEMENTED`, `BLOCKED`.

Сырую идею можно довести до `PROMPT_READY`, но не реализовывать без явной команды, `APPROVED` или
разрешающей project policy. Не удаляй исходные идеи и не повышай их до `DONE` без code/evidence.
