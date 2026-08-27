# Проверка глобального ДЕВ

Этот документ описывает discoverable verification commands самого global
framework. Общие правила test contracts остаются в `AGENTS.md`,
`rules/governance.md` и dev-karkas `references/TESTING_POLICY.md`.

## Canonical commands

Из корня `~/.codex`:

```powershell
py -3 -B tools\validate_context.py
py -3 -B -m unittest tools.test_sync_global_skills tools.test_reconcile_project_framework tools.test_validate_global_codex tools.test_validate_project_overlay tools.test_backend_dx_policy tools.test_documentation_sync_policy tools.test_stage_completion_policy tools.test_unified_project_workflow_policy tools.test_i18n_l10n_policy
py -3 -B tools\sync_global_skills.py
py -3 -B tools\validate_global_codex.py --workspace ~/.codex --codex-home ~/.codex
git diff --check
```

`install-global.ps1` выполняет Skill sync и основные проверки installed layer, но
не заменяет целевой unit suite во время разработки.

## Backend DX fixture contract

`tools.test_backend_dx_policy` создаёт temporary independent Git repositories и
проверяет:

- neutral complete `BDX-L2` delta как framework clean-room fixture;
- ambiguous/L0 classification, missing fields/commands и missing route;
- local/test guard destructive reset;
- generated API/contract drift command;
- conservative `.env.example` secret detection без вывода значения;
- misplaced/duplicated global policy content;
- alignment template, policy IDs/gates, routers, Skill и existing agent roles.

Fixture доказывает read-only deterministic contract validator-а. Он не запускает
реальную DB, service, provider или production clean-room и не должен описываться
как E2E конкретного product backend.

## Documentation synchronization contract

`tools.test_documentation_sync_policy` проверяет стабильные `FR-006` / `AC-006`,
обязательный список state-bearing sources, routing Skills и поддержку AI templates.
Это structural contract test: смысловую актуальность проектной документации подтверждает
Completion Documentation Synchronization Gate, а не эвристический semantic validator.

## Architecturally complete stage contract

`tools.test_stage_completion_policy` проверяет стабильные `FR-007` / `AC-007`, единственного
владельца полного Stage contract, обязательные planning/status fields, routes Skills/templates,
разделение lifecycle/evidence, SPEC authority и отсутствие конкурирующего local backlog path.
Subprocess-тесты дополнительно проходят внутренний путь
`AI_PLAN Stage ID → session_context.py → exact selected STAGES record` и проверяют no-selector,
missing и ambiguous degraded-сценарии.

Policy-часть остаётся structural contract test глобальной автоматизации, а hook-часть — internal
E2E context-projection path. Она не валидирует семантику произвольного project
`prompts/STAGES.md`, не исполняет product path и не превращает mocks/stubs в E2E evidence.

## Unified project workflow contract

`tools.test_unified_project_workflow_policy` проверяет `FR-008..009` / `AC-009..012`, единственного
policy owner, восемь copy-ready lifecycle requests, новый LEARNING shape, external/device/monitoring
markers и фактический `~/.codex` source root. Его executable consumer path передаёт отсутствующий
canonical root в production validator и требует structured issues вместо traceback.

Это internal policy/validator E2E, а не product E2E. Восстановление реального project repository
проверяется отдельно read-only командами `reconcile_project_framework.py` и
`validate_project_overlay.py` плюс semantic link/status audit; structural PASS не маскирует stale
references.

## Global i18n/l10n contract

`tools.test_i18n_l10n_policy` проверяет `FR-010` / `AC-013`, единственного policy owner,
global routers, различие `language` / `locale`, resource-based строки, полный класс
locale-dependent данных, fallback locale, text expansion, RTL и self-contained initial slice с
pseudo-locale либо alternate test locale.

Это structural contract test global framework. Он подтверждает, что КАРКАС доставляет требование
в user-facing product architecture, но не заменяет project unit/component/integration/E2E evidence
конкретных переводов, форматирования и locale switch.

## Evidence policy

Для каждой команды фиксируй command, purpose, `PASS | FAIL | BLOCKED`, scope и
caveat. Pre-existing runtime failures отделяются от regressions. Не ослабляй
принятые tests/fixtures/goldens; новые contract tests добавляются отдельным файлом.
