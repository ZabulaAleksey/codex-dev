# Текущее состояние ДЕВ / КАРКАС

Дата: 2026-08-28

## Статус

- Lifecycle: global framework hardening `implemented_unverified`.
- Integration: feature commit `67112aa` fast-forward merged в локальную `main`; push, release и
  deploy не выполнялись.
- Runtime: canonical Skill sync подтверждён для 9 sources. Terminal global validation блокирует
  только pre-existing `unmatched-browser-client-hash` в активной конфигурации.
- Protected state: active `config.toml`, `docs/LEARNING_LOG.md` и
  `docs/notes/LEARNING_LOG.md` не изменялись; их контрольные хеши до и после actual installer runs
  совпали.

Статус не повышен до `completed`: исправление active Browser client hash находится вне scope этой
задачи и потребовало бы изменения защищённого `config.toml`.

## Реализованный vertical slice

- Global `AGENTS.md` сокращён до thin router меньше 32 KiB с сохранением critical policy routes,
  Git/data-safety boundaries, documentation gate и точных merge handoff-вопросов.
- `hooks/stage_selector.py` задаёт единый pure contract selector-а для session hook и read-only
  project-overlay validator.
- Validator fail-visible различает missing, multiple, empty и invalid selector, а также missing и
  ambiguous exact unfenced heading; fenced examples и частичные token matches не принимаются.
- Explicit model pins проверены как reviewed allow-list; unpinned agent profiles наследуют
  active/default Codex model. Active `config.toml` не переписывается.
- `install-global.ps1` и executable `install-global.sh` выполняют одинаковую последовательность:
  placement/Git-root check → context validation → Skill sync → context/global validation.
- Добавлены thin project `AGENTS.md` template и bounded read-only CI gate без materialization или
  runtime config writes.
- Требования и acceptance criteria закреплены в
  `specs/features/global-framework-hardening.spec.md`.

## Verification evidence

- baseline full suite — PASS, 101 tests; feature full suite — PASS, 110 tests;
- independent test gate — PASS, 110 tests;
- post-merge full suite — PASS, 110 tests;
- post-merge `py -3 -B tools\validate_context.py` — PASS, 207 files;
- Stage selector/hook regression suites — PASS;
- Windows PowerShell syntax и actual PowerShell wrapper path — PASS до terminal global validator;
- Git Bash syntax и actual Bash wrapper path (`PYTHON_BIN=py`) — PASS до terminal global validator;
- оба actual wrapper runs завершились на одном pre-existing issue:
  `unmatched-browser-client-hash`; Skill parity перед ним — PASS, 9 sources;
- protected file hashes после обоих wrapper runs — UNCHANGED;
- `git diff --check` — PASS; line-ending warnings informational;
- final read-only review выявил stale status, слишком сильную model evidence формулировку и Unix
  executable-bit gap; все три замечания исправлены до commit.

Structural tests подтверждают delivery глобального framework contract. Они не являются product E2E;
product stage считается закрытым только по живому пути `client → API/CLI → backend`.

## Синхронизация документации

- Обновлены: `README.md`, `QUICKSTART.md`, `docs/AI_PLAN.md`, `docs/AI_STATUS.md`,
  `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`,
  `docs/CONTEXT_COMPATIBILITY.md`, `docs/CONTEXT_POLICY.md`, `docs/HOOK_POLICY.md`,
  `docs/TEAM_ARCHITECTURE.md`, `docs/TESTING.md`, `docs/VERIFY_SETUP.md`, `docs/WORKFLOW.md`,
  affected SPEC/templates, validator inventory и `MANIFEST.txt`.
- Проверены и не потребовали изменений: `docs/PROJECT_FRAMEWORK.md`, `docs/DESIGN.md`,
  `docs/SECURITY.md`, `docs/project-context.md`, `docs/MCP_CATALOG.md` и `specs/system.spec.md`.
- По прямому ограничению задачи не изменены оба `LEARNING_LOG*`.
- Не применяются в global infrastructure repository: project `prompts/STAGES.md`,
  `TRACEABILITY.md`, `CHANGELOG.md` и `DEV_LOG.md`.

## Известный blocker и следующее действие

Владелец active runtime configuration должен отдельно исправить
`unmatched-browser-client-hash`, после чего повторить соответствующий installer wrapper и
`tools/validate_global_codex.py`. Только terminal PASS этого пути разрешает перевести item из
`implemented_unverified` в `completed`.
