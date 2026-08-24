# Полный пофайловый реестр контекста

Дата инвентаризации: 2026-08-24. База: `MANIFEST.txt` ветки `docs/global-context-dependency-map`.

Реестр охватывает все 259 tracked-файлов глобального DEV-репозитория. Для каждого файла указано, как он участвует в создании, выборе, проекции, проверке или объяснении контекста. Runtime-файлы вне Git перечислены отдельно.

## 1. Корень репозитория — 9 файлов

| Файл | Роль в контексте |
|---|---|
| `.gitignore` | отделяет canonical files от cache, build, worktree и machine-local state |
| `AGENTS.md` | глобальная постоянно обнаруживаемая точка входа и порядок приоритетов |
| `config.ai-dev-team.recommended.toml` | безопасный версионируемый baseline runtime config без credentials |
| `hooks.json` | декларативно связывает события Codex с hook-скриптами |
| `install-global.ps1` | синхронизирует managed skills и запускает глобальные проверки |
| `install-project.ps1` | проецирует выбранный preset в новый/пустой project overlay |
| `MANIFEST.txt` | точный ожидаемый набор tracked-файлов; вход validator-а |
| `QUICKSTART.md` | короткий операционный маршрут установки и проверки |
| `README.md` | главный human-readable индекс архитектуры, команд и каталогов |

## 2. Глобальные субагенты — 13 файлов

Все файлы `agents/*.toml` обнаруживаются как глобальные custom roles. Они добавляют role-specific developer instructions к наследуемому config и контексту родителя.

| Файл | Граница роли |
|---|---|
| `agents/architect.toml` | архитектура и service boundaries |
| `agents/backend_engineer.toml` | backend/API/business logic |
| `agents/beginner_mentor.toml` | учебное объяснение выполненного изменения |
| `agents/database_engineer.toml` | schema/migration/query/data invariants |
| `agents/devops_engineer.toml` | CI/CD, containers и operations |
| `agents/docs_researcher.toml` | проверка актуальной официальной документации |
| `agents/frontend_engineer.toml` | frontend UI и browser behavior |
| `agents/performance_engineer.toml` | profiling и performance bottlenecks |
| `agents/planner.toml` | план, зависимости и acceptance criteria |
| `agents/release_manager.toml` | read-only release readiness |
| `agents/reviewer.toml` | read-only correctness/regression review |
| `agents/security_reviewer.toml` | read-only security boundaries review |
| `agents/test_engineer.toml` | reproduction и regression tests |

## 3. Hooks — 3 файла

| Файл | Триггер/выход |
|---|---|
| `hooks.json` | `SessionStart`, `SubagentStart`, `PreToolUse(Bash)` → команды hooks |
| `hooks/session_context.py` | читает bounded набор status/spec/plan/architecture и возвращает context payload |
| `hooks/guard_destructive.py` | проверяет shell input на известные destructive patterns и разрешает/отклоняет вызов |

## 4. Rules — 57 файлов

### 4.1 Корневой индекс и поперечные политики — 7

| Файл | Условие активации |
|---|---|
| `rules/README.md` | при любой маршрутизации rules; выбирает минимальный subset |
| `rules/ai-dev-team.rules` | базовый engineering contract |
| `rules/fallback-policy.md` | сбой preferred path/tool/model и необходимость fallback |
| `rules/governance.md` | изменение global/project living contract |
| `rules/model-routing.md` | выбор Luna/Terra/Sol и эскалация |
| `rules/node-package-management.md` | Node package manager, lockfile и install policy |
| `rules/word-pdf-academic.md` | Word/PDF/academic artifact workflow |

### 4.2 Режимы — 3

| Файл | Условие активации |
|---|---|
| `rules/modes/prototype.md` | быстрый ограниченный prototype |
| `rules/modes/standard.md` | обычная production-oriented работа |
| `rules/modes/strict.md` | повышенные assurance/risk требования |

### 4.3 SDLC — 10

| Файл | Этап |
|---|---|
| `rules/sdlc/README.md` | индекс SDLC |
| `rules/sdlc/requirements.md` | сбор и фиксация требований |
| `rules/sdlc/specification.md` | формальная спецификация |
| `rules/sdlc/architecture.md` | архитектурные решения |
| `rules/sdlc/design.md` | UX/UI/system design |
| `rules/sdlc/implementation.md` | реализация |
| `rules/sdlc/testing.md` | тестирование |
| `rules/sdlc/review.md` | review |
| `rules/sdlc/release.md` | release readiness |
| `rules/sdlc/maintenance.md` | сопровождение |

