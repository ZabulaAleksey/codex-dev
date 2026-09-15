# Реестр файлов глобального контекста

## Prompt queue extension

- `rules/prompt-queue-lifecycle.md`: единственный policy owner.
- `specs/features/prompt-queue-lifecycle.spec.md`: PQ acceptance mapping.
- `tools/prompt_queue.py`, `tools/test_prompt_queue.py`: guard/CLI/receipt verifier и tests.


Дата проверки: 2026-09-10.

Точный пофайловый состав Git-контекста задаёт `MANIFEST.txt`. Этот документ объясняет роль каждого класса файлов; любой tracked-файл обязан одновременно присутствовать в manifest и в одной из категорий ниже.

## Корень

| Путь | Роль |
|---|---|
| `AGENTS.md` | единственный global instruction router |
| `.gitignore` | allowlisted граница canonical source и local generated/secrets |
| `README.md`, `QUICKSTART.md` | human-readable навигация и проверка |
| `config.ai-dev-team.recommended.toml` | безопасное предложение конфигурации без credentials |
| `hooks.json` | event → hook wiring |
| `install-global.ps1`, `install-global.sh` | platform entry points source → installed layer; dry-run поддерживается |
| `tools/install_global.py` | manifest policy, protected paths, ownership ledger, transaction/rollback и validation sequence |
| `MANIFEST.txt` | точный tracked source file set и верхняя allowlist-граница installer |

Именованные project installers, backlog и project inventory в active global root запрещены.

## Автоматически и условно загружаемый слой

| Путь | Роль |
|---|---|
| `agents/*.toml` | универсальные роли субагентов |
| `hooks/*.py` | bounded session context и safety checks |
| `rules/ai-dev-team.rules` | shell command policy |
| `rules/README.md` | router по режиму, домену, стеку и SDLC |
| `rules/governance.md`, `rules/model-routing.md`, `rules/fallback-policy.md`, `rules/dependency-management.md`, `rules/backend-dx.md`, `rules/i18n-l10n.md` | общие инженерные контракты |
| `rules/modes/*.md` | режим выполнения |
| `rules/domains/*.md` | универсальные доменные ограничения |
| `rules/stacks/*.md` | правила применимого технологического стека |
| `rules/sdd/*.md` | specification-driven workflow |

Каждый файл в этих каталогах выбирается router-ом по текущей задаче; каталог целиком в prompt не подмешивается.
Для stage-bound задачи `rules/governance.md` и выбранный record из project
`docs/STAGES.md` добавляются явно; остальные stages не загружаются. Session hook использует
ровно одну строку `- Stage ID: <stable-id>` из того же `docs/STAGES.md`, exact unique heading selector и visible
`DEGRADED` result при ошибке явного selector.

## Skills

| Путь | Роль |
|---|---|
| `skill-sources/<skill>/SKILL.md` | versioned trigger и workflow |
| `skill-sources/<skill>/references/**` | on-demand policy/reference |
| `skill-sources/<skill>/scripts/**` | воспроизводимая automation |
| `skill-sources/<skill>/README.md` | human documentation |
| `~/.agents/skills/<skill>/**` | runtime projection, не tracked этим repository |

`tools/sync_global_skills.py` и tests обеспечивают hash parity source/runtime.
`backend-dx-audit` является procedural consumer канонического
`rules/backend-dx.md`, а не второй копией policy. Project-specific Skills принадлежат project repository.

## Канонические документы

| Путь | Роль |
|---|---|
| `docs/STAGES.md` | selector, текущее состояние, ближайший план, blockers, evidence и `NEXT` |
| `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/DESIGN.md`, `docs/TESTING.md` | устойчивые глобальные границы и verification contract |
| `docs/PROJECT_FRAMEWORK.md` | contract project КАРКАСА |
| `docs/CONTEXT_POLICY.md`, `docs/CONTEXT_COMPATIBILITY.md` | загрузка и reconciliation |
| `docs/HOOK_POLICY.md`, `docs/MCP_CATALOG.md` | governance hooks/MCP |
| `docs/ROADMAP.md`, `docs/DECISIONS.md`, `docs/WORKFLOW.md` | этапы, решения и процесс |
| `docs/TEAM_ARCHITECTURE.md`, `docs/VERIFY_SETUP.md` | роли и verification |

## Вспомогательные документы

Все долговечные неканонические материалы находятся в `docs/notes/`:

- `AUTOMATION_EXTENSIONS.md`;
- `CONTEXT_DEPENDENCY_MAP.md`;
- `CONTEXT_FILE_INVENTORY.md`;
- `LEARNING_LOG.md`;
- `MENTORING_GUIDE.md`;
- `ORCHESTRATION_LATER.md`;
- `SDD_GUIDE.md`;
- `TEAM_COMMANDS.md`.

Они загружаются только по явной необходимости и не становятся вторым источником status/plan/architecture.

## Specifications и templates

| Путь | Роль |
|---|---|
| `specs/system.spec.md` | system contract глобального framework |
| `specs/README.md` | индекс SPEC |
| `specs/features/*.spec.md` | проверяемая история изменения framework |
| `templates/*.md` | project-agnostic формы SPEC, canonical STAGES, decisions, журналов и Backend DX delta |
| `templates/prompt-modes/*.md` | пользовательские opt-in prompts для экспериментов и игр; не DEV rules и не загружаются router-ом автоматически |

Historical `SUPERSEDED` SPEC сохраняет audit trail, но не управляет новой реализацией.

## Tools и tests

| Путь | Роль |
|---|---|
| `tools/normalize_user_codex.py` | безопасный plan нормализации runtime config |
| `tools/reconcile_project_framework.py` | read-only brownfield reconciliation |
| `tools/validate_context.py` | manifest/repository integrity |
| `tools/validate_global_codex.py` | managed runtime и security invariants |
| `tools/validate_project_overlay.py` | один явно выбранный project repository |
| `tools/sync_global_skills.py` | versioned source → runtime projection |
| `tools/test_*.py` | regression coverage соответствующего tool |
| `tools/test_stage_completion_policy.py` | structural consistency Stage contract, routes, templates и status/evidence vocabulary |
| `tools/test_unified_project_workflow_policy.py` | source ownership, lifecycle prompts, learning format, external/device/monitoring policy и fail-visible source-root validation |
| `tools/test_i18n_l10n_policy.py` | global i18n/l10n owner, routes, project delta, locale/fallback/RTL и self-contained initial slice |

## Quarantine / BLOCKED

Project-specific источники с недоказанным mapping не являются active governance и не загружаются router-ом. Они сохраняются без mutation до доказанного project destination либо отдельно разрешённого внешнего архива с exact read-back. Их наличие — осознанный `BLOCKED`, а не шаблон для новых проектов.

Текущие tracked `presets/field-lab`, `presets/music-sequencer` и `presets/tutor-platform` относятся
именно к этому legacy quarantine. Installer, global router, Skills discovery и project registry их
не подключают. Они не являются поддерживаемым способом bootstrap и не получают обновления global
policy; перенос или удаление требует отдельного project mapping, проверки уникального содержания и
явного разрешения.

## Контроль полноты

1. `git ls-files` должен точно совпадать с `MANIFEST.txt`.
2. `tools/validate_context.py` проверяет наличие, canonical paths и Git visibility.
3. `tools/validate_global_codex.py` проверяет ownership ledger, все installable manifest files,
   config invariants и Skill parity.
4. Broken-reference и contamination scans выполняются отдельно, потому что manifest доказывает наличие, но не семантическую корректность.
