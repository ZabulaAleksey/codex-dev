# Существенные решения

## 2026-08-27 — Один канонический контракт архитектурно завершённых этапов

**Статус:** принято.

**Контекст:** прежние stage surfaces требовали dependencies, acceptance и tests, но позволяли
прочитать заблокированный gate как допустимый для `DONE`, не отделяли scaffold от production
evidence и не запрещали forward dependency на будущую обязательную инфраструктуру. Дополнительно
`TESTING_POLICY.md` называл tests источником требований, а project-file references расходились в
порогах полного staged overlay. Detailed stage source также отсутствовал в минимальном
task-aware context route между SPEC и `AI_PLAN`.

**Решение:** стабильное требование принадлежит `specs/system.spec.md` (`FR-007`/`AC-007`), а
единственный полный lifecycle/evidence contract — `rules/governance.md`. Planning/execution Skills,
`dev-karkas`, templates и workflow содержат только ссылки и поля проекции. Полный project overlay
имеет единый baseline из governance; UI `DESIGN.md` остаётся условным. Tests являются исполняемым
контрактом принятого поведения и evidence, но не первичным source of requirements. Stage-bound
задача задаёт stable `Stage ID` в `docs/AI_PLAN.md`; существующий SessionStart/SubagentStart hook
проецирует только один exact unique heading record из `prompts/STAGES.md`, а не весь catalog.

**Альтернативы:** копирование полной нормы во все Skills отклонено из-за drift; эвристический parser
произвольных `prompts/STAGES.md` отклонён до появления versioned schema/migration, чтобы не создать
false positives и несовместимость существующих project overlays. Exact heading selector принят как
узкая context projection: он не интерпретирует DAG, prerequisites, PASS criteria или evidence.

**Последствия:** future stage не может задним числом завершить primary path предыдущего stage;
mock/stub-only результат остаётся `scaffolded`; structural global test защищает маршрутизацию,
production hook test подтверждает путь `AI_PLAN → selected STAGES record`, а фактический
end-to-end PASS stage по-прежнему подтверждается project evidence и review. Invalid, missing,
ambiguous или oversized selector даёт видимый `DEGRADED` context и запрещает completion claim.

## 2026-08-26 — Обязательный documentation audit без формального churn

- Решение: перед завершением task/stage и после merge всегда выполнять Completion
  Documentation Synchronization Gate для `README`, `AI_PLAN`, `AI_STATUS`, `ROADMAP`,
  stage tracker и других state-bearing документов.
- Причина: условное «обновить документацию при необходимости» не выявляло stale plan/status,
  старое verification evidence и возможности README, уже не совпадающие с кодом.
- Альтернатива: обновлять все документы и даты после каждой задачи; отклонена, потому что
  создаёт шум и скрывает содержательные изменения.
- Последствия: аудит обязателен, mutation зависит от фактов; после merge gate повторяется по
  target branch, а handoff различает обновлённые и проверенные без изменений документы.

## 2026-08-25 — Один канонический Backend DX contract с opt-in validation

- Решение: полный Backend Developer Experience contract хранится только в
  `rules/backend-dx.md`; `AGENTS.md` и framework docs содержат routing, Skill —
  процедуру, project `docs/project-context.md` — только delta.
- Applicability: `BDX-L0..L3` определяется фактической архитектурой. Validator не
  угадывает backend по Python/Node manifests и включается только при явном
  `## Backend DX Delta`.
- Автоматизация: расширяется существующий read-only project validator; новый hook,
  task runner, runtime dependency и devops/platform role не создаются.
- Причина: policy должна выявлять hidden setup, unsafe reset, stale config/docs и
  CI drift без создания второго framework или false positives для non-backend
  проектов.
- Последствия: reusable template хранится в `templates/`, runtime Skill синхронизируется
  штатным source/runtime flow, а fixture evidence доказывает только framework
  contract и не считается production clean-room evidence конкретного backend.

## 2026-08-20 — Brownfield Reconciliation Gate

