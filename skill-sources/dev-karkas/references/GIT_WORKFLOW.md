# Git workflow

Следуй существующей политике репозитория прежде этого reference.

## Перед изменениями

Проверь, если доступно:

- current branch;
- working tree status;
- untracked files;
- relevant remote/target branch;
- наличие незакоммиченных пользовательских изменений.

Не затирай unrelated work.

Для Continuous Master Execution continuation того же track переиспользует существующий worktree.
Независимый parallel writer получает отдельную branch/worktree через deterministic route;
read-only task isolation не создаёт. Occupied path/branch, dirty unknown state или ownership
overlap дают fail-closed/integration checkpoint. Worktree живёт до coherent integration или
finalization boundary и не удаляется после каждого slice.

## Commit

Commit должен быть атомарным и соответствовать выполненному scope. Не включай случайные unrelated files.

## Push / PR / merge

Различай действия:

- local commit;
- push;
- PR creation;
- merge;
- branch deletion.

Одно не означает другое.

Checkpoint commits внутренних master slices не являются запросом на merge. Integration checkpoint
нужен на coherent boundary, cross-track dependency/divergence, release gate или master completion;
сам checkpoint не разрешает merge/push/delete.

Если пользователь просит простой merge без PR и repository policy это допускает, используй обычный git merge workflow; не создавай искусственный PR только ради процесса.

## Conflict policy

При conflict:

1. не выбирай автоматически «ours/theirs» для неизвестного содержимого;
2. пойми смысл обеих сторон;
3. сохрани независимые изменения;
4. повторно запусти релевантные проверки.

## Dangerous operations

Не используй без явного разрешения:

- `git push --force` / `--force-with-lease`;
- destructive reset на пользовательской работе;
- массовое удаление untracked files;
- history rewrite.

## Status synchronization

Не обновляй evidence level stage как `merged`, пока merge не подтверждён target branch/evidence.
