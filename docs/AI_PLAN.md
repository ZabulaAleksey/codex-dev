# Текущий план ДЕВ / КАРКАС

Статус: `implemented_unverified` / internal infrastructure item
Stage ID (internal, не selector): `DEV-GLOBAL-HARDENING-001`
Рабочий item: hardening global router, Stage selector validation, models и cross-platform install
Дата: 2026-08-28

## Applicability

Global infrastructure repository не является full staged project overlay и намеренно не имеет
`prompts/STAGES.md`. Поэтому этот internal Stage ID не записан selector-строкой `- Stage ID:`:
такая строка потребовала бы project stage catalog и создала ложный `DEGRADED` hook context.

Связанные требования: `specs/features/global-framework-hardening.spec.md`
(`FR-GFH-001..006`, `AC-GFH-001..008`).

## Dependency DAG и входные предпосылки

```text
canonical ~/.codex consolidation (completed)
        ↓
architecturally complete Stage hook contract (completed)
        ↓
unified workflow + cross-device handoff (completed)
        ↓
SPEC / acceptance delta
        ↓
shared selector contract + validator tests
        ↓
validator implementation
        ↓
AGENTS router reduction + model/config audit + installers
        ↓
docs/manifest synchronization + full tests/review
```

Evidence на старте:

- Git `main...origin/main`, clean, HEAD `e675b16` до создания feature worktree;
- baseline full suite: PASS, 101 tests;
- `py -3 -B tools\validate_context.py`: PASS, 201 files;
- active global validation: pre-existing FAIL из-за runtime drift шести Skills;
- `config.toml` и оба `LEARNING_LOG*` запрещены к изменению.

Self-reference, cycle и forward dependency отсутствуют. Runtime Skill drift должен быть либо
устранён approved sync path, либо остаться явным blocker без completion claim.

## Самостоятельный runnable vertical slice

```text
temporary independent Git project
  → docs/AI_PLAN.md exact selector
  → prompts/STAGES.md exact unfenced heading
  → tools/validate_project_overlay.py
  → deterministic PASS или issue code/message
  → unchanged target bytes и Git status
```

Installer consumer path:

```text
canonical ~/.codex
  → placement/Git-root check
  → read-only validate_context
  → sync_global_skills materialization
  → context/global validation
  → config.toml hash unchanged
```

Оба пути исполнимы без future stage, нового service, dependency, Skill, hook или MCP.

## Concrete end-to-end scenario

1. Создать temporary independent full-overlay fixture.
2. Valid selector с одним отдельным heading token даёт exit `0` без mutation.
3. Missing/multiple/invalid selector и missing/ambiguous headings дают отдельные fail-visible issues.
4. Fenced examples игнорируются так же, как existing SessionStart/SubagentStart hook.
5. Windows и реальный Unix-like runner выполняют canonical installer sequence; `config.toml` hash
   до и после совпадает.

## Область работы

Входит: SPEC, selector parser/validator/tests, `AGENTS.md`, model recommendation docs,
PowerShell/Bash installers, затронутые README/QUICKSTART/architecture/state/testing docs, thin
project AGENTS template, небольшой CI gate и `MANIFEST.txt`.

Не входит: active `config.toml`, learning logs, product repositories, legacy preset cleanup,
full semantic Stage parser, новые agents/hooks/Skills/MCP, push/merge/release/deploy.

## Рабочие задачи

1. Зафиксировать SPEC и этот Stage contract до production-code mutation.
2. Вынести pure Stage selector contract и переиспользовать его в hook/validator без semantic drift.
3. Добавить positive/negative overlay validator tests, сохранив hook regressions.
4. Сжать global router ниже 32 KiB, сохранив critical markers и policy routes.
5. Подтвердить agent model pins/default inheritance; обновить recommendation/docs без silent model override.
6. Реализовать симметричные install wrappers и cross-platform onboarding.
7. Добавить только недостающую thin project AGENTS template и bounded CI validation.
8. Выполнить tests/review, восстановить или честно отметить Skill parity, синхронизировать docs/manifest.

## Acceptance / PASS criteria

- [x] `AGENTS.md` меньше 32 KiB; обязательные policy markers и ссылки сохранены.
- [x] Stage selector tests ловят valid/missing/multiple/empty/invalid/missing-heading/ambiguous/fenced.
- [x] Existing hook behavior и size limits не сломаны.
- [x] Explicit agent model IDs сверены с reviewed catalog; unpinned agents наследуют default.
- [x] Оба installer path дошли до pre-existing active-config blocker; status честно оставлен
  `implemented_unverified`.
- [x] `config.toml` hash и `LEARNING_LOG*` неизменны.
- [x] Full unit suite и `validate_context.py` PASS; runtime Skill parity подтверждена actual runs.
- [x] Reviewer findings исправлены; documentation synchronization gate и manifest завершены.

Terminal global validation остаётся красной только из-за pre-existing
`unmatched-browser-client-hash`. Этот внешний blocker не отменяет выполненный implementation slice,
но не разрешает completion claim.

## Допустимая временная реализация

- Thin Bash/PowerShell wrappers вокруг существующих Python tools допустимы.
- CI является дополнительным Unix syntax/unit evidence, но не заменяет actual installer run.
- Mocks/fakes не подтверждают Unix install или model availability.

## Deferred

- semantic validation полного Stage contract;
- mass rollout project overlays и removal quarantined presets;
- изменение hook `MAX_CHARS` / scan limits;
- repair unrelated runtime config/browser state;
- push, merge, release, deployment и external writes.

## Риски и rollback

- Mandatory selector validation может выявить существующие incomplete overlays; сообщения должны
  давать точную remediation и validator не должен автоматически исправлять project.
- Shared parser extraction повышает hook regression risk; существующие subprocess tests обязательны.
- Router reduction может потерять critical invariant; marker/policy suites и manual diff audit
  являются blocking gate.
- Rollback: отдельный `git revert`; runtime Skill sync использует существующий recoverable backup.

## Documentation synchronization gate

Перед terminal status проверить README, QUICKSTART, AI_PLAN, AI_STATUS, ROADMAP, architecture,
decisions, compatibility, testing, VERIFY_SETUP, affected SPEC и manifest. Менять только
изменившиеся факты; `LEARNING_LOG*` не трогать.
