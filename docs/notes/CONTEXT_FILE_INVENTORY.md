# Реестр файлов глобального контекста

Дата проверки: 2026-08-25.

Точный пофайловый состав Git-контекста задаёт `MANIFEST.txt`. Этот документ объясняет роль каждого класса файлов; любой tracked-файл обязан одновременно присутствовать в manifest и в одной из категорий ниже.

## Корень

| Путь | Роль |
|---|---|
| `AGENTS.md` | единственный global instruction router |
| `.gitignore` | deny-by-default граница между governance и runtime/secrets |
| `README.md`, `QUICKSTART.md` | human-readable навигация и проверка |
| `config.ai-dev-team.recommended.toml` | безопасное предложение конфигурации без credentials |
| `hooks.json` | event → hook wiring |
| `install-global.ps1` | read-only install/verification entry point |
| `MANIFEST.txt` | точный tracked file set для validator |

Именованные project installers, backlog и project inventory в active global root запрещены.

## Автоматически и условно загружаемый слой

| Путь | Роль |
|---|---|
| `agents/*.toml` | универсальные роли субагентов |
| `hooks/*.py` | bounded session context и safety checks |
| `rules/ai-dev-team.rules` | shell command policy |
| `rules/README.md` | router по режиму, домену, стеку и SDLC |
| `rules/governance.md`, `rules/model-routing.md`, `rules/fallback-policy.md`, `rules/dependency-management.md`, `rules/backend-dx.md` | общие инженерные контракты |
| `rules/modes/*.md` | режим выполнения |
| `rules/domains/*.md` | универсальные доменные ограничения |
| `rules/stacks/*.md` | правила применимого технологического стека |
| `rules/sdd/*.md` | specification-driven workflow |

Каждый файл в этих каталогах выбирается router-ом по текущей задаче; каталог целиком в prompt не подмешивается.

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
| `docs/AI_STATUS.md`, `docs/AI_PLAN.md` | текущее состояние и ближайший план |
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
| `templates/*.md` | project-agnostic формы SPEC, AI plan/status, decisions, журналов и Backend DX delta |

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

## Quarantine / BLOCKED

Project-specific источники с недоказанным mapping не являются active governance и не загружаются router-ом. Они сохраняются без mutation до доказанного project destination либо отдельно разрешённого внешнего архива с exact read-back. Их наличие — осознанный `BLOCKED`, а не шаблон для новых проектов.

## Контроль полноты

1. `git ls-files` должен точно совпадать с `MANIFEST.txt`.
2. `tools/validate_context.py` проверяет наличие, canonical paths и Git visibility.
3. `tools/validate_global_codex.py` проверяет managed files, config invariants и Skill parity.
4. Broken-reference и contamination scans выполняются отдельно, потому что manifest доказывает наличие, но не семантическую корректность.
