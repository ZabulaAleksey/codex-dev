---
name: dev-karkas
description: Bootstrap, audit, maintain, and evolve software projects using the user's DEV / КАРКАС engineering framework. Use for repository bootstrapping, project structure and governance, AGENTS.md and AI planning/status files, architecture/security/testing/fallback policies, prompt and stage generation, Notion Ideas intake, backlog refinement, implementation planning, project audits, and keeping documentation synchronized with verified repository state.
---

# DEV / КАРКАС

Работай как orchestration-layer ДЕВ: сначала понимай существующий проект, затем добавляй только недостающее. Не превращай КАРКАС в механическое копирование шаблонов.

## Главный принцип

1. Сначала исследуй репозиторий и доступный проектный контекст.
2. Определи, какие части КАРКАСА уже существуют и являются каноническими.
3. Не дублируй существующие правила, документы, промпты, этапы, агенты, skills, hooks или конфигурацию.
4. Меняй минимально необходимый набор файлов.
5. Не утверждай, что что-либо реализовано, проверено, совместимо или слито, пока это не подтверждено кодом, тестами, git-состоянием или другим надёжным evidence.
6. Сохраняй пользовательский контент и существующие решения. Не удаляй содержимое ради «чистой структуры» без явного разрешения.
7. Крупные решения фиксируй как решения, а не прячь в случайных промптах.

## Выбор режима

Определи режим работы из запроса:

- **bootstrap** — навесить КАРКАС на новый или существующий репозиторий;
- **audit** — проверить полноту и непротиворечивость КАРКАСА без лишних изменений;
- **maintain** — обновить статусы, документы и правила после подтверждённых изменений;
- **idea-intake** — обработать идеи из Notion и превратить их в качественный backlog / implementation prompts;
- **prompt-build** — превратить выбранную идею, feature или архитектурное решение в исполнимый PROMPT;
- **execute** — реализовать явно одобренный prompt/этап, провести проверки и синхронизировать подтверждённый статус.

Если режим однозначно следует из задачи, не проси пользователя выбирать его.

## Обязательные references

Читай только те references, которые нужны текущей задаче:

- `references/KARKAS.md` — канонический состав и логика КАРКАСА;
- `references/PROJECT_REGISTRY.md` — schema и discovery policy внешних project-aware привязок без actual inventory;
- `references/PROJECT_FILES.md` — назначение файлов и правила их создания;
- `references/NOTION_INTAKE.md` — Notion `Идеи → <проект> → backlog`;
- `references/PROMPT_TEMPLATE.md` — стандарт implementation prompt;
- `references/STATUS_WORKFLOW.md` — AI_PLAN / AI_STATUS / evidence / этапы;
- `references/TESTING_POLICY.md` — тесты, quality gates и evidence;
- `references/SECURITY_BASELINE.md` — security baseline и abuse protection;
- `references/FALLBACK_POLICY.md` — graceful degradation и fallback policy;
- `references/AUTONOMY_POLICY.md` — что делать автоматически, а что требует явного разрешения;
- `references/GIT_WORKFLOW.md` — ветки, commit/PR/merge и работа с git;
- `references/ARCHITECTURE_POLICY.md` — API-first, границы слоёв, telemetry, adapters, SDK/CLI/MCP.

## Универсальный workflow

### 1. Inspect

Исследуй:

- дерево репозитория;
- `AGENTS.md` / `AGENTS.override.md`;
- README, SPEC, DESIGN, SECURITY, ROADMAP;
- AI_PLAN, AI_STATUS, PROGRESS, DEV_LOG, LEARNING, decisions;
- `PROMPTS/`, docs, tests, CI/CD;
- package/workspace manifests;
- dependency manager, canonical lockfile, CI restore command and tracked generated
  dependency/build directories when an ecosystem is present;
- наличие backend/runtime service, его уровень `BDX-L0..L3`, command/config/service
  surface и project-specific `Backend DX Delta`;
- существующие skills, hooks, MCP и agent config;
- git status и последние релевантные изменения, если git доступен.

Не создавай дубликат файла только потому, что его имя отличается. Сначала выясни семантическое назначение.

### 2. Classify

Определи:

- зрелость проекта;
- фактический стек;
- существующие project-specific правила;
- фактический Backend DX applicability level и применимые gaps по
  `~/.codex/rules/backend-dx.md`;
- недостающие части КАРКАСА;
- конфликты между документацией и кодом;
- потенциально устаревшие заявления без evidence.

### 3. Plan minimal changes

Составь небольшой план изменений. Предпочитай:

- дополнение существующего канона вместо параллельного документа;
- ссылку вместо дублирования;
- локальный project overlay вместо копирования глобальных правил;
- конкретный prompt вместо размытого TODO.

### 4. Apply

Вноси изменения атомарно. Не переписывай большие документы целиком, если достаточно точечной правки.

### 5. Validate

Запусти релевантные проверки из репозитория. Не придумывай команды. Ищи их в manifests, README, CI, scripts и existing tooling.

### 6. Synchronize evidence

Обновляй статус только после фактического подтверждения. Разделяй:

- реализовано;
- проверено;
- известно как ограничение;
- запланировано;
- идея;
- неизвестно / требует evidence.

### 7. Report

В конце кратко сообщи:

- что изменено;
- что проверено;
- какие проверки не удалось выполнить;
- какой следующий шаг является первым ещё не выполненным.

## Notion

Если задача относится к идеям/планированию и Notion доступен:

1. Прочитай schema/discovery policy в `references/PROJECT_REGISTRY.md`; actual inventory в global Skill отсутствует намеренно.
2. Найди внешний корень `Идеи`/`Projects` и страницу проекта по явному названию или URL пользователя, затем проверь mapping полным fetch/read-back.
3. Ограничь поиск страницей проекта и её потомками, когда это возможно.
4. Следуй `references/NOTION_INTAKE.md`.
5. Не реализуй сырую идею автоматически только потому, что она присутствует в Notion.

Если Notion недоступен, не выдумывай его содержимое. Продолжи с локальным контекстом и явно отметь границу доступных данных.

## Prompt generation

Любой implementation prompt должен быть достаточно самодостаточным, чтобы другой агент мог выполнить его без пересказа текущего чата. Следуй `references/PROMPT_TEMPLATE.md`.

## Защита от дрейфа

Считай источником истины в порядке конкретности:

1. фактическое состояние репозитория и результаты проверок;
2. явно утверждённая спецификация / архитектурное решение;
3. project-specific `AGENTS.md` и project policy;
4. AI_STATUS / AI_PLAN;
5. backlog / PROMPTS;
6. Notion-идеи и brainstorm.

Более низкий уровень не должен молча переписывать более высокий.
