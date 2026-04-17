## Metadata
- Project: DOA
- Doc type: audit_check
- ID: DOA-AUD-001
- Status: draft
- Date: 2026-04-17
- Parent: DOA-OP-003
- Tags: [lead-discovery, crm, mvp, sqlite, access-audit, t01]

# Summary
Проведён T01 audit текущего SQLite access path для цикла Operational robustness.
Зафиксированы runtime touchpoints, read/write path, transaction boundaries и lock-risk зоны без изменения
продуктовой логики.

# Scope of Audit
- in-scope: модули, которые открывают SQLite connection и выполняют SQL-операции;
- out-of-scope: внедрение WAL/busy_timeout/retry/транзакционных изменений (будет на T02-T04).

# Обнаруженные модули работы с SQLite
## Core DB module
- `app/db/database.py`
  - `get_connection()`: открывает `sqlite3.connect(DB_PATH)`, включает `PRAGMA foreign_keys = ON`.
  - `init_db()`: выполняет `executescript(schema_sql)` на startup.

## Service modules (runtime SQL touchpoints)
- `app/services/lead_service.py`
  - write: `create_lead`, `update_lead_status`, `update_lead_notes`;
  - read: `list_leads`, `get_lead`.
- `app/services/contact_service.py`
  - write: `create_contact_attempt`;
  - read: `list_contact_attempts_by_lead`.
- `app/services/consultation_service.py`
  - write: `create_consultation`, `update_consultation_status_result`;
  - read: `list_consultations_by_lead`, `get_consultation`.
- `app/services/dashboard_service.py`
  - read: `get_lead_dashboard_metrics` (агрегирующие запросы).

## App lifecycle touchpoint
- `app/main.py`
  - `startup_init_db()`: вызывает `init_db()` при старте приложения.

# Текущая модель lifecycle соединений
- фактическая модель: `with get_connection() as connection` per service operation;
- соединения короткоживущие на уровне функции сервиса;
- явный pool/shared long-lived connection не используется.

# Read Path (текущий)
- read-операции выполняются отдельными короткими запросами в `list_*` / `get_*` функциях;
- `row_factory = Row` ставится локально перед read-запросами;
- отдельной read-specific политики busy handling нет.

# Write Path (текущий)
- write-операции выполняются одиночными `INSERT/UPDATE` в пределах одного `with connection`;
- commit/rollback boundaries не задаются явно на уровне SQL (`BEGIN/COMMIT` не используются);
- используется implicit transaction behavior sqlite3 context manager.

# Transaction / Commit Boundaries (текущие)
- транзакционные границы не выражены явно в коде;
- атомарность опирается на контекст `with get_connection()` и одиночные SQL-команды;
- длинных явных multi-statement write-транзакций не выявлено.

# Потенциальные lock-risk зоны
- Одновременные write-запросы из разных инстансов в:
  - `create_lead`
  - `update_lead_status`
  - `update_lead_notes`
  - `create_contact_attempt`
  - `create_consultation`
  - `update_consultation_status_result`
- Startup touchpoint:
  - параллельный запуск двух инстансов может одновременно вызвать `init_db().executescript(...)`.
- Read-after-write contention:
  - dashboard/read-запросы во время write-нагрузки могут сталкиваться с временными lock-state.
- Отсутствие явной busy policy:
  - нет `busy_timeout`, нет ограниченного write-retry, поэтому transient collision может приводить к
    `database is locked`.

# Runtime touchpoints для T02–T04
## T02 (WAL + connection lifecycle)
- `app/db/database.py::get_connection()`
  - добавить PRAGMA-инициализацию concurrency policy (WAL-related pragmas);
  - формализовать безопасную конфигурацию per-operation connection.
- `app/main.py::startup_init_db()`
  - учесть безопасный startup behavior при multi-instance старте.

## T03 (busy handling + write retry)
- `app/db/database.py`
  - централизовать `busy_timeout`;
  - добавить базовый helper/policy для ограниченного retry только на writes.
- write functions в service modules:
  - `lead_service.py` (3 write functions)
  - `contact_service.py` (1 write function)
  - `consultation_service.py` (2 write functions)

## T04 (explicit short transactions)
- все write functions в сервисах:
  - явно обозначить короткие transaction boundaries;
  - сохранить краткость и атомарность write операций;
  - не затрагивать read path и продуктовую логику.

# Gaps readiness относительно concurrency hardening
- WAL mode пока не внедрён;
- busy_timeout не установлен;
- ограниченный retry для writes отсутствует;
- явные транзакционные границы для write path не формализованы.

# Связь с `DOA-OP-003` (T01)
T01 выполнен:
- access path проанализирован;
- runtime touchpoints зафиксированы;
- lock-risk зоны выделены;
- сформирован список технических точек для T02-T04 без изменения продуктовой логики.
