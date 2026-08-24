# Project registry contract

Этот файл описывает только schema, discovery policy и validation contract. Он не хранит фактический список пользовательских проектов, реальные Notion page IDs, repository names или абсолютные project paths.

## Schema внешней привязки

Project-aware внешний слой при необходимости может хранить:

```text
project_id
display_name
repository_url_or_path
notion_root_url_or_id
status
overlay_path
required_docs
validation_state
last_verified_at
```

## Discovery policy

1. Определи текущий repository из Git root/cwd и ближайшего project `AGENTS.md`.
2. Ищи внешний project root по явному названию/URL пользователя и проверяй полный page/repository context.
3. Не считай search highlight или совпадение имени доказанной привязкой.
4. Перед записью или реализацией сверь repository, SPEC, status и project-local instructions.
5. Если mapping неоднозначен, сохрани материал во внешнем Ideas/staging layer и пометь `BLOCKED`; не добавляй реальный inventory в global КАРКАС.

## Где хранить actual inventory

Фактические привязки принадлежат project-aware внешнему слою, например Notion `Projects`, либо machine-local registry вне versioned active governance. Такой registry не должен содержать secrets и не становится источником требований продукта.

## Синтетический пример

```text
project_id: example-project-a
repository_url_or_path: <discovered-project-root>
notion_root_url_or_id: <verified-external-root>
validation_state: verified | stale | blocked
last_verified_at: YYYY-MM-DD
```

Синтетический пример нельзя заменять реальным пользовательским inventory внутри этого файла.
