# Node.js / Corepack / package manager policy

## Назначение

Канонические правила AI Dev Team для Node.js,
Corepack, npm, pnpm и Yarn, особенно на Windows.

Проектные overlays не должны копировать этот документ,
если у проекта нет действительно уникального toolchain requirement.

## Источники истины

Перед установкой dependencies определи:

1. `packageManager` в ближайшем корневом `package.json`;
2. lockfile;
3. workspace configuration;
4. `engines.node`;
5. `.node-version`, `.nvmrc` или аналогичный runtime pin;
6. требования используемого framework/tooling.

Используй пересечение всех ограничений.

Если требования несовместимы — остановись и исправь toolchain contract.
Не пытайся чинить несовместимость случайной сменой package manager.

## Package manager

Если проект содержит:

`packageManager: "pnpm@X.Y.Z"`

то pnpm этой версии является каноническим manager.

Нельзя использовать `npm install`, `npm ci` или Yarn
как fallback для pnpm-проекта.

Аналогичное правило действует для npm/Yarn-проектов.

Lockfile другого package manager не создаётся.

Предпочтительный default нового совместимого Node/JS/TS project — pnpm согласно
[`dependency-management.md`](dependency-management.md). Исключение, shared store,
clean restore и migration proof определяются там; этот документ уточняет только
Node/Corepack behavior.

## Exact version

Предпочитай exact package-manager version в `packageManager`.

Не использовать `latest` в reproducible project/CI workflow.

Изменение major/minor package manager является отдельным toolchain change
с review compatibility и lockfile.

## Windows

В PowerShell сначала используй нормальную команду manager:

`pnpm`
`npm`
`yarn`

Если Windows Execution Policy блокирует только `.ps1` shim,
допускается вызов соответствующего `.cmd`:

`pnpm.cmd`
`npm.cmd`

Это shell-level fallback, а не смена package manager.

Запрещено автоматически менять глобальную PowerShell Execution Policy
ради запуска проекта.

## Preflight

При проблеме сначала проверь:

`node --version`

`npm --version`

`corepack --version`

`where.exe node`

`where.exe pnpm.*`

`Get-Command node`

`Get-Command pnpm -All`

Не удаляй файлы из PATH до определения,
какой executable или shim фактически запускается.

## Corepack

Если Corepack доступен и совместим с используемой версией Node.js,
он является предпочтительным способом исполнения project-pinned pnpm/Yarn.

После установки/изменения Node при необходимости:

`corepack enable`

Для современного Corepack предпочитай project-aware команды:

`corepack install`

или явный approved toolchain change через:

`corepack use <manager>@<version>`

`corepack use` изменяет project metadata
и поэтому не должен применяться как автоматический repair.

Не использовать `corepack ... @latest`
в production/reproducible workflow без отдельного решения.

## Corepack compatibility

Не предполагай, что Corepack всегда bundled с Node.js.

Перед установкой или обновлением Corepack проверь совместимость
его версии с используемым Node.js.

Не выполняй автоматически:

`npm install -g corepack@latest`

если текущий Node может быть несовместим с latest Corepack.

Сначала compatibility check, потом toolchain change.

## pnpm installation fallback

Допустимая цепочка:

project-pinned pnpm
→ тот же exact pnpm через совместимый Corepack
→ тот же exact pnpm через заранее разрешённый installation method
→ fail closed / исправление toolchain

Недопустимая цепочка:

pnpm сломан
→ npm install
→ получить второй lockfile
→ продолжить как будто всё нормально

## Frozen lockfile

Для существующего проекта по умолчанию:

`pnpm install --frozen-lockfile`

или эквивалентный строгий режим package manager.

Если lockfile не соответствует `package.json`,
не отключай frozen mode автоматически.

Это изменение dependencies/toolchain и должно быть явным.

## Dependency changes

Добавляй/удаляй dependency только через канонический manager.

Например:

`pnpm add <package>`

`pnpm add -D <package>`

`pnpm remove <package>`

Не редактируй lockfile вручную.

После dependency change проверяй diff package manifest + lockfile.

## Workspaces

Если существует `pnpm-workspace.yaml`,
выполняй команды из workspace root,
кроме случаев, когда project contract явно говорит иначе.

Для target package предпочитай фильтрацию:

`pnpm --filter <package> <command>`

Не устанавливай отдельное независимое dependency tree
в workspace package без необходимости.

## CI

CI использует:

- project-pinned package manager;
- совместимый Node runtime;
- frozen lockfile;
- reproducible install;
- cache только как ускорение, не как источник истины.

Cache failure должен приводить к обычной установке,
а не к пропуску dependency validation.

## Install scripts и supply chain

Новые packages рассматриваются как исполняемый supply-chain input.

Перед новой production dependency проверь:

- package origin;
- maintenance;
- version;
- install/postinstall scripts;
- необходимость dependency.

Не добавляй package только как случайный fallback
для сломанной локальной установки.

## Troubleshooting

При ошибке сначала классифицируй:

- incompatible Node;
- incompatible package-manager version;
- broken Corepack shim;
- PATH collision;
- PowerShell shim issue;
- corrupted local install/cache;
- lockfile mismatch;
- actual project dependency error.

Repair должен исправлять установленную причину,
а не маскировать её альтернативным manager.

## Fallback Policy

Все toolchain fallback'и подчиняются:

`rules/fallback-policy.md`

Toolchain fallback не может:
- менять package manager незаметно;
- ослаблять lockfile guarantees;
- менять Node/package-manager major без явного решения;
- создавать второй источник истины.
