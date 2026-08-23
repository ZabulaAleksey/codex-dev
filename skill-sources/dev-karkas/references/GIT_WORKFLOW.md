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

Не обновляй AI_STATUS как `merged`, пока merge не подтверждён target branch/evidence.
