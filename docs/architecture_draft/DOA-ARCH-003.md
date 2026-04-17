## Metadata
- Project: DOA
- Doc type: architecture_draft
- ID: DOA-ARCH-003
- Status: draft
- Date: 2026-04-17
- Parent: DOA-IDEA-003
- Tags: [lead-discovery, crm, mvp, operational-robustness, sqlite-concurrency, architecture]

# Summary
Документ описывает архитектурную стратегию concurrent-safe runtime для SQLite в рамках single-user
multi-instance usage.

# Context
- MVP уже реализован на FastAPI + SQLite.
- Следующий цикл направлен не на multi-user feature, а на эксплуатационную устойчивость.
- Риск: concurrent access из 2+ инстансов может приводить к lock/error scenarios.

# Architectural Goal
- обеспечить устойчивое чтение/запись при 2+ инстансах;
- не менять базовую архитектуру продукта;
- остаться в рамках SQLite и минимальных архитектурных изменений.

# Scope
## Входит
- SQLite journal/concurrency strategy;
- connection lifecycle;
- transaction boundaries;
- busy handling / retry strategy;
- правила write path.

## Не входит
- полноценная multi-user архитектура;
- переход на PostgreSQL;
- distributed locking;
- user auth / roles.

# Core Architectural Decisions
## 1. SQLite journal mode
- рассмотреть WAL как базовый режим;
- WAL предпочтителен для multi-instance, так как лучше разделяет чтение и запись, снижая блокировки
  чтения при активных write-операциях.

## 2. Connection lifecycle
- зафиксировать подход с короткоживущими connections per operation/request;
- shared long-lived connection нежелателен, потому что повышает риск долгого удержания lock и усложняет
  предсказуемость поведения при конкурентном доступе.

## 3. Busy handling
- описать использование `busy_timeout`;
- описать ограниченный retry на write как runtime hardening при временных lock-состояниях.

## 4. Transaction model
- описать явные короткие транзакции;
- минимизировать время удержания lock.

## 5. Write path safety
- write-операции должны быть краткими, атомарными и воспроизводимыми;
- длинные write sequences нежелательны, так как увеличивают вероятность contention между инстансами.

# Runtime Flow
- instance открывает connection;
- применяет необходимые pragmas / timeout behavior;
- выполняет короткую read/write операцию;
- закрывает connection или переиспользует только в безопасной границе операции;
- предсказуемо обрабатывает временное busy-состояние.

# Risks
- SQLite всё равно не превращается в полноценную multi-user DB;
- write contention остаётся возможным;
- retry logic может скрывать часть проблем, если применять слишком широко;
- тестирование concurrent scenarios сложнее обычного MVP.

# Validation Strategy
- запуск из 2 инстансов;
- конкурентные CRUD-сценарии;
- отсутствие `database is locked` в нормальном usage;
- отсутствие потери записей.

# Next Steps
Следующий этап: `DEC`.

В DEC нужно зафиксировать конкретные точки выбора:
1. WAL vs alternative;
2. connection lifecycle model;
3. busy_timeout / retry policy;
4. transaction strategy;
5. scope of robustness implementation.
