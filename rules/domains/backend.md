# Backend

- Не помещай бизнес-логику в HTTP handlers или transport-слой.
- Валидируй входные данные на границе системы.
- Используй стабильные контракты ошибок.
- Учитывай timeouts, retries, идемпотентность и отмену операций.
- Не раскрывай stack trace и внутренние данные клиенту.
- Отделяй доменную логику от инфраструктурных адаптеров.
- Для bootstrap, command/config/service/API/DB/test workflow и local/CI parity
  применяй `rules/backend-dx.md`; domain rule не дублирует полный DX contract.