- Решение: перед bootstrap/refresh классифицировать repository и для brownfield выполнять отдельный read-only reconciliation.
- Причина: фактическая реализация и результаты baseline-тестов должны сохраняться source of truth; шаблон не должен молча перезаписывать продуктовые решения.
- Статусы matrix: `KEEP`, `ADD`, `ADAPT`, `MERGE`, `CONFLICT`, `SUPERSEDED`, `FORBIDDEN_TO_OVERWRITE`.
- Последствие: unresolved `CONFLICT` блокирует mutation, а `FORBIDDEN_TO_OVERWRITE` запрещает автоматическую запись. После refresh новые baseline failures считаются regression.

## 2026-08-13 — Project overlay вместо копии AI Dev Team

- Решение: project хранит только локальные требования, документы и подтверждённые расширения.
- Причина: исключить drift и конфликт глобальных agents, Skills, hooks, rules и workflow.
- Альтернатива: копировать общий набор в каждый repository; отклонена из-за дублирования.
- Последствие: точная копия глобальной capability является ошибкой validator.

## 2026-08-13 — Один Markdown-каталог rollout

**Статус:** superseded 2026-08-20.

- Решение: использовать только `docs/PROJECT_CATALOG.md`.
- Причина: человеку нужен один источник lifecycle, blockers и следующего действия.
- Альтернатива: дополнительный JSON/YAML registry; отклонена как второй источник истины.

## 2026-08-13 — Read-only validator

- Решение: validator принимает путь одного repository, ничего не исправляет и поддерживает human/JSON output.
- Причина: проверка должна быть повторяемой и безопасной для независимых рабочих копий.
- Последствие: неполный или спорный repository получает issue; изменение выполняется отдельным этапом.

## 2026-08-20 — Один канонический контракт Fallback Policy

- Решение: общий контракт retry/fallback/degraded/fail-closed хранится только в `rules/fallback-policy.md`.
- Причина: fallback-правила не должны расходиться между agents, Skills, security docs и проектами.
- Проекты наследуют общий контракт и при необходимости создают только `docs/FALLBACKS.md` с предметной delta.
- `SECURITY.md` остаётся владельцем security invariants, `DECISIONS.md` — причин решений, `ARCHITECTURE.md` — границ и recovery interfaces.
- Silent fallback и fallback, ослабляющий security или evidence, запрещены.

## 2026-08-20 — ДЕВ не владеет live-статусом product repositories

**Статус:** принято.

**Решение:** AI Dev Team хранит общие инженерные правила, policies, validators,
project framework и reusable automation, но не хранит канонический live inventory
этапов, blockers или очереди отдельных product repositories.

Состояние конкретного продукта принадлежит его собственным `AI_STATUS`,
`AI_PLAN`, `ROADMAP` и другим project-specific источникам.

`validate_project_overlay.py` остаётся универсальным read-only инструментом,
который запускается для явно выбранного repository, но ДЕВ не обязан хранить
глобальную очередь таких repositories.

**Причина:** жизненный цикл общей инженерной инфраструктуры не должен зависеть
от состояния её потребителей.

**Последствия:**

- `docs/PROJECT_CATALOG.md` удаляется;
- blockers конкретных продуктов не входят в `docs/AI_STATUS.md` ДЕВ;
- product repository не становится следующим этапом ДЕВ;
- исторический pilot/forward-test может оставаться evidence в истории решений,
  если он действительно происходил;
- общие project-overlay rules и validator сохраняются.

## 2026-08-20 — Канон и runtime глобальной конфигурации разделены

**Статус:** superseded 2026-08-23 консолидацией в `~/.codex`.

**Решение:** прежний workspace source tree оставался единственным versioned source-of-truth для managed AGENTS, agents, hooks и rules. `~/.codex/config.toml` оставался runtime-specific и менялся только ограниченным идемпотентным normalizer; installer не перезаписывал его целиком.

**Причина:** слепая синхронизация теряла полезные local deltas, а полное сохранение installed-файлов закрепляло drift, Unicode defect и небезопасные настройки.

**Последствия:**

