# Dependency management policy

## Назначение и границы

Эта policy — единый канонический контракт выбора dependency manager, lockfile,
штатного shared cache/store и clean restore. Она применяется к независимым project
repositories; shared storage никогда не означает shared project state. Перед
созданием либо изменением project dependency context загрузите эту policy вместе с
подходящим stack rule.

## Preferred defaults

| Ecosystem | Preferred manager | Manifest + lockfile | Shared storage | Project-local materialization |
|---|---|---|---|---|
| Node / JavaScript / TypeScript | pnpm | `package.json` + `pnpm-lock.yaml` | pnpm content-addressable store | isolated virtual store by default |
| Python | uv | `pyproject.toml` + `uv.lock` | uv cache | isolated environment per project |
| Rust | Cargo | `Cargo.toml` + `Cargo.lock` when applicable | `CARGO_HOME` | `target/` |
| Go | Go Modules | `go.mod` + `go.sum` | `GOMODCACHE`, `GOCACHE` | none by default |
| .NET | dotnet + NuGet | project/solution manifest + lock mode where adopted | global NuGet packages | `bin/`, `obj/` |
| Java / Kotlin | Gradle | Gradle files + wrapper/lock policy | `GRADLE_USER_HOME` | `.gradle/`, `build/` |
| C / C++ | vcpkg or Conan | manager manifest + lock/profile/config | native manager cache | build tree |
| PHP | Composer | `composer.json` + `composer.lock` | Composer cache | `vendor/` |
| Dart / Flutter | pub | `pubspec.yaml` + `pubspec.lock` where applicable | pub cache | `.dart_tool/` |
| Swift | SwiftPM | `Package.swift` + `Package.resolved` where applicable | SwiftPM cache | `.build/` |

Defaults are not bans. A project may keep another manager when toolchain
compatibility, upstream repository contract, deployment, migration risk, vendor or
CI constraint requires it. Record the rationale in `docs/DEPENDENCIES.md` under
`Dependency-manager exception`; “familiarity” is not sufficient.

## Required project dependency contract

When the ecosystem is determined, `docs/DEPENDENCIES.md` (or an existing canonical
architecture/dependency document) records: canonical manager; manifest and
lockfile; `Source of truth`; shared cache/store; project-local materialization;
`Clean restore` command; cleanup classification; CI restore command; and any
exception rationale. Do not create a duplicate document when this content belongs
in an existing canonical dependency contract.

Git stores source, manifests, lockfiles and configuration—not dependency trees or
rebuildable outputs. Do not track `node_modules/`, `.venv/`, `venv/`, `target/`,
`dist/`, `build/`, `.next/`, `.nuxt/`, `.svelte-kit/`, `.turbo/`, `coverage/`,
`__pycache__/`, Python tool caches, `bin/`, `obj/` or `.gradle/` unless a
stack-specific exception records why the material is required runtime/source data.
Classify unknown directories before deleting them: `REBUILDABLE`, `EXPENSIVE_CACHE`,
`REQUIRED_RUNTIME`, `UNKNOWN` or `USER_DATA`. Only verified rebuildable material may
be cleaned.

## Reproducibility and migrations

Use exactly one canonical manager and lockfile per ecosystem in a project. A
competing lockfile is drift unless `Dependency-manager exception` documents a
compatibility contract. Do not hand-edit lockfiles.

Migration sequence: preserve dirty work and current lockfile; establish a recovery
point; run the existing checks; generate the target lockfile with the canonical
manager; compare the graph; update CI/docs/scripts; prove clean restore plus
applicable build, lint/typecheck, tests and smoke; only then delete obsolete
lockfiles or dependency state. A changed graph, test failure, offline dependency,
dirty repository or unknown directory stops cleanup.

Toolchains may be global (for example pnpm, uv, Cargo, Go, dotnet or JDK), but
project dependencies must be manifest- and lockfile-declared. Never share a manual
`node_modules` or one Python environment between independent repositories.

## Ecosystem specifics and fallback

pnpm uses the machine-level content-addressable store with an isolated linker by
default. `virtualStoreType: global` requires a representative compatibility pilot;
fallback is the shared store plus project-local virtual store. PnP is not a default.

uv uses its shared cache while environments remain isolated. Centralized environment
storage requires a tooling/IDE/CI pilot; fallback is project-local `.venv` plus the
shared uv cache. Cargo does not use a shared `target` directory by default. Go,
NuGet, Gradle and native managers use their official caches, never hand-made shared
dependency folders.

All fallback and migration stop conditions follow
[`fallback-policy.md`](fallback-policy.md): retain the known working state, record
the exception, and fail closed instead of silently switching managers or weakening
lockfile guarantees.
