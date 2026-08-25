# Текущий план ДЕВ / КАРКАС

Статус: Backend DX реализован и локально проверен в feature-ветке; merge/push не выполнены
Этап: Backend Developer Experience Policy integration
Дата: 2026-08-25

## Текущий ограниченный срез

Встроить один адаптивный Backend DX contract в global rules, Skills, agents,
КАРКАС и существующий read-only project validator. Product repositories, hooks,
dependencies и production systems не изменять.

Связанная SPEC: `specs/features/backend-dx-policy.spec.md`

## Выполнено

1. Создан канон `rules/backend-dx.md` с `BDX-L0..L3`, semantic commands,
   `BDX-*` IDs, `BDX-GATE-01..12`, anti-patterns и clean-room contract.
2. Добавлены thin routing, Skill `backend-dx-audit`, bounded responsibilities шести
   existing agents и project delta template для `docs/project-context.md`.
3. КАРКАС/bootstrap workflow учитывает Backend DX applicability без создания
   пустого L0 section или нового runtime stack.
4. Existing overlay validator расширен opt-in checks; neutral fixture и negative
   cases добавлены отдельным test module без изменения принятых tests.
5. Architecture, decision, security, testing, commands, framework, inventory,
   learning log и roadmap documents синхронизированы.
6. Runtime Skills `backend-dx-audit`, `bootstrap-project-framework` и `dev-karkas`
   materialized штатным sync с recoverable backup; feature source/runtime parity PASS.

## Проверки

- `py -3 -B tools\validate_context.py` — PASS, 196 files;
- полный validator/sync/reconcile/Backend DX unit suite — PASS, 65 tests;
- `backend-dx-audit` quick validation и dev-karkas package validation — PASS;
- runtime Skill parity — PASS, 9 sources;
- `git diff --check`, conflict-marker и machine-path scans — PASS.

## Следующее действие

После явного разрешения слить `feature/backend-dx-policy` в `main`, повторить
active `validate_global_codex.py` и удалить временный worktree. До merge active
`main` закономерно сообщает drift двух runtime Skills относительно старых sources.
