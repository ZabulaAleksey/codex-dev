# Project registry

Этот файл хранит стабильные пользовательские привязки, которые помогают `dev-karkas` не искать канонические корни проекта заново. Он не заменяет project-specific `AGENTS.md` и не должен содержать secrets.

## Tutor

- Canonical Notion root title: `Tutor`
- Canonical Notion page ID: `3c161ed8-f246-8162-9e2a-c13427218b33`
- Canonical Notion URL: `https://app.notion.com/p/3c161ed8f24681629e2ac13427218b33?pvs=204`
- Purpose: продуктовая концепция, учебный опыт, архитектура, AI, монетизация и исторический backlog.
- Idea-processing rule: материалы Tutor являются уровнем идей/целевой архитектуры; не переносить их в SPEC/ROADMAP и не реализовывать автоматически без отдельного решения/approval.

Known child sources useful for intake:

- `Исходные идеи Tutor` — исторические идеи, ранее находившиеся в общей странице `Идеи`;
- `Банк идей Tutor` — текущий банк идей;
- `Общие принципы Tutor` — концептуальные принципы и целевая архитектура;
- `Безопасность, abuse и защита от перегрузки` — security/abuse backlog;
- `UX, дизайн и A11y` — UX/accessibility backlog;
- `AI, вузовский контент и контекст страницы` — AI/content context.

### Repository resolution

Не хранить здесь выдуманный локальный путь. Определять репозиторий Tutor из текущего Codex project/cwd, project metadata, GitHub/Notion ссылки или явной пользовательской привязки. После надёжного определения путь/URL можно добавить сюда.

## Добавление проекта

Для нового проекта добавь:

```text
## <Project>
- Canonical Notion root title:
- Canonical Notion page ID:
- Canonical Notion URL:
- Repository:
- Notes:
```

Не добавляй credentials, tokens или приватные ключи.
