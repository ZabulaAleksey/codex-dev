# Спецификация политики управления зависимостями

Статус: Действует
Версия: 1.0

## 1. Назначение

Закрепить единый, воспроизводимый и безопасный процесс выбора dependency manager,
lockfile, штатного shared cache/store и clean restore для независимых project
repositories, не превращая их в общий workspace и не изменяя их без явной миграции.

## 2. Область

SPEC охватывает global policy, routing, project-framework guidance и read-only
проверки overlay для Node/JS/TS, Python, Rust, Go, .NET, Java/Kotlin, C/C++, PHP,
Dart/Flutter и Swift.

## 3. Вне области

- массовая миграция существующих product repositories;
- установка или обновление toolchain и shared caches;
- автоматическое удаление lockfiles, dependency directories либо build caches;
- включение pnpm global virtual store, PnP или централизованных uv environments
  без отдельного compatibility pilot.

## 4. Функциональные требования

### FR-001 Канонический выбор

Для каждого project overlay КАРКАС определяет ecosystem, canonical manager,
manifest, lockfile, штатный shared cache/store, project-local materialization,
cleanup policy и CI clean-restore command. Preferred matrix: Node/JS/TS — pnpm;
Python — uv; Rust — Cargo; Go — Go Modules; .NET — NuGet; Java/Kotlin — Gradle;
C/C++ — vcpkg или Conan; PHP — Composer; Dart/Flutter — pub; Swift — SwiftPM.

### FR-002 Исключения и независимость

Непредпочтительный manager допустим лишь с документированной причиной: toolchain,
upstream contract, deployment, legacy migration risk, vendor или CI constraint.
Независимые repositories не разделяют вручную `node_modules`, Python environment
или иной project state.

### FR-003 Воспроизводимость

Manifest и canonical lockfile являются source of truth. В project Git не
отслеживаются dependency directories и rebuildable build/cache outputs, кроме
документированных stack-specific exceptions. Clean restore command документируется
там, где manager/stack определяется из repository.

### FR-004 Drift checks

Read-only project-overlay validator сообщает competing Node lockfiles для
pnpm-declared project, missing uv lockfile для uv-declared project, tracked
dependency/build-cache directories и отсутствие dependency source-of-truth / clean
restore documentation, когда ecosystem определим по manifest. Reconciler показывает
dependency inventory и документированный drift в compatibility matrix без записи.

### FR-005 Fallback и миграция

Manager migration не удаляет старое рабочее состояние до clean-restore proof и
проверок. При incompatibility сохраняется existing manager как documented exception;
при внезапном изменении graph, test failure, dirty repository, network failure или
unknown directory операция останавливается.

## 5. Нефункциональные требования

### NFR-001 Безопасность

Validators и reconciler не изменяют target repository, Git configuration, caches или
toolchains. Dependency additions остаются project-declared; global install допустим
только для toolchain.

### NFR-002 Совместимость

Existing stable repositories не переводятся между managers только ради унификации.
Advanced shared-materialization modes требуют отдельного pilot и имеют documented
fallback к штатному shared cache/store и project-local materialization.

## 6. Критерии приёмки

- AC-001 Одна global policy описывает matrix, exception contract, source of truth,
  cache/materialization, cleanup и clean restore.
- AC-002 Rules router, Node policy, governance и fallback policy ссылаются на неё
  без копирования competing policy.
- AC-003 PROJECT_FRAMEWORK и dev-karkas guidance требуют dependency inventory и
  фиксируют выбранный manager в project context.
- AC-004 Validator и reconciler дают deterministic read-only results для dependency
  drift; целевые unit tests покрывают positive и negative cases.
- AC-005 Documentation/status отражает только подтверждённую global-framework
  реализацию и её границы.

## 7. Связь с тестами

| Требование | Тест |
|---|---|
| FR-004 | `tools.test_validate_project_overlay` |
| FR-004 | `tools.test_reconcile_project_framework` |

## 8. История изменений

- 2026-08-24 — создана для global dependency-manager policy migration.
