# Project router: <project>

Этот файл — минимальная project-specific delta над глобальным `~/.codex/AGENTS.md`, не копия ДЕВ.
Перед первым implementation stage используй global Skill `bootstrap-project-framework`, чтобы
исследовать repository, классифицировать GREENFIELD/BROWNFIELD и создать только содержательные
недостающие contracts.

## Project facts

- Назначение: <кратко>
- Production mode: <prototype | production>
- Canonical working directory: `~/codex-workspace/<project>`
- Project-specific fragile areas: <если подтверждены>

## Canonical project context

- Requirements: `specs/system.spec.md` и `specs/features/*` при наличии.
- Architecture/decisions: `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`.
- Current work/state: `docs/AI_PLAN.md`, `docs/AI_STATUS.md`.
- Detailed stages: `prompts/STAGES.md` после полного staged bootstrap.

## Verification delta

- Canonical commands: <взять из существующих manifests/README/CI; не выдумывать>
- Project-specific acceptance gates: <если есть>

## Local prohibitions

- <только project-specific ограничения; global Git/testing/security/fallback policy не копировать>

Эта template сама по себе не объявляет repository полным staged overlay и не является evidence
реализации. Незаполненные поля должны быть разрешены во время bootstrap, а не коммититься как
формальные placeholders.