### 4.4 Spec-driven development — 3

| Файл | Роль |
|---|---|
| `rules/sdd/spec-driven-development.md` | общий SDD lifecycle |
| `rules/sdd/spec-authoring.md` | authoring contract для spec |
| `rules/sdd/spec-validation.md` | validation/acceptance contract |

### 4.5 Домены — 16

`rules/domains/README.md` — индекс. Остальные 15 файлов активируются только при наличии соответствующего домена в задаче:

```text
rules/domains/ai-ml.md
rules/domains/api.md
rules/domains/backend.md
rules/domains/database.md
rules/domains/desktop.md
rules/domains/devops.md
rules/domains/distributed.md
rules/domains/embedded.md
rules/domains/frontend.md
rules/domains/gpu-computing.md
rules/domains/mobile.md
rules/domains/networking.md
rules/domains/realtime.md
rules/domains/scientific-computing.md
rules/domains/security.md
```

### 4.6 Стеки — 18

`rules/stacks/README.md` — индекс. Остальные 17 файлов активируются по фактически используемой технологии:

```text
rules/stacks/arrow-parquet.md
rules/stacks/cloudflare.md
rules/stacks/docker.md
rules/stacks/fastapi.md
rules/stacks/mql5.md
rules/stacks/nextjs.md
rules/stacks/postgres.md
rules/stacks/pyside6.md
rules/stacks/python.md
rules/stacks/react.md
rules/stacks/rust.md
rules/stacks/svelte.md
rules/stacks/temporal.md
rules/stacks/typescript.md
rules/stacks/wasm.md
rules/stacks/web-audio.md
rules/stacks/yjs.md
```

## 5. Глобальные docs — 23 файла

| Файл | Роль/потребитель |
|---|---|
| `docs/AI_PLAN.md` | текущий план глобального DEV-репозитория; hook-compatible |
| `docs/AI_STATUS.md` | подтверждённое текущее состояние; первый файл session hook |
| `docs/ARCHITECTURE.md` | устойчивые границы глобальной системы; session hook |
| `docs/AUTOMATION_EXTENSIONS.md` | каталог возможных расширений automation |
| `docs/CONTEXT_COMPATIBILITY.md` | правила совместимости global ↔ project overlay |
| `docs/CONTEXT_DEPENDENCY_MAP.md` | системный анализ потоков и конфликтов |
| `docs/CONTEXT_FILE_INVENTORY.md` | этот исчерпывающий пофайловый реестр |
| `docs/CONTEXT_POLICY.md` | что грузить автоматически, по требованию или не грузить |
| `docs/DECISIONS.md` | журнал принятых глобальных решений |
| `docs/DESIGN.md` | общая design policy; receipt-specific design исключён из global scope |
| `docs/HOOK_POLICY.md` | additive hooks и запрет ненужного project duplication |
| `docs/LEARNING_LOG.md` | исторический журнал уроков; on-demand, не runtime authority |
| `docs/MCP_CATALOG.md` | governance-каталог MCP и fallback, не список фактически активных servers |
| `docs/MENTORING_GUIDE.md` | правила обучающего handoff |
| `docs/ORCHESTRATION_LATER.md` | отложенные orchestration ideas, не активный contract |
| `docs/PROJECT_FRAMEWORK.md` | состав и жизненный цикл project КАРКАСа |
| `docs/ROADMAP.md` | долгосрочные этапы глобального DEV-контура |
| `docs/SDD_GUIDE.md` | практическая навигация по SDD rules/specs |
| `docs/SECURITY.md` | глобальная security baseline |
| `docs/TEAM_ARCHITECTURE.md` | роли и взаимодействие AI Dev Team |
| `docs/TEAM_COMMANDS.md` | команды запуска/проверки team workflows |
| `docs/VERIFY_SETUP.md` | проверяемые post-install checks |
| `docs/WORKFLOW.md` | end-to-end engineering workflow |

## 6. Backlog — 7 файлов

Backlog не загружается автоматически. Каждый файл становится входом только при выборе соответствующей идеи:

```text
backlog/README.md                    # индекс и статус идей
backlog/blockchain-tooling.md        # идея blockchain tooling
backlog/deye-digital-twin.md         # идея digital twin
backlog/dune2-bot.md                 # идея bot
backlog/low-level-os-lab.md          # идея low-level lab
backlog/nonogram-solver.md           # идея solver
backlog/video-compiler.md            # идея video compiler
```

## 7. Specs — 6 файлов

