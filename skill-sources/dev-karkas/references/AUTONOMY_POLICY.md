# Autonomy policy

Цель: дать агенту максимум полезной автономии без тихих разрушительных действий.

## Обычно можно автоматически

При наличии задания и в пределах текущего worktree/repository:

- читать код и docs;
- искать Notion/GitHub/project context;
- создавать и править production code;
- создавать новые non-destructive docs/prompts;
- запускать существующие tests/build/lint;
- обновлять current record/NEXT в `docs/STAGES.md` на основе evidence;
- добавлять безопасные новые tests, если это требуется task/project policy;
- делать локальные non-destructive git operations;
- формировать commit/PR content, если workflow это предусматривает.
- после одного explicit master start автоматически продолжать единственный dependency-ready
  non-destructive slice и создавать/reuse отдельный Git worktree по bounded route;
- создавать compact launcher/handoff при context budget overflow.

## Требует особой осторожности / явного разрешения

- удаление страниц/баз/важных документов;
- массовое перемещение/перестройка Notion;
- destructive DB migration;
- production deployment;
- изменение billing/commerce;
- изменение authentication/security model с широким blast radius;
- secret creation/rotation/revocation;
- force push / history rewrite;
- merge в protected/main, если project policy не разрешает это явно;
- merge/push/worktree deletion на master integration/finalization boundary;
- удаление значительного объёма user data;
- irreversible external action.

## Запрещено как shortcut

- отключать security controls для прохождения теста;
- hardcode credentials;
- скрывать failing checks;
- подделывать status/evidence;
- удалять чужой/пользовательский контент «для упрощения»;
- обходить repository policy без прямого указания.

## Notion Ideas

Сырые идеи можно автоматически читать, классифицировать и доводить до `PROMPT_READY`. Автоматически переходить к реализации можно только при явной project policy или прямом поручении.
