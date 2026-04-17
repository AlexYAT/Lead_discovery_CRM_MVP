## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-010
- Status: accepted
- Date: 2026-04-17
- Parent: DOA-OP-003
- Tags: [lead-discovery, crm, mvp, imp, operational-robustness, sqlite-audit, t01]

# Summary
Документ фиксирует выполнение T01 (`SQLite access audit`) из `DOA-OP-003`: проведён аудит SQLite access path
и выделены runtime touchpoints/lock-risk зоны для этапов T02-T04 без изменения продуктовой логики.

# Что выполнено в рамках T01
- выполнен полный аудит модулей, работающих с SQLite;
- выделены read path и write path;
- зафиксирована текущая модель lifecycle соединений;
- определены потенциальные lock-risk зоны и точки contention;
- сформирован список runtime touchpoints для внедрения WAL, busy handling, retry и explicit transactions
  на этапах T02-T04.

# Какие модули и точки доступа к SQLite выявлены
- `app/db/database.py`:
  - `get_connection()`
  - `init_db()`
- `app/services/lead_service.py`:
  - read: `list_leads`, `get_lead`
  - write: `create_lead`, `update_lead_status`, `update_lead_notes`
- `app/services/contact_service.py`:
  - read: `list_contact_attempts_by_lead`
  - write: `create_contact_attempt`
- `app/services/consultation_service.py`:
  - read: `list_consultations_by_lead`, `get_consultation`
  - write: `create_consultation`, `update_consultation_status_result`
- `app/services/dashboard_service.py`:
  - read: `get_lead_dashboard_metrics`
- `app/main.py`:
  - startup touchpoint: `startup_init_db()`

# Какие lock-risk зоны обнаружены
- конкурентные write-операции в сервисах lead/contact/consultation;
- startup-инициализация schema при параллельном старте инстансов;
- read-after-write contention при одновременной нагрузке;
- отсутствие явной busy policy (`busy_timeout`/write-retry) в текущей реализации;
- неявные transaction boundaries (implicit behavior контекстного менеджера).

# Какие runtime touchpoints выделены для T02–T04
- **T02 (WAL + lifecycle):**
  - `app/db/database.py::get_connection()`
  - `app/main.py::startup_init_db()`
- **T03 (busy_timeout + write-retry):**
  - централизованно в `app/db/database.py`
  - write functions в `lead_service.py`, `contact_service.py`, `consultation_service.py`
- **T04 (explicit short transactions):**
  - все write functions в перечисленных service modules с фокусом на короткие и прозрачные boundaries.

# Что сознательно НЕ делалось
- не внедрялся WAL;
- не внедрялись busy_timeout/write-retry;
- не менялась бизнес-логика и продуктовый flow;
- не вносились изменения UI/UX;
- не выполнялся переход на PostgreSQL или иные архитектурные расширения.

# Какая проверка выполнена
- подтверждено покрытие всех модулей с SQLite-доступом;
- отдельно выделены read path и write path;
- отдельно зафиксированы потенциальные lock-risk зоны;
- аудит явно соотнесён с T01 из `DOA-OP-003`.

# Как это соотносится с `DOA-OP-003`
Результат полностью закрывает T01:
- сформирован перечень runtime touchpoints;
- выделены зоны риска блокировок;
- подготовлена техническая база для выполнения T02-T04.

# Next Steps
- переход к T02 (`WAL mode and connection lifecycle hardening`).