| Файл | Роль/статус |
|---|---|
| `specs/README.md` | индекс specs; второй файл session hook |
| `specs/system.spec.md` | системные инварианты; третий файл session hook |
| `specs/features/codex-home-consolidation.spec.md` | перенос canonical DEV home |
| `specs/features/full-workspace-governance.spec.md` | аудит и согласование всех репозиториев |
| `specs/features/global-codex-normalization.spec.md` | историческая superseded normalization spec |
| `specs/features/project-overlay-rollout.spec.md` | rollout project overlays |

## 8. Canonical skill sources — 25 файлов

### 8.1 `bootstrap-project-framework` — 2

| Файл | Роль |
|---|---|
| `skill-sources/bootstrap-project-framework/SKILL.md` | trigger, scope и workflow skill |
| `skill-sources/bootstrap-project-framework/agents/openai.yaml` | UI/name/description metadata |

### 8.2 `dev-karkas` — 17

| Файл | Роль |
|---|---|
| `skill-sources/dev-karkas/SKILL.md` | главный router skill |
| `skill-sources/dev-karkas/README.md` | human-readable overview |
| `skill-sources/dev-karkas/agents/openai.yaml` | UI metadata |
| `skill-sources/dev-karkas/references/KARKAS.md` | основная модель framework |
| `skill-sources/dev-karkas/references/PROJECT_FILES.md` | обязательные/условные project files |
| `skill-sources/dev-karkas/references/AUTONOMY_POLICY.md` | границы автономии и approval |
| `skill-sources/dev-karkas/references/GIT_WORKFLOW.md` | branch/commit/merge/push contract |
| `skill-sources/dev-karkas/references/ARCHITECTURE_POLICY.md` | архитектурные критерии |
| `skill-sources/dev-karkas/references/STATUS_WORKFLOW.md` | синхронизация plan/status/roadmap |
| `skill-sources/dev-karkas/references/FALLBACK_POLICY.md` | fallback decision tree |
| `skill-sources/dev-karkas/references/NOTION_INTAKE.md` | перевод идеи из Notion в backlog/spec |
| `skill-sources/dev-karkas/references/PROJECT_REGISTRY.md` | registry contract для проектов |
| `skill-sources/dev-karkas/references/PROMPT_TEMPLATE.md` | шаблон stage/task prompt |
| `skill-sources/dev-karkas/references/SECURITY_BASELINE.md` | project security minimum |
| `skill-sources/dev-karkas/references/TESTING_POLICY.md` | required tests/DoD |
| `skill-sources/dev-karkas/scripts/install.ps1` | установка framework assets |
| `skill-sources/dev-karkas/scripts/validate.ps1` | локальная проверка framework |

### 8.3 Узкие skills — 6

```text
skill-sources/explain-change/SKILL.md
skill-sources/fix-bug/SKILL.md
skill-sources/implement-stage/SKILL.md
skill-sources/plan-stage/SKILL.md
skill-sources/resume-project/SKILL.md
skill-sources/review-change/SKILL.md
```

Каждый из этих файлов одновременно задаёт trigger, ограничения и workflow одноимённой операции. Runtime-проекция всех 25 файлов — `C:\Users\aleks\.agents\skills` через `tools/sync_global_skills.py`.

## 9. Presets — 104 файла

Обозначения ролей, применимые к каждому exact path ниже:

- `AGENTS.md` — project root living contract;
- `AGENTS.override.md` — subtree-specific override;
- `.codex/config.toml` — project config delta;
- `.codex/agents/*.toml` — project-specific role;
- `.codex/rules/project.rules` — minimal project-only rules;
- `.agents/skills/*/SKILL.md` — stage skill;
- `docs/AI_STATUS.md` / `AI_PLAN.md` / `ROADMAP.md` — состояние, ближайший план, долгий план;
- `docs/ARCHITECTURE.md` / `DECISIONS.md` / `MCP.md` — границы, ADR log, project MCP choices;
- `specs/README.md` / `system.spec.md` — spec index и system contract.

### 9.1 `field-lab` — 16

```text
presets/field-lab/AGENTS.md
presets/field-lab/.agents/skills/field-lab-stage/SKILL.md
presets/field-lab/.codex/config.toml
presets/field-lab/.codex/rules/project.rules
presets/field-lab/.codex/agents/electromagnetics_engineer.toml
presets/field-lab/.codex/agents/math_verifier.toml
presets/field-lab/.codex/agents/numerical_methods_engineer.toml
presets/field-lab/.codex/agents/scientific_visualization_engineer.toml
presets/field-lab/docs/AI_PLAN.md
presets/field-lab/docs/AI_STATUS.md
presets/field-lab/docs/ARCHITECTURE.md
presets/field-lab/docs/DECISIONS.md
presets/field-lab/docs/MCP.md
presets/field-lab/docs/ROADMAP.md
presets/field-lab/specs/README.md
presets/field-lab/specs/system.spec.md
```

