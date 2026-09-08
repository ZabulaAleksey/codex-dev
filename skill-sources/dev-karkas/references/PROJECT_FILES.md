# Project files policy

Используй этот документ как карту назначения. Обязательный baseline active full staged product
overlay задаёт `~/.codex/rules/governance.md`; колонка applicability не разрешает пропускать его.
Repository вне полного overlay сначала явно классифицируется и не получает placeholders.

| Artifact | Назначение | Создавать когда |
|---|---|---|
| `AGENTS.md` | project-specific инструкции агентам | обязательно для полного overlay |
| `README.md` | вход для человека/разработчика | почти всегда |
| `specs/system.spec.md` / `specs/features/*.spec.md` | требования продукта/системы | когда меняется существенное наблюдаемое поведение |
| `docs/ARCHITECTURE.md` | каноническая архитектура | обязательно для полного overlay |
| `docs/DESIGN.md` | канонический UI/UX contract | есть пользовательский интерфейс |
| `docs/SECURITY.md` | security baseline | есть сеть, пользователи, данные, upload, auth или публичный API |
| `docs/DEPENDENCIES.md` | canonical manager, lockfile, shared cache/store и clean restore | ecosystem определим и существующий architecture document не выполняет эту роль |
| `docs/ROADMAP.md` | направления и крупные этапы | обязательно для полного overlay |
| `docs/project-context.md` | устойчивые project facts, включая применимую Backend DX delta | обязательно для полного overlay; Backend DX section только при `BDX-L1..L3` |
| `docs/DECISIONS.md` | журнал важных решений; может ссылаться на ADR supplement | обязательно для полного overlay |
| `prompts/STAGES.md` | единый detailed stage и execution-state source: selector, plan, lifecycle/evidence, blockers, NEXT | обязательно для полного overlay |
| `docs/LEARNING_LOG.md` | повторно полезные выводы | обязательно для полного overlay; entries только при наличии evidence |
| `docs/DEV_LOG.md` | краткий журнал существенных работ | нужен trace, отличный от Git history |
| `docs/notes/<topic>.md` | долговечный дополнительный материал без канонической роли | заметка действительно нужна и не помещается в существующий контракт |

## Именование и канон

1. В brownfield не переименовывай существующий legacy-файл только ради совпадения с таблицей до reconciliation и semantic/link audit.
2. Зафиксируй canonical mapping в `docs/CONTEXT_COMPATIBILITY.md`, сохрани уникальное содержание и мигрируй к одному канону без параллельной роли.
3. Ссылки между документами предпочтительнее копипаста.
4. Не создавай пустые placeholder-файлы без ближайшего полезного содержания.
5. Не генерируй `AI_PLAN.md`, `AI_STATUS.md`, `PLAN.md`, `STATUS.md`, `PROGRESS.md` или
   `SNAPSHOT.md`: их актуальное execution-state содержание принадлежит `prompts/STAGES.md`.
6. Не создавай произвольный новый `.md` в корне repository или непосредственно в `docs/`: сначала переиспользуй канонический документ, иначе используй `docs/notes/<topic>.md`.
7. Не перемещай существующую документацию автоматически; сначала выполни semantic/link audit и сохрани уникальное содержание.

## Stage prompts

Рекомендуемая форма:

```text
prompts/
└── STAGES.md
```

`STAGES.md` является единым detailed stage source. Каждый stage применяет архитектурный Stage
contract из governance. Сырые идеи не превращаются в отдельные stage-файлы до refinement/approval.
