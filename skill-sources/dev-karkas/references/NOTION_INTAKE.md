# Notion Idea Intake

Цель: превращать человеческий brainstorm в качественный инженерный backlog, не смешивая идею с подтверждённым планом реализации.

## Source scope

Сначала прочитай schema/discovery policy в `PROJECT_REGISTRY.md`. Фактические project bindings глобальный Skill не хранит: найди внешний root по явному названию/URL, затем подтверди mapping полным fetch/read-back.

Обычный путь:

```text
Notion
└── Идеи
    └── <Project>
        ├── note A
        ├── note B
        └── ...
```

Если известна страница `<Project>`, предпочитай поиск, ограниченный этой страницей и её потомками. Не сканируй весь workspace без необходимости.

## Intake workflow

### 1. Discover

Найди:

- страницу `Идеи`;
- страницу нужного проекта;
- дочерние заметки и релевантные фрагменты;
- признаки того, что заметка уже обработана.

### 2. Fetch enough context

Для каждой потенциально полезной заметки прочитай достаточный контекст. Не делай prompt из одного search highlight, если полная заметка содержит ограничения или альтернативы.

### 3. Classify

Присвой одну или несколько категорий:

- IDEA;
- FEATURE;
- UX;
- CONTENT;
- ARCHITECTURE;
- SECURITY;
- INFRASTRUCTURE;
- PERFORMANCE;
- TESTING;
- RESEARCH;
- COMMERCIAL;
- DUPLICATE;
- ALREADY_IMPLEMENTED;
- NEEDS_DECISION;
- NOT_ACTIONABLE_YET.

### 4. Cross-check repository

Перед генерацией prompt проверь:

- код;
- DESIGN / architecture docs;
- ROADMAP;
- AI_PLAN / AI_STATUS;
- existing PROMPTS/BACKLOG;
- decisions;
- тесты и TODO, если релевантно.

Никогда не создавай новый prompt, если идея уже реализована или существующий prompt её адекватно покрывает.

### 5. Refine

Преврати заметку в инженерно понятную формулировку:

- problem / opportunity;
- user value;
- scope;
- known constraints;
- unknowns;
- dependencies;
- security/performance implications;
- возможные альтернативы.

Если идея требует продуктового/архитектурного решения, создай `NEEDS_DECISION`, а не притворяйся, что решение принято.

### 6. Build prompt

Если идея достаточно определена, создай prompt по `PROMPT_TEMPLATE.md` в `PROMPTS/BACKLOG/` или в принятом проектом аналоге.

### 7. State machine

Используй логическое состояние:

```text
IDEA
  ↓
REFINED
  ↓
PROMPT_READY
  ↓
APPROVED
  ↓
IMPLEMENTING
  ↓
DONE
```

Допустимы боковые состояния:

```text
NEEDS_DECISION
DUPLICATE
ALREADY_IMPLEMENTED
REJECTED
BLOCKED
```

Не переходи из `IDEA/REFINED/PROMPT_READY` в реализацию без явного approval policy проекта или прямого поручения пользователя.

## Запись обратно в Notion

Если write access разрешён и формат страницы это позволяет, после обработки можно добавить минимальную метаинформацию:

- classification;
- state;
- repository/project;
- generated prompt path;
- duplicate / implemented reference;
- краткую причину решения.

Не переписывай исходную идею. Сохраняй авторский brainstorm как source material.

## Дедупликация

Считай две идеи потенциальными дублями, если они решают одну проблему, даже если сформулированы разными словами. При объединении:

1. сохрани все уникальные требования;
2. выбери один канонический prompt;
3. оставь ссылки/метки на объединённые источники;
4. не теряй спорные альтернативы — вынеси их в decision section.

## Автоматическая реализация запрещена по умолчанию

Notion `Идеи` — входной backlog, а не очередь shell-команд. Обработка идеи может автоматически доходить до `PROMPT_READY`, но реализация требует approval, если project policy явно не разрешает иначе.
