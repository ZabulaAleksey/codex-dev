# Текущее состояние ДЕВ / КАРКАС

Дата: 2026-08-25

## Статус

Глобальный ДЕВ хранится в единственном Git root `~/.codex`. Backend Developer
Experience Policy реализована, validated и fast-forward слита в локальную `main`
commit `17debb4`. Runtime Skills materialized из active source; push не выполнялся.
Product repositories не изменялись.

## Подтверждённые инварианты

- один canonical Backend DX source — `rules/backend-dx.md`;
- applicability `BDX-L0..L3` зависит от фактической backend surface, а не от
  желаемого stack;
- project `AGENTS.md` остаётся thin router, а `Backend DX Delta` принадлежит
  `docs/project-context.md`; L0 не создаёт пустой section;
- versioned Skill source — `skill-sources/backend-dx-audit`, runtime projection —
  `~/.agents/skills/backend-dx-audit`;
- existing package/task/test/ORM/migration/orchestration mechanisms сохраняются;
- destructive DB/resource actions и production access deny-by-default;
- project validator read-only и включает Backend DX checks только при явной delta;
- dependency, database/API, testing, security и fallback contracts сохраняют
  собственных canonical owners.

## Verification evidence

- `py -3 -B tools\validate_context.py` — PASS, 196 files;
- `py -3 -B -m unittest tools.test_sync_global_skills tools.test_reconcile_project_framework tools.test_validate_global_codex tools.test_validate_project_overlay tools.test_backend_dx_policy` — PASS, 65 tests;
- neutral `BDX-L2` clean-room fixture и 16 additional Backend DX/global contract cases — PASS;
- `python -X utf8 ...\quick_validate.py skill-sources\backend-dx-audit` — PASS;
- `skill-sources\dev-karkas\scripts\validate.ps1` — PASS;
- `tools\sync_global_skills.py` parity — PASS, 9 sources;
- `git diff --check`, conflict-marker, machine-specific path и tracked secret-assignment scans — PASS.
- active `tools\validate_global_codex.py` не сообщает Backend DX или Skill drift,
  но остаётся `BLOCKED` прежним `unmatched-browser-client-hash` runtime Browser.

## Ограничения

- fixture доказывает framework/validator contract, но не E2E или production
  clean-room конкретного backend;
- полный active global validator не имеет PASS из-за baseline
  `unmatched-browser-client-hash`; эта интеграция не изменяет Browser runtime/config;
- inactive project-specific quarantine/presets не подключены к Backend DX и не
  изменялись.

## Следующее действие

Обязательных этапов интеграции Backend DX больше нет. Подтверждённые уровни:
`implemented`, `validated`, `committed`, `merged locally`, `materialized globally`.
`pushed`, `released` и `deployed` не заявляются. Product rollout выполняется только
отдельной opt-in задачей; Browser hash repair остаётся отдельной maintenance-задачей.
