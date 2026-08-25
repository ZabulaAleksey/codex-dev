# Безопасность

## Границы доверия

Project-overlay validator читает путь локального repository, его файлы и Git metadata. Он не выполняет project scripts, hooks или код из проверяемого repository, не обращается к сети и не записывает файлы.

Brownfield reconciler соблюдает те же границы: он только читает repository и test output.
`FORBIDDEN_TO_OVERWRITE` и unresolved `CONFLICT` не могут быть автоматически обойдены refresh-процессом.

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

Эти риски приемлемы для локального read-only аудита; любые автоматические исправления остаются вне области этапа.

## Глобальный пользовательский слой Codex

Активный `~/.codex/config.toml` нормализуется без печати значений секретов:

- Context7 запускается без inline credential;
- `ignore_default_excludes = false` удаляет переменные вида `KEY`, `SECRET` и `TOKEN` из окружения spawned shell;
- static GitHub и неподтверждённый Atlassian MCP выключены;
- широкое доверие домашнему каталогу и несуществующие project paths запрещены;
- отсутствующая browser service и неподтверждённый browser client hash не считаются доверенными.

Hook контекста использует repository containment и bounded read. Destructive guard покрывает `git.exe`, `git -C`, варианты порядка PowerShell flags и `rm -fr /`, но остаётся дополнительным слоем поверх sandbox/approvals/execpolicy.

Git-root ДЕВ совмещён с runtime-каталогом `~/.codex`. Поэтому принудительный `git clean` запрещён во всех формах (`-f`, combined/split flags и `--force`): иначе Git может удалить игнорируемые credentials, sessions, SQLite, cache, plugins и active config. Для аудита допустим только dry-run без force.

## Остаточные действия владельца

- отозвать или ротировать ранее использованный Context7 credential у провайдера;
- выбрать для GitHub plugin режим `inherit` или `ask_before_writes` вместо текущего app-specific allow-all;
- после restart проверить, что новый shell не видит secret-like variables, а `/hooks` доверяет новым hashes;
- восстановить Browser plugin штатным lifecycle, если host не создаст корректный service binding.
