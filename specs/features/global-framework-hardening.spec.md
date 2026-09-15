# SPEC: hardening глобального ДЕВ / КАРКАСА

Статус: APPROVED
Дата: 2026-08-28

> FR-GFH-004/AC-GFH-004 описывают исторический placement wrapper-а. С 2026-09-10 source/install
> boundary superseded спецификацией `source-installed-layer.spec.md`; остальные требования этого
> завершённого hardening contract остаются действующими.

## Цель

Уменьшить обязательный контекст глобального ДЕВ, сделать Stage selector проверяемым до запуска
hook, зафиксировать корректное наследование моделей субагентов и обеспечить одинаковый безопасный
install/validation path на Windows и Unix-like системах.

## Scope

- тонкий глобальный `AGENTS.md` как router к единственным владельцам policy;
- аудит `agents/*.toml` и документированный default/pinned model contract;
- read-only Stage selector validation в `tools/validate_project_overlay.py`;
- Windows и Unix-like install wrappers вокруг существующих Python tools;
- относящиеся к изменению tests, onboarding, architecture/state и manifest;
- минимальная project-agnostic заготовка project `AGENTS.md`, `STAGES` template и bootstrap Skill;
- небольшой CI gate только для read-only context validation, unit suite и shell syntax.

## Non-goals

- изменение `~/.codex/config.toml`, secrets, credentials или runtime state Codex;
- изменение `docs/LEARNING_LOG.md`, `docs/notes/LEARNING_LOG.md` либо личных learning-журналов;
- создание новых agents, hooks, Skills, MCP или второго source of truth;
- превращение global infrastructure repository в product overlay; собственный internal
  `docs/STAGES.md` разрешён последующим canonical-stages contract;
- semantic validation полного Stage contract, product E2E, mass rollout project repositories;
- удаление legacy presets, изменение hook size limits, push, merge, release или deployment.

## Требования

### FR-GFH-001 Тонкий global router

`AGENTS.md` должен сохранить critical invariants, precedence, SIMPLE/STANDARD/COMPLEX routing,
context cascade, protected-branch/destructive/config safeguards, test-contract minimum и completion
gate. Полные процедуры принадлежат соответствующим `rules/*`, `docs/*` и `dev-karkas`; router не
копирует их. Размер versioned router должен быть меньше 32 KiB.

### FR-GFH-002 Model inheritance

Каждый явный `model` в `agents/*.toml` должен быть доступен в текущем поддерживаемом наборе.
Роли без `model` наследуют выбранную пользователем/default Codex model и сохраняют только
role-specific `model_reasoning_effort`. Recommendation file не устанавливает глобальную model
молча и явно документирует этот контракт.

### FR-GFH-003 Stage selector validation

Для полного project overlay validator обязан fail visibly, если:

- в `docs/STAGES.md` нет ровно одной unfenced строки `- Stage ID: <id>`;
- ID пуст, длиннее 64 символов или содержит символы вне ASCII letters/digits/`.`/`_`/`-`;
- в том же `docs/STAGES.md` нет ровно одного unfenced Markdown heading, содержащего ID как отдельный
  token;
- heading отсутствует или неоднозначен.

Valid selector не создаёт issue. Validator остаётся read-only и использует тот же pure selector
contract, что SessionStart/SubagentStart hook. Full Stage semantics остаются human/agent gate.

### FR-GFH-004 Cross-platform install

`install-global.ps1` и `install-global.sh` должны:

1. fail closed, если script directory и Git root не являются каноническим `~/.codex`;
2. до materialization запустить read-only `tools/validate_context.py`;
3. materialize/sync Skills только через `tools/sync_global_skills.py`;
4. повторно проверить context и запустить `tools/validate_global_codex.py`;
5. не читать, не создавать и не перезаписывать `config.toml` как часть install mutation.

Shell wrappers не вводят новую dependency: используются PowerShell + Python 3 на Windows и
POSIX-compatible Bash + Python 3 на Unix-like.

### FR-GFH-005 Onboarding и handoff без дублей

README/QUICKSTART документируют Windows и Linux/macOS с переносимыми путями от `~`.
DEGRADED Stage context и computer↔laptop handoff дополняются только у существующих владельцев
`docs/WORKFLOW.md` / `docs/VERIFY_SETUP.md`. Cost/concurrency guidance переиспользует существующие
лимиты и `max_concurrent_threads_per_session`, не вводя новую policy.

### FR-GFH-006 Automation evidence

CI выполняет только read-only `validate_context`, полный `tools/test_*.py` suite и syntax checks
install wrappers. Он не materialize-ит runtime Skills, не изменяет config и не заменяет actual
Unix-like installer evidence.

## Acceptance criteria

- AC-GFH-001 `AGENTS.md` меньше 32 KiB, обязательные router markers сохранены, ссылки не сломаны.
- AC-GFH-002 audit всех `agents/*.toml` не находит unknown explicit models; unpinned agents
  документированно наследуют default Codex model.
- AC-GFH-003 positive/negative selector tests покрывают valid, missing, multiple, empty/invalid,
  missing heading, ambiguous heading и fenced examples; existing hook regressions остаются green.
- AC-GFH-004 Windows wrapper проходит на Windows; Unix wrapper проходит на реальном Unix-like
  runner. Без Unix evidence installer slice остаётся `implemented_unverified`.
- AC-GFH-005 hash активного `config.toml` не меняется; оба `LEARNING_LOG*` не изменяются.
- AC-GFH-006 `py -3 -B tools/validate_context.py` и полный `tools/test_*.py` suite проходят.
- AC-GFH-007 runtime Skill parity восстановлен approved sync path либо честно остаётся blocker;
  state docs не содержат прежнего ложного `9/9 PASS`.
- AC-GFH-008 новые глобальные дубли agents/hooks/Skills/MCP отсутствуют; manifest содержит только
  фактически tracked files.

## Verification mapping

| Требование | Evidence |
|---|---|
| FR-GFH-001 | byte-size check, policy marker tests, link/context validator |
| FR-GFH-002 | TOML parse/model audit test, `TEAM_ARCHITECTURE` review |
| FR-GFH-003 | `tools.test_validate_project_overlay`, `tools.test_stage_completion_policy` |
| FR-GFH-004 | Windows installer run, Unix installer run, config hash comparison |
| FR-GFH-005 | README/QUICKSTART/WORKFLOW/VERIFY_SETUP review |
| FR-GFH-006 | CI definition review, full local suite |

## Rollback

Изменение откатывается отдельным `git revert`. Runtime Skill materialization имеет recoverable
backup contract существующего `sync_global_skills.py`; `config.toml` rollback не требуется,
поскольку installers не должны его изменять.

## Compatibility update

С 2026-09-08 selector и execution state принадлежат одному `docs/STAGES.md` согласно
`canonical-stages-policy.spec.md`. Это заменяет только прежнюю AI plan/status projection и не
изменяет остальные требования/acceptance этого завершённого hardening contract.
