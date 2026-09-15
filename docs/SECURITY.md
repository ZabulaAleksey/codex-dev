# Безопасность

## Global Action Journal boundary

`tools/global_action.py` is an explicit opt-in local observation CLI. It rejects unknown,
oversized, secret-like or unsafe event/catalog inputs and stores only normalized IDs,
safe relative refs and fingerprints; raw prompts, commands, stdout/stderr, environment
values, credentials and model reasoning are excluded. `init/record --dry-run` do not
write; the journal has a 16 MiB pre-read limit, rejects redirected parents,
and actual append has bounded lock, duplicate-ID no-op/conflict and read-back.
Detection/preflight cannot execute or promote scripts. The ignored journal is runtime
data, not Git/project status. Unknown host activation and exact Notion cleanup remain
separate gates.

## Continuous master execution

Embedded `master-execution` state считается недоверенным структурированным вводом: bounded size,
exact fields, duplicate-key/ID rejection, cycle/path/branch validation и fail-closed unknown facts.
State/prompt никогда не является command source. Git adapter имеет только inventory и explicit
create-only worktree operation внутри разрешённого root; occupied target/branch и unknown outcome
требуют read-back/reconciliation. Merge, push, release, worktree deletion и prompt cleanup не
выполняются controller-ом. Launcher сверяется по state revision + Git checkpoint.

## Prompt queue cleanup boundary

Threat/control contract принадлежит `rules/prompt-queue-lifecycle.md` и PQ SPEC.
CLI принимает trusted executor attestations, не инструкции из страницы, не исполняет evidence
strings и не имеет credentials. Decision привязан к source/execution/evidence digest и Git HEAD;
stale/ambiguous read-back блокирует cleanup. Semantic DoD проверяет executor/reviewer.

## Specification → Execution boundary

Pipeline принимает только bounded JSON/TOML с exact fields, не интерпретирует строки как команды и
не загружает тела нерелевантных Skills. Context diagnostics сохраняет structural signals, но не
prompts, code, secrets или raw handoff content. Router и promotion decision не меняют executor,
model, Git, policy, hook, Skill source, runtime materialization или внешний backlog.

UNC/device paths отклоняются до filesystem access. Trace contract должен находиться внутри exact
Git root; live selector и CME v2 slice являются владельцами requirements/status/evidence threshold,
artifact paths проходят containment/link checks, validators и tests представлены identifier refs.
Typed security/integrity, authorization, resource-limit и contract-validation failures блокируют
execution и не передают raw failure text модели или stdout. High-confidence secret-like intake и
lifecycle evidence отвергаются без echo.

Skill retirement является fail-closed preflight: active Skill сначала должен стать deprecated,
source/runtime digest обязаны совпасть, live consumers отсутствовать, а replacement — быть active,
проверенным и покрывать обязательные capabilities. Даже успешный preflight не разрешает удаление.
Caller consumer/parity attestations не повышаются до trusted evidence: clean preflight возвращает
`review_required`, `attestation_trusted=false`, `deletion_authorized=false`.


## Границы доверия

Project-overlay validator читает путь локального repository, его файлы и Git metadata. Он не выполняет project scripts, hooks или код из проверяемого repository, не обращается к сети и не записывает файлы.

Brownfield reconciler соблюдает те же границы: он только читает repository и test output.
`FORBIDDEN_TO_OVERWRITE` и unresolved `CONFLICT` не могут быть автоматически обойдены refresh-процессом.

Stage compatibility adapter читает только три known project-relative state path с отдельными
size limits, запрещает symlink/non-file sources и декодирует только UTF-8. Legacy fields
извлекаются по exact labels; duplicate/conflicting facts, malformed same-file manifest и source
digest drift дают `conflict` / `migration_required`. Dry-run plan не исполняет Markdown и не
запускает product code. Explicit materializer принимает только strict bounded plan JSON и отдельно
подтверждённый digest, разрешает write только `docs/STAGES.md`, повторно проверяет repository
identity, все source/target bytes и path containment под exclusive lock. Sibling temp file
fsync-ится до atomic replace; exact parser/router read-back обязателен, failure восстанавливает
pre-image. Unknown leftover lock не удаляется по возрасту: до manual reconciliation возвращается
`recovery_required`. Retained legacy files не удаляются и не переписываются.
Compatibility CLI может успешно вернуть non-runnable audit report: caller обязан проверять
`runnable=true`, а не только process exit code. Projection scalars bounded и отвергают control
characters; state files должны хранить только references/digests, но не credentials или payloads.

