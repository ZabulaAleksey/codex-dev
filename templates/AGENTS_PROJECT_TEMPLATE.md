# Project router: <project>

Этот файл — минимальная project-specific delta над глобальным `~/.codex/AGENTS.md`, не копия ДЕВ.
Перед первым implementation stage используй global Skill `bootstrap-project-framework`, чтобы
исследовать repository, классифицировать GREENFIELD/BROWNFIELD и создать только содержательные
недостающие contracts.

Global DEV bridge: enabled

Machine-readable membership is declared only by `.codex/dev-project.toml`; this line is the
human-readable router declaration and is not sufficient by itself.

## Project facts

- Назначение: <кратко>
- Production mode: <prototype | production>
- Canonical working directory: `${PROJECTS_ROOT}/<project>`
- Project-specific fragile areas: <если подтверждены>

## Canonical project context

- Requirements: `specs/system.spec.md` и `specs/features/*` при наличии.
- Architecture/decisions: `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`.
- Current work/state and detailed stages: `docs/STAGES.md` после полного staged bootstrap.

## Verification delta

- Canonical commands: <взять из существующих manifests/README/CI; не выдумывать>
- Project-specific acceptance gates: <если есть>

## Local prohibitions

- <только project-specific ограничения; global Git/testing/security/fallback policy не копировать>

Эта template сама по себе не объявляет repository полным staged overlay и не является evidence
реализации. Незаполненные поля должны быть разрешены во время bootstrap, а не коммититься как
формальные placeholders.
