## Metadata
- Project: DOA
- Doc type: decision_log
- ID: DOA-DEC-003
- Status: accepted
- Date: 2026-04-17
- Parent: DOA-ARCH-003
- Tags: [lead-discovery, crm, mvp, operational-robustness, sqlite-concurrency, hardening]

# Summary
Документ фиксирует ключевые решения по обеспечению concurrent-safe runtime для SQLite без перехода к
multi-user архитектуре.

# Context
Решения приняты на основании:
- `DOA-IDEA-003`;
- `DOA-ARCH-003`;
- подтверждённого decision checkpoint;
- цели обеспечить устойчивую работу при 2+ инстансах без смены SQLite.

# Decision 1 — SQLite Journal Mode
## Варианты
- default / DELETE;
- WAL.

## Принятое решение
Использовать WAL.

## Обоснование
- лучше разделяет чтение и запись;
- снижает read/write blocking;
- подходит для multi-instance runtime в рамках SQLite.

# Decision 2 — Connection Lifecycle
## Варианты
- shared long-lived connection;
- short-lived connection per operation/request.

## Принятое решение
Short-lived connection per operation/request.

## Обоснование
- снижает риск длительного удержания lock;
- делает поведение соединений предсказуемее;
- лучше подходит для concurrent-safe runtime.

# Decision 3 — Busy Handling Policy
## Варианты
- только busy_timeout;
- busy_timeout + ограниченный retry only for writes.

## Принятое решение
Использовать busy_timeout + ограниченный retry только для write-операций.

## Обоснование
- повышает устойчивость при кратковременных write collisions;
- не усложняет read path;
- снижает вероятность `database is locked` в нормальном usage.

# Decision 4 — Transaction Strategy
## Варианты
- неявные транзакции;
- явные короткие транзакции.

## Принятое решение
Использовать явные короткие транзакции.

## Обоснование
- минимизирует время удержания lock;
- делает границы write-операций прозрачными;
- снижает contention между инстансами.

# Decision 5 — Scope of Robustness Implementation
## Варианты
- минимально: только WAL + timeout;
- цельно: WAL + connection lifecycle + busy handling + write safety.

## Принятое решение
Цельный runtime hardening scope.

## Обоснование
- закрывает не только journal mode, но и эксплуатационные риски connection/write path;
- остаётся в рамках MVP и SQLite;
- формирует целостную стратегию без перехода к PostgreSQL.

# Consequences
- SQLite сохраняется как storage MVP;
- система становится устойчивее для single-user multi-instance usage;
- полноценная multi-user семантика всё ещё не гарантируется;
- потребуется явная validation concurrent-сценариев на этапе OP/IMP;
- реализация должна избегать длинных write sequences.

# Constraints
- без перехода на PostgreSQL;
- без distributed locking;
- без multi-user auth/roles;
- без продуктового расширения beyond runtime robustness;
- только эксплуатационное hardening текущего MVP.

# Next Steps
- следующий этап: `OP`;
- декомпозиция реализации SQLite concurrency hardening;
- обязательная проверка сценариев запуска из 2 инстансов и concurrent CRUD без потери записей.
