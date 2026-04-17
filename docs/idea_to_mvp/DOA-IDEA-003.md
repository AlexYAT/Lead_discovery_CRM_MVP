## Metadata
- Project: DOA
- Doc type: idea_to_mvp
- ID: DOA-IDEA-003
- Status: draft
- Date: 2026-04-17
- Parent: DOA-VAL-001
- Tags: [lead-discovery, crm, mvp, operational-robustness, sqlite-concurrency]

# Summary
Добавление устойчивости runtime при одновременном доступе к SQLite из нескольких инстансов приложения.

# Context
- MVP построен на FastAPI + SQLite.
- система рассчитана на одного пользователя.
- возможен запуск из нескольких мест (локально, разные окна, разные машины).
- SQLite может давать блокировки при concurrent access.

# Problem
При одновременной работе нескольких инстансов возможны:
- `database is locked`;
- потеря операций записи;
- нестабильность системы.

# Goal
Обеспечить:
- стабильную работу при 2+ инстансах;
- отсутствие критических блокировок SQLite;
- предсказуемое поведение записи/чтения.

# Scope
## Включено
- настройка SQLite для concurrent access;
- управление транзакциями;
- безопасный write pattern;
- базовая защита от блокировок.

## Не входит
- полноценная multi-user система;
- авторизация;
- распределённая архитектура;
- переход на PostgreSQL.

# Constraints
- сохраняется SQLite;
- минимальные изменения архитектуры;
- не ломать текущий MVP.

# Definition of Done
- система стабильно работает при 2 параллельных инстансах;
- отсутствуют ошибки `database is locked` в нормальном usage;
- записи не теряются;
- CRUD операции выполняются корректно.

# Risks
- ограничения SQLite;
- race conditions;
- сложность тестирования concurrent сценариев.

# Next Step
-> переход к ARCH (выбор стратегии работы с SQLite concurrency).
