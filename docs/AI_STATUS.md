# Текущее состояние ДЕВ / КАРКАС

Дата: 2026-08-27

## Статус

- Lifecycle: global i18n/l10n policy `completed` / `validated locally`.
- Evidence level: feature-worktree structural consumer path и полный global test suite — PASS.
- Integration: `feature/global-i18n-l10n-policy`; merge в active local `main`, push и external
  writes не выполнялись.
- Runtime: Skill sources, hooks, MCP, dependencies и config не менялись; active Skill parity —
  PASS, 9/9.

Один cross-cutting owner теперь задаёт internationalization/localization для всех user-facing
products. Product repositories наследуют contract и хранят только supported locales, stack, UX,
исключения и acceptance evidence.

## Реализованный vertical slice

- `specs/system.spec.md` v1.4 содержит `FR-010` / `AC-013`;
- `rules/i18n-l10n.md` различает `i18n`, `l10n`, `language` и `locale`, включая `en-US` / `en-GB`;
- user-facing strings маршрутизируются в translation resources, а locale-dependent data contract
  охватывает dates/time, numbers, currencies, units, plural rules, collation, addresses/phones и
  time zones;
- locale resolution, fallback locale, missing/partial translation, text expansion, RTL и
  accessibility имеют явные инварианты;
- initial product slice может иметь одну production locale только с реальным resource/fallback/
  formatting path и pseudo-locale либо alternate test locale;
- `AGENTS.md`, rules router, `PROJECT_FRAMEWORK.md`, README и architecture ведут к одному owner;
- compatibility audit подтвердил отсутствие нового Skill/hook/MCP/service/dependency и отсутствие
  конкурирующей project copy;
- новый structural contract test зарегистрирован в canonical suite и context validator.

## Verification evidence

- baseline full suite — PASS, 94 tests; final full suite — PASS, 101 tests;
- `py -3 -B -m unittest tools.test_i18n_l10n_policy` — PASS, 7 tests;
- `py -3 -B tools\validate_context.py` — PASS, 201 files;
- active `tools\sync_global_skills.py` read-enabled check — PASS, 9 sources;
- active global validator baseline — `BLOCKED` только pre-existing
  `unmatched-browser-client-hash`;
- validation feature source против active unmerged layer ожидаемо сообщает
  `managed-file-drift: AGENTS.md`; это pending integration evidence, не runtime regression;
- `git diff --check` — PASS; line-ending warnings informational.
- independent read-only re-review — PASS без blockers; P2 про отсутствие uniqueness assertion
  исправлен negative test-ом второго rules owner и копирования нормативных headings в routers.

Structural framework PASS подтверждает доставку global requirement, но не является E2E перевода
конкретного продукта. Product E2E закрывается только живым locale switch и locale-dependent output
в соответствующем repository.

## Синхронизация документации

- Обновлены: global router, rules index/new policy, system SPEC, README, `PROJECT_FRAMEWORK.md`,
  `ARCHITECTURE.md`, `DECISIONS.md`, `CONTEXT_COMPATIBILITY.md`, `TESTING.md`, context inventory/map,
  `LEARNING_LOG.md`, manifest/validator/test и AI state docs.
- Проверены и остались точными: `QUICKSTART.md`, `CONTEXT_POLICY.md`, `WORKFLOW.md`, `DESIGN.md`,
  `SECURITY.md`, `HOOK_POLICY.md`, `MCP_CATALOG.md`, feature SPECs, `docs/project-context.md`,
  Skills/hooks/installer.
- Не применяются в global infrastructure repository: project `prompts/STAGES.md`,
  `TRACEABILITY.md`, `CHANGELOG.md`, `DEV_LOG.md`.

## Ограничения

- Feature ещё не integrated в `main`; active global layer продолжает использовать прежний
  `AGENTS.md` до разрешённого merge.
- Active global validator сохраняет pre-existing `unmatched-browser-client-hash`; policy его не
  меняет.
- Product rollout, brownfield string migration, реальные translations и product E2E не выполнялись
  и не являются evidence текущего internal policy slice.
- Push, branch/worktree deletion, external Ideas/Notion writes и release/deploy не выполнялись.

## Следующее действие

После feature commit следующий уровень интеграции — merge в `main` только по явному разрешению.
Затем Completion Documentation Synchronization Gate повторяется по target branch.
