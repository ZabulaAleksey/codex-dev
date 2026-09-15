# Stages и execution state

- Stage ID: `<stable-id>`
- Sequence: `<stable-id> → <future-stable-id>`
- NEXT: <один конкретный следующий шаг>

`docs/STAGES.md` — единственный owner текущего плана, lifecycle/evidence, blockers и NEXT.
Требования принадлежат SPEC, долгосрочный порядок — `docs/ROADMAP.md`, история — Git/CHANGELOG/
DEV_LOG при наличии. Перед validator замени placeholder selector реальным stable ASCII ID.

Если пользователь явно запускает `master_prompt`, current record может содержать один versioned
bounded `master-execution` JSON block по `schemas/master-execution.schema.json`. Не добавляй block
для обычного stage и не создавай отдельный master status/track registry/handoff file. Controller
читает только selected record и сохраняет Prompt Queue Lifecycle/merge approval boundaries.

## <stable-id> — <название самостоятельного slice>

- Status: `planned | implemented | verified | partial | blocked | unavailable`
- Lifecycle: `planned | in_progress | blocked | scaffolded | partial | implemented_unverified | completed`
- Evidence level: `implemented locally | validated locally | committed | pushed | PR opened | merged | released/deployed`
- Requirements / SPEC:
- `verified` / `DONE` допустимы только при terminal conditions Stage contract.
- `implemented` означает implementation без terminal verification; `unavailable` означает blocked
  из-за недоступной prerequisite/capability.

### dependency DAG и entry evidence

- Completed / verified prerequisites:
- DAG и проверка отсутствия self-reference, cycle, forward dependency:
- Входные предпосылки и evidence доступности:

### Самостоятельный runnable vertical slice

- Точка входа:
- Полный текущий путь:
- Наблюдаемый результат:
- Обязательная инфраструктура этого stage:

### Concrete end-to-end PASS evidence

1. Consumer input/action:
2. Реальный application/API/CLI/backend path:
3. Наблюдаемый результат:

### Scope / non-goals

- Входит:
- Не входит:

### Tasks / acceptance / PASS evidence

- [ ] <критерий>

| Gate | Command / check | Expected PASS | Result/evidence scope/environment |
|---|---|---|---|
| End-to-end | | | |

### Blockers / fallback / rollback

- Blockers: `none` или точная prerequisite/primary-path преграда.
- Fallback / degraded behavior:
- Rollback:

### Действия пользователя

- `User actions: none`, если действий пользователя нет.
- Иначе для каждого действия: `<stable-action-id>` — `READY | PENDING | DONE | NOT_REQUIRED`
  (`CONDITIONAL`, если применимо); trigger/условие; точное безопасное действие; ожидаемое evidence;
  какой шаг оно разблокирует. Secret values сюда не записываются.

### Допустимая временная реализация / Deferred

- Полностью рабочая temporary implementation или `none`:
- Deferred: только расширения/оптимизации/замены, не нужные primary path текущего stage.

### Documentation synchronization / NEXT

- Обновлены:
- Проверены без изменений: `README`, `docs/STAGES.md`, `ROADMAP`, <другие owners>.
- NEXT:

## <future-stable-id> — <следующий stage>

- Lifecycle: `planned`.
- Dependencies:
- Runnable slice / PASS contract:
- Deferred from current stage: <только необязательные расширения>.
