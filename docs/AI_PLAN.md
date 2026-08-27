# Текущий план ДЕВ / КАРКАС

Статус: global i18n/l10n policy — `completed` / `validated locally` в
`feature/global-i18n-l10n-policy`; integration в `main` не выполнялась
Рабочий item: межпроектный стандарт internationalization/localization для user-facing products
Дата: 2026-08-27

## Applicability

Глобальный infrastructure repository не является full staged product overlay и намеренно не
использует project `prompts/STAGES.md`. Change ведётся как bounded internal policy item в
`AI_PLAN`; architecture-complete fields и evidence определены ниже.

Связанная SPEC: `specs/system.spec.md`, `FR-010`, `AC-013`.

## Dependency DAG и обязательные входные предпосылки

```text
unified project workflow (`96e948b`, completed / merged locally)
        ↓
clean global baseline (94 tests, 199-file manifest, Skill parity 9/9)
        ↓
global i18n/l10n contract + routers + project-delta boundary
        ↓
structural consumer test and documentation synchronization
```

- Self-reference, cycle и forward dependency отсутствуют.
- Existing governance остаётся владельцем lifecycle/evidence; Fallback Policy — retry/degraded
  semantics; язык context — authoring language. Новая policy добавляет только product-locale delta.
- Existing accepted tests не изменялись; новый contract test добавлен отдельным файлом.
- Product repositories, Skills, hooks, MCP, dependencies, config и external services не являются
  prerequisites и этой feature не изменяются.

## Самостоятельный runnable vertical slice

```text
user requirement
  → specs/system.spec.md FR-010 / AC-013
  → rules/i18n-l10n.md (single normative owner)
  → AGENTS + rules/README + PROJECT_FRAMEWORK routers
  → thin project SPEC/DESIGN/architecture/testing delta contract
  → tools/test_i18n_l10n_policy.py
  → observable PASS or fail-visible test failure
```

Slice полностью работает как global architecture-policy consumer path без будущего hook, Skill,
runtime service или product rollout. Он не выдаёт structural PASS за перевод конкретного продукта.

## Concrete end-to-end scenario

1. Codex начинает architecture/specification user-facing product и читает global `AGENTS.md`.
2. Router подключает `rules/i18n-l10n.md` независимо от frontend/mobile/desktop/public CLI stack.
3. КАРКАС создаёт только project delta: supported locales, fallback, UX/RTL, implementation и
   evidence; полный global contract не копируется.
4. Structural contract test проходит цепочку SPEC → policy → routers → project-delta boundary и
   fail visibly при отсутствии любого обязательного звена.

Это concrete internal policy E2E. Живой product path `client → API/CLI → backend` принадлежит
конкретному repository и может быть закрыт только его locale-switch/formatting evidence.

## PASS criteria и evidence

- [x] Есть один canonical owner `rules/i18n-l10n.md`; competing global/project copies не созданы.
- [x] `i18n`, `l10n`, `language` и `locale` разделены, включая `en-US` / `en-GB`.
- [x] User-facing strings вынесены в resources; locale-dependent contract охватывает dates/time,
  numbers, currencies, units, plural rules, collation, addresses/phones и time zones.
- [x] Fallback locale, missing/partial translation, text expansion, RTL и accessibility заданы
  без дублирования общей Fallback Policy.
- [x] Initial slice допускает одну production locale только с real resources/fallback/formatting и
  pseudo-locale либо alternate test locale; future stage не разблокирует прошлый.
- [x] Project SPEC/DESIGN/architecture/testing содержат только concrete delta и evidence.
- [x] Compatibility audit не выявил конфликта с Skills/hooks/MCP/config/product repositories.
- [x] Structural и полный global test suites проходят; manifest/context validator согласованы.

Проверки:

- baseline `py -3 -B -m unittest discover -s tools -p "test_*.py"` — PASS, 94 tests;
- final full suite — PASS, 101 tests;
- `py -3 -B -m unittest tools.test_i18n_l10n_policy` — PASS, 7 tests;
- `py -3 -B tools\validate_context.py` — PASS, 201 files;
- active `~/.codex` ↔ `~/.agents/skills` parity — PASS, 9/9; Skill sources не менялись;
- active global validator baseline — `BLOCKED` только pre-existing
  `unmatched-browser-client-hash`;
- feature source против active unmerged layer ожидаемо показывает `managed-file-drift` для
  `AGENTS.md`; active files не перезаписывались;
- `git diff --check` — PASS, только line-ending informational warnings.
- independent read-only re-review — PASS без blockers; первичный P2 про uniqueness gate устранён
  отдельной negative owner/router-copy проверкой.

## Допустимая временная реализация

Одна полностью рабочая production locale допустима в product initial slice только при реальном
resource/fallback/formatting path и pseudo-locale либо alternate test locale. Для этого global
policy slice временных заглушек нет: policy, routes и executable contract tests являются рабочей
реализацией.

## Deferred / не входит

- merge в `main`, push, branch/worktree deletion и release;
- rollout либо mass migration конкретных brownfield product repositories;
- реальные переводы, locale switch и product E2E каждого отдельного продукта;
- repair pre-existing Browser client hash;
- внешняя Notion/Ideas status mutation и другие external writes без exact mapping/approval.

Ни один deferred item не нужен для запуска или проверки текущего global policy slice.

## Documentation audit

- Обновлены: `AGENTS.md`, rules router и новая policy, system SPEC, README,
  `PROJECT_FRAMEWORK.md`, architecture/decisions/compatibility/testing, context inventory/map,
  learning log, manifest/validator/test и state docs.
- Проверены без содержательных изменений: `QUICKSTART.md`, `CONTEXT_POLICY.md`, `WORKFLOW.md`,
  `DESIGN.md`, `SECURITY.md`, `HOOK_POLICY.md`, `MCP_CATALOG.md`, feature SPECs,
  `docs/project-context.md`, Skills/hooks/installer.
- Не применяются: project `prompts/STAGES.md`, `TRACEABILITY.md`, `CHANGELOG.md`, `DEV_LOG.md`.

## Следующее действие

Feature slice реализован и проверен локально. После commit следующий integration level — только
явно разрешённый merge в `main`; push и external/runtime writes не выполняются автоматически.