### 9.2 `music-sequencer` — 17

```text
presets/music-sequencer/AGENTS.md
presets/music-sequencer/audio/AGENTS.override.md
presets/music-sequencer/.agents/skills/music-sequencer-stage/SKILL.md
presets/music-sequencer/.codex/config.toml
presets/music-sequencer/.codex/rules/project.rules
presets/music-sequencer/.codex/agents/audio_dsp_engineer.toml
presets/music-sequencer/.codex/agents/realtime_audio_engineer.toml
presets/music-sequencer/.codex/agents/sequencer_model_engineer.toml
presets/music-sequencer/.codex/agents/wasm_audio_engineer.toml
presets/music-sequencer/docs/AI_PLAN.md
presets/music-sequencer/docs/AI_STATUS.md
presets/music-sequencer/docs/ARCHITECTURE.md
presets/music-sequencer/docs/DECISIONS.md
presets/music-sequencer/docs/MCP.md
presets/music-sequencer/docs/ROADMAP.md
presets/music-sequencer/specs/README.md
presets/music-sequencer/specs/system.spec.md
```

### 9.3 `receipt-price-db` — 17

```text
presets/receipt-price-db/AGENTS.md
presets/receipt-price-db/data/AGENTS.override.md
presets/receipt-price-db/.agents/skills/receipt-price-db-stage/SKILL.md
presets/receipt-price-db/.codex/config.toml
presets/receipt-price-db/.codex/rules/project.rules
presets/receipt-price-db/.codex/agents/arrow_data_engineer.toml
presets/receipt-price-db/.codex/agents/product_normalization_engineer.toml
presets/receipt-price-db/.codex/agents/receipt_data_quality_engineer.toml
presets/receipt-price-db/.codex/agents/vision_ocr_engineer.toml
presets/receipt-price-db/docs/AI_PLAN.md
presets/receipt-price-db/docs/AI_STATUS.md
presets/receipt-price-db/docs/ARCHITECTURE.md
presets/receipt-price-db/docs/DECISIONS.md
presets/receipt-price-db/docs/MCP.md
presets/receipt-price-db/docs/ROADMAP.md
presets/receipt-price-db/specs/README.md
presets/receipt-price-db/specs/system.spec.md
```

### 9.4 `trading-terminal` — 20

```text
presets/trading-terminal/AGENTS.md
presets/trading-terminal/backend/AGENTS.override.md
presets/trading-terminal/frontend/AGENTS.override.md
presets/trading-terminal/.agents/skills/trading-terminal-stage/SKILL.md
presets/trading-terminal/.codex/config.toml
presets/trading-terminal/.codex/rules/project.rules
presets/trading-terminal/.codex/agents/mql_engineer.toml
presets/trading-terminal/.codex/agents/observability_engineer.toml
presets/trading-terminal/.codex/agents/quant_engineer.toml
presets/trading-terminal/.codex/agents/temporal_engineer.toml
presets/trading-terminal/.codex/agents/timescale_engineer.toml
presets/trading-terminal/.codex/agents/wasm_engineer.toml
presets/trading-terminal/docs/AI_PLAN.md
presets/trading-terminal/docs/AI_STATUS.md
presets/trading-terminal/docs/ARCHITECTURE.md
presets/trading-terminal/docs/DECISIONS.md
presets/trading-terminal/docs/MCP.md
presets/trading-terminal/docs/ROADMAP.md
presets/trading-terminal/specs/README.md
presets/trading-terminal/specs/system.spec.md
```

### 9.5 `tutor-platform` — 18

```text
presets/tutor-platform/AGENTS.md
presets/tutor-platform/collaboration/AGENTS.override.md
presets/tutor-platform/.agents/skills/tutor-platform-stage/SKILL.md
presets/tutor-platform/.codex/config.toml
presets/tutor-platform/.codex/rules/project.rules
presets/tutor-platform/.codex/agents/calendar_integration_engineer.toml
presets/tutor-platform/.codex/agents/collaboration_engineer.toml
presets/tutor-platform/.codex/agents/education_content_engineer.toml
presets/tutor-platform/.codex/agents/pwa_mobile_engineer.toml
presets/tutor-platform/.codex/agents/realtime_comms_engineer.toml
presets/tutor-platform/docs/AI_PLAN.md
presets/tutor-platform/docs/AI_STATUS.md
presets/tutor-platform/docs/ARCHITECTURE.md
presets/tutor-platform/docs/DECISIONS.md
presets/tutor-platform/docs/MCP.md
presets/tutor-platform/docs/ROADMAP.md
presets/tutor-platform/specs/README.md
presets/tutor-platform/specs/system.spec.md
```

