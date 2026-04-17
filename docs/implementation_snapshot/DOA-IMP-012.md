## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-012
- Status: accepted
- Date: 2026-04-18
- Parent: DOA-OP-003
- Tags: [lead-discovery, crm, mvp, imp, operational-robustness, t03, busy-timeout, write-retry]

# Summary
Документ фиксирует выполнение T03 из `DOA-OP-003`: добавлены централизованный `busy_timeout` и
ограниченный write-only retry для повышения устойчивости SQLite write path при кратковременных lock collisions.

# Что выполнено в рамках T03
- в `app/db/database.py` централизованно добавлен `PRAGMA busy_timeout`;
- добавлен простой helper `run_write_with_retry(...)` для ограниченного retry;
- retry применяется только для transient SQLite busy/locked ошибок;
- write functions в сервисах переведены на retry policy;
- read path сохранён без retry.

# Какие файлы созданы/изменены
Изменены:
- `app/db/database.py`
- `app/db/__init__.py`
- `app/services/lead_service.py`
- `app/services/contact_service.py`
- `app/services/consultation_service.py`

Новые файлы в рамках T03 не создавались.

# Где и как установлен `busy_timeout`
- в `app/db/database.py` внутри `_configure_connection(connection)`:
  - `PRAGMA busy_timeout = <значение>`;
- применяется централизованно при каждом открытии соединения через `get_connection()`.

# Как устроен write-only retry
- реализован helper `run_write_with_retry(operation)` в `app/db/database.py`;
- retry ограничен по количеству попыток (`WRITE_RETRY_MAX_ATTEMPTS`);
- используется простой возрастающий backoff (`WRITE_RETRY_BACKOFF_SEC * attempt`);
- retry срабатывает только для transient `sqlite3.OperationalError` с busy/locked-сигнатурой;
- для других ошибок поведение fail-fast (исключение пробрасывается без retry).

# Какие write functions переведены на retry policy
- `app/services/lead_service.py`:
  - `create_lead`
  - `update_lead_status`
  - `update_lead_notes`
- `app/services/contact_service.py`:
  - `create_contact_attempt`
- `app/services/consultation_service.py`:
  - `create_consultation`
  - `update_consultation_status_result`

# Почему read path остался без retry
- по DEC/OP retry должен применяться только к write path;
- read path не модифицирован для сохранения предсказуемости чтения и минимальной сложности;
- это снижает риск скрытия проблем чтения и исключает лишнее усложнение runtime.

# Что сознательно НЕ делалось
- не внедрялись явные короткие транзакции beyond текущий уровень (это T04);
- не менялись UI/UX и продуктовая функциональность;
- не добавлялись новые фичи;
- не выполнялся переход на PostgreSQL.

# Какая проверка выполнена
- синтаксическая проверка Python-файлов (`py_compile`);
- запуск приложения через uvicorn;
- проверка доступности `/`, `/leads`, `/dashboard` (HTTP 200);
- проверка write path:
  - создание lead;
  - обновление status/notes;
  - contact log create;
  - consultation create/update;
  - подтверждение сохранения данных в SQLite.

# Как это соотносится с `DOA-OP-003`
Результат закрывает T03:
- busy handling внедрён централизованно;
- write path hardened через ограниченный retry;
- read path сохранён без retry согласно scope этапа.

# Next Steps
- переход к T04 (`Explicit short transactions`).