Normal router/validator/hook используют только pure inspection projection. Suggested migration
action — список fixed argv tokens; repository-controlled paths/content не интерполируются в shell
string и не исполняются. Hook не имеет implicit write/materialization capability, не публикует
exact plan content или raw legacy payload и обрезает structured context. Invalid canonical state
не может заставить router довериться legacy projection. Plan digest можно показывать как integrity
reference, но `plan_path=null` остаётся честным, пока caller отдельно не сохранил reviewed plan.
Structural CME validation нормализует repository-controlled worktree paths лексически и не
выполняет `resolve()`/UNC network probe; filesystem resolution остаётся только в explicit
worktree adapter operation после отдельного route request.

Для явно объявленного Backend DX project validator читает `docs/project-context.md`
и Git-visible `.env.example`. Он сообщает только имя подозрительного config key,
но не его значение; private-key blocks и high-confidence credential-like values
считаются ошибкой. DB/resource reset требует документированного enforced local/test
guard, а production access остаётся deny-by-default.

## Меры

- команды Git передаются как список аргументов без shell interpolation;
- `safe.directory` задаётся process-local через `git -c` для точного target path и не меняет пользовательский config;
- fingerprints вычисляются SHA-256 над файлами канонических источников;
- validator не удаляет и не исправляет найденные дубликаты;
- JSON сериализуется стандартной библиотекой, issues сортируются детерминированно.

## Остаточные риски

- чтение очень большого локального automation-файла расходует память пропорционально его размеру;
- точное побайтовое сравнение не обнаруживает семантические копии после косметического изменения;
- conservative `.env.example` scan не заменяет полноценный secret scanner и может
  не обнаружить короткий либо нестандартно названный credential;
- Backend DX validator проверяет declared contract и очевидные guards, но не
  выполняет project scripts и не доказывает runtime production isolation;
- состояние repository может измениться другим процессом между отдельными filesystem/Git проверками.
- portable Python stdlib на Windows не даёт полного `openat`/`O_NOFOLLOW` эквивалента против
  враждебного same-user процесса, меняющего junction в узком окне между последней path-проверкой и
  `os.replace`; repeated containment checks, handle/type checks и cooperative lock уменьшают, но не
  устраняют этот residual TOCTOU risk.

Эти риски приемлемы для локального read-only аудита; любые автоматические исправления остаются вне области этапа.

## Глобальный пользовательский слой Codex

Активный `~/.codex/config.toml` нормализуется без печати значений секретов:

- Context7 запускается без inline credential;
- `ignore_default_excludes = false` удаляет переменные вида `KEY`, `SECRET` и `TOKEN` из окружения spawned shell;
- static GitHub и неподтверждённый Atlassian MCP выключены;
- широкое доверие домашнему каталогу и несуществующие project paths запрещены;
- отсутствующая browser service и неподтверждённый browser client hash не считаются доверенными.

Hook контекста использует repository containment и bounded read. Destructive guard покрывает `git.exe`, `git -C`, варианты порядка PowerShell flags и `rm -fr /`, но остаётся дополнительным слоем поверх sandbox/approvals/execpolicy.

Runtime-каталог `~/.codex` не является Git working tree. Не инициализируй в нём repository и не
используй Git cleanup как механизм установки: это может удалить credentials, sessions, SQLite,
cache, plugins и active config. Canonical DEV Git operations выполняются только в отдельном source
repository.

Installer использует deny-by-default границу: protected runtime namespaces проверяются до writes,
manifest collision завершает операцию, unknown destination files сохраняются, а stale deletion
разрешён только по валидному ownership ledger. Update/delete имеют transaction backup; validation и
Skill-sync failure запускают rollback. Ledger не содержит absolute paths, payload или secrets.

## Остаточные действия владельца

- отозвать или ротировать ранее использованный Context7 credential у провайдера;
- выбрать для GitHub plugin режим `inherit` или `ask_before_writes` вместо текущего app-specific allow-all;
- после restart проверить, что новый shell не видит secret-like variables, а `/hooks` доверяет новым hashes;
- восстановить Browser plugin штатным lifecycle, если host не создаст корректный service binding.

## AI Policy Profiling

Profiler работает только после explicit opt-in внутри выбранного project root. Versioned schema
разрешает bounded identifiers, numbers и короткие observations; prompt/user/source content, raw
command arguments, stdout/stderr, environment values, secrets и credentials не являются частью
контракта и не записываются.

Telemetry path resolve-ится с проверкой containment и symlink escape. JSONL line/file имеют
limits; каждый config/stream/report descendant повторно проверяется непосредственно перед I/O.
Concurrent JSONL writers используют bounded exclusive lock и append mode; stale lock fail closed.
Invalid, oversized и unsupported schema fail closed до append. Generated reports сначала
строятся и валидируются в memory/temporary sibling, затем заменяются atomically, поэтому corrupt
input не повреждает последний валидный report. Git metadata читается process-local без изменения
config; отсутствие Git даёт null facts.

Остаточный риск: короткое human observation может содержать чувствительные данные вопреки
инструкции. Поэтому text fields ограничены, CLI не принимает arbitrary payload/env/output и
documentation требует записывать только operational summary без private content.
