# Model Routing Policy

## Область действия

Выбранная пользователем в чате модель остаётся моделью главного агента. Инструкции
не должны создавать впечатление, что она незаметно заменяется другой моделью.

Если оркестратор может выбирать модель и `reasoning_effort` субагента, используй
эту policy для делегирования. Если выбор модели средой недоступен, сохрани выбранную
модель и регулируй только доступный `reasoning_effort`.

## Базовая маршрутизация

Используй минимально достаточную модель:

До model route проверь deterministic-first ladder:

`tool/script → validator/parser/compiler/query → Skill + deterministic executor → bounded cheap
model → normal implementation → high reasoning → strongest available only after evidenced failure`.

`tools/spec_execution.py executor` выдаёт recommendation и escalation reason, но не меняет
выбранную пользователем модель. Failure deterministic path сохраняется как input Automation
Promotion Review; неизвестный root cause остаётся reasoning/debugging route.

| Класс задачи | Предпочтительная модель | Reasoning по умолчанию |
|---|---|---|
| Поиск файлов и символов, чтение документации, классификация, извлечение данных, простые преобразования, запуск и первичный анализ тестов | `gpt-5.6-luna` | `low` |
| Обычная реализация, frontend/backend, локальный рефакторинг, тесты и хорошо локализованный debugging | `gpt-5.6-terra` | `medium` |
| Архитектура, security-critical работа, важные публичные API, сложный debugging, concurrency/race conditions, риск потери данных и долгосрочные решения | `gpt-5.6-sol` | `high` |

Повышай `reasoning_effort` отдельно от модели:

- `low` — механические и хорошо ограниченные операции;
- `medium` — обычная реализация и анализ;
- `high` — неоднозначные, архитектурные и security-critical задачи;
- `xhigh` или `max` — только для самых сложных quality-first задач, когда дополнительная глубина оправдывает задержку и расход.

Не выбирай максимальный reasoning только потому, что он доступен. Если задача
решается на текущем уровне с выполнением acceptance criteria и quality gates,
не повышай уровень.

## Эскалация

Используй последовательность:

`Luna/low → Terra/medium → Sol/high → Sol/xhigh или Sol/max`.

Повышай уровень, если более лёгкая конфигурация не справилась после разумной
попытки, требования неоднозначны, тесты продолжают падать, обнаружен архитектурный
или security-риск, возможна потеря данных либо нужны существенные trade-offs.

Не повышай модель только из-за размера файла или количества строк.

## Лимиты, стоимость и устаревшие модели

При ограниченном бюджете или лимите сначала делегируй подходящие bounded-задачи
на `gpt-5.6-luna` с `low` reasoning. Для обычной реализации используй
`gpt-5.6-terra` с `medium`, если Luna недостаточна.

Не закрепляй модель только по предполагаемой цене. Цена, квоты и доступность
меняются; перед cost-driven fallback проверь, что модель доступна в текущей среде,
дешевле по актуальному тарифу и способна выполнить acceptance criteria.

Модели `Shark` в поддерживаемом наборе нет. `GPT-5.3-Codex-Spark` не является
базовым маршрутом: используй его только как явно доступный approved fallback после
проверки актуальной цены, лимита и capability. Не подменяй им Luna автоматически.

Fallback подчиняется `rules/fallback-policy.md`:

`preferred model → approved available fallback → capability check → выполнение`

Если fallback не обеспечивает требуемые точность, reasoning depth, context capacity,
security guarantees или tool capability, заверши операцию fail closed либо эскалируй.

## Continuous master slices

`master-execution` state фиксирует для каждого slice `model_class` (`LOW | MEDIUM | HIGH |
FRONTIER`) и `reasoning_effort` как recommendation runtime adapter. Механический slice принятого
контракта обычно использует LOW/MEDIUM; архитектурная развилка, conflicting SPEC/ADR, сложная
schema/parser/concurrency/security/payment semantics — HIGH. FRONTIER требует фактической
эскалации capability, а не размера prompt.

Metadata не меняет выбранную пользователем модель главного агента. Существенная смена capability
предпочитает checkpoint + durable low-context handoff + новую session; один длинный active slice
не переключает model молча.

## Проверки

Более лёгкая модель и меньший reasoning не отменяют SPEC, Definition of Done,
unit/integration/component tests, review, security rules и Git workflow.

Если автоматический выбор недоступен, сообщи рекомендуемую конфигурацию, но не
утверждай, что фактическая модель была переключена.