### 9.6 `wifi-share` — 16

```text
presets/wifi-share/AGENTS.md
presets/wifi-share/server/AGENTS.override.md
presets/wifi-share/.agents/skills/wifi-share-stage/SKILL.md
presets/wifi-share/.codex/config.toml
presets/wifi-share/.codex/rules/project.rules
presets/wifi-share/.codex/agents/network_protocol_engineer.toml
presets/wifi-share/.codex/agents/wifi_security_engineer.toml
presets/wifi-share/.codex/agents/windows_network_engineer.toml
presets/wifi-share/docs/AI_PLAN.md
presets/wifi-share/docs/AI_STATUS.md
presets/wifi-share/docs/ARCHITECTURE.md
presets/wifi-share/docs/DECISIONS.md
presets/wifi-share/docs/MCP.md
presets/wifi-share/docs/ROADMAP.md
presets/wifi-share/specs/README.md
presets/wifi-share/specs/system.spec.md
```

## 10. Templates — 3 файла

| Файл | Роль после явного применения |
|---|---|
| `templates/DEV_LOG_TEMPLATE.md` | основа project development log |
| `templates/LEARNING_LOG_TEMPLATE.md` | основа project learning log |
| `templates/SPEC_TEMPLATE.md` | основа новой feature/system spec |

## 11. Tools и их tests — 10 файлов

| Файл | Контекстный эффект |
|---|---|
| `tools/normalize_user_codex.py` | строит/применяет план нормализации user Codex layout |
| `tools/reconcile_project_framework.py` | inspect + gap plan для existing project overlay |
| `tools/sync_global_skills.py` | source/runtime skill parity и backup перед заменой |
| `tools/validate_context.py` | проверяет repository-wide links, manifest и contract |
| `tools/validate_global_codex.py` | проверяет canonical global home и managed skills |
| `tools/validate_project_overlay.py` | проверяет отдельный project overlay |
| `tools/test_reconcile_project_framework.py` | regression tests reconcile planning |
| `tools/test_sync_global_skills.py` | regression tests sync/hash/backup behavior |
| `tools/test_validate_global_codex.py` | regression tests global validator |
| `tools/test_validate_project_overlay.py` | regression tests project validator |

## 12. Runtime-файлы вне MANIFEST

Эти пути влияют на текущую сессию, но не принадлежат canonical tracked set:

| Путь | Класс | Почему не включён в Git |
|---|---|---|
| `C:\Users\aleks\.codex\config.toml` | active runtime config | machine-local settings, trust и enabled servers/plugins |
| `C:\Users\aleks\.agents\skills\**` | managed skill projection | генерируется из `skill-sources`, проверяется hashes/file set |
| `C:\Users\aleks\.codex\skills\.system\**` | product-managed skills | обновляется поставщиком Codex |
| `C:\Users\aleks\.codex\plugins\**` | plugin packages/cache | внешний runtime и cache, не DEV source |
| `C:\Users\aleks\.codex\auth*` и credentials | secrets | никогда не документировать содержимое и не переносить в Git |
| `C:\Users\aleks\.codex\sessions\**` | session state | transient/private execution history |
| `C:\Users\aleks\.codex\state*`, `cache*`, logs | runtime state | воспроизводимо или приватно, не policy source |
| `<project>\.codex\config.toml` | trusted project delta | принадлежит соответствующему project repo |
| `<project>\.codex\agents\**` | project roles | принадлежит project overlay |
| `<project>\.agents\skills\**` | project skills | принадлежит project overlay |
| `<project>\AGENTS*.md` | local discovered rules | принадлежит project repo и имеет более высокий local priority |

## 13. Полнота

Проверка полноты считается успешной, если:

1. отсортированный `git ls-files` совпадает с `MANIFEST.txt`;
2. число tracked-файлов равно 259;
3. каждый tracked path попадает ровно в одну секцию 1–11;
4. runtime dependencies из секции 12 не ошибочно объявлены canonical source;
5. `validate_context.py`, `validate_global_codex.py` и unit tests проходят.
