## Metadata
- Project: DOA
- Doc type: decision_log
- ID: DOA-DEC-001
- Status: accepted
- Date: 2026-04-17
- Parent: DOA-ARCH-001
- Tags: [lead-discovery, crm, mvp, dec, architecture-decisions]

# Summary
Документ фиксирует подтвержденные ключевые архитектурные решения MVP перед переходом к этапу OP.

# Context
Решения приняты на основании:
- `DOA-ARCH-001`;
- source input `Lead Discovery CRM — MVP Project Schema`;
- подтвержденного decision checkpoint.

# Decision 1 - Status Transition Model
## Варианты
- свободные переходы между статусами;
- FSM с фиксированными допустимыми переходами.

## Принятое решение
Использовать FSM.

## Обоснование
- соответствует status flow из schema;
- делает воронку контролируемой;
- упрощает расчет conversion metrics;
- снижает риск неконсистентных состояний.

# Decision 2 - Consultation Model
## Варианты
- хранить консультацию внутри Lead;
- выделить отдельную сущность Consultation.

## Принятое решение
Использовать отдельную сущность Consultation.

## Обоснование
- соответствует schema;
- сохраняет независимый lifecycle консультации;
- упрощает развитие модели в следующих релизах.

# Decision 3 - Storage Strategy
## Варианты
- SQLite;
- PostgreSQL.

## Принятое решение
Использовать SQLite.

## Обоснование
- минимальная сложность MVP;
- быстрое локальное развёртывание;
- достаточно для single-user режима MVP.

# Decision 4 - Backend Architecture
## Варианты
- простой route-centric монолит;
- layered architecture.

## Принятое решение
Использовать layered architecture поверх FastAPI.

## Обоснование
- лучшее разделение ответственности;
- чище развитие MVP;
- снижает риск смешивания UI/API/data logic.

# Consequences
- MVP остается простым и быстрым в запуске;
- архитектура ограничена по масштабируемости;
- статусная модель становится строгой и наблюдаемой;
- консультации получают самостоятельный контур данных;
- backend остается пригодным для дальнейшего расширения.

# Constraints
- single-user;
- без AI-слоя;
- без сложных интеграций;
- без автоматических коммуникаций;
- без смены storage на этапе MVP.

# Next Steps
- переход к `OP`;
- декомпозиция реализации на операционные задачи.