- reviewed model pins и routing сначала попадают в канон;
- `-SyncManaged` является явным режимом синхронизации;
- plugin имеет приоритет над дублирующим static MCP;
- inline secrets и broad trust являются validation errors;
- host-managed browser paths/hashes не угадываются;
- внешняя ротация credential и интерактивный trust hooks не автоматизируются.

## 2026-08-23 — `~/.codex` является Git-корнем и единственным каноном ДЕВ

**Решение:** перенести versioned AI Dev Team в `~/.codex` и использовать
`AGENTS.md`, `agents/`, `hooks/`, `skills/` и `rules/` непосредственно из активного
пользовательского слоя Codex. Product repositories остаются независимыми Git roots
в `~/codex-workspace/*`.

**Причина:** прежняя схема «канон в `~/codex-workspace` → installed-копия в
`~/.codex` / `~/.agents`» создавала drift и два конфликтующих `AGENTS.md`.

**Альтернативы:**

- оставить installer и две копии — отклонено из-за повторного drift;
- поместить repository в `~/.codex/dev` — отклонено, потому что глобальный
  `AGENTS.md`, hooks и agents снова оказались бы вне Git root либо потребовали бы копирования.

**Последствия:**

- runtime state, secrets, sessions, plugins, cache и `config.toml` исключены из Git;
- engineering Markdown rules сосуществуют с runtime `.rules` в `~/.codex/rules`;
- project overlays ссылаются на `~/.codex`, но не копируют глобальную automation;
- `install-global.ps1` стал проверкой canonical placement, а не copy/sync installer;
- откат versioned части выполняется Git, runtime state не затрагивается.

## 2026-08-24 — Skills разделены на versioned source и runtime projection

**Статус:** принято; supersedes часть решения 2026-08-23 о непосредственном использовании `~/.codex/skills` для Skills ДЕВ.

**Решение:** versioned source reusable Skills хранится в `~/.codex/skill-sources`. Единственная active runtime-проекция ДЕВ находится в `~/.agents/skills`. `tools/sync_global_skills.py` сравнивает file set/SHA-256, не удаляет unmanaged Skills и перед заменой drifted runtime Skill переносит прежнюю копию в `~/.agents/.migration-backup`.

**Причина:** Codex использует `.codex/skills` и `.agents/skills` как discovery roots, поэтому одинаковые Skills обнаруживались дважды. При этом source должен оставаться в Git для cross-device восстановления.

**Альтернативы:** отдельный Git repository `.agents` отклонён из-за отсутствия отдельного remote и появления второго lifecycle; junction отклонён из-за двойного discovery и неясной Git-portability на Windows.

**Последствия:** host-managed `.codex/skills/.system` и unmanaged Skills не затрагиваются; после clone выполняется `install-global.ps1`; runtime drift является validation error.

## 2026-08-24 — workspace flatten и единый project governance contract

**Статус:** принято.

**Решение:** product repositories располагаются непосредственно в `~/codex-workspace/<project>`, canonical stage source — `prompts/STAGES.md`, а общие lifecycle/evidence/database/security/tooling policies находятся в `rules/governance.md`.

**Причина:** промежуточный `projects/`, смешанные prompt formats и неполные project state contracts создавали path coupling и затрудняли восстановление новой сессии.

**Последствия:** physical moves проверяются по одному repository; dirty/merge state сохраняется backup refs; legacy stage files удаляются только после semantic content/link audit; внешние projections остаются derived.

## 2026-08-24 — Дополнительные Markdown-файлы изолируются в `docs/notes`

**Статус:** принято.

**Решение:** непосредственно в `docs/` создаются только обязательные и условные канонические документы КАРКАСА. Новый долговечный Markdown без собственной канонической роли хранится в `docs/notes/<topic>.md`; временный scratch и одноразовые audit outputs не коммитятся.

**Причина:** произвольные документы на верхнем уровне `docs/` размывают источник истины и увеличивают контекстный шум.

**Последствия:** сначала обновляется существующий canonical source; правило применяется forward-only; legacy files переносятся только после semantic/link audit без потери содержания.
