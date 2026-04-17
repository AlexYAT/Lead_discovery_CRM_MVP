## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-013
- Status: accepted
- Date: 2026-04-18
- Parent: DOA-OP-003
- Tags: [lead-discovery, crm, mvp, imp, operational-robustness, t04, short-transactions, sqlite]

# Summary
Документ фиксирует выполнение T04 из `DOA-OP-003`: write path в сервисах переведён на явные короткие
транзакции с узкой областью удержания lock и подготовкой параметров до открытия транзакции, без изменения
продуктовой логики и публичных контрактов.

# Что выполнено в рамках T04
- для каждой write-функции в `lead_service`, `contact_service`, `consultation_service` граница транзакции
  задана явно через вложенный `with connection:` (стандартный контекстный менеджер `sqlite3.Connection`);
- подготовка значений для INSERT/UPDATE (нормализация строк, кортежи параметров) вынесена до входа в область
  write-транзакции;
- сохранены `get_connection()`, `run_write_with_retry()` и существующий short-lived connection lifecycle;
- read path в сервисах не менялся.

# Какие файлы изменены
- `app/services/lead_service.py`
- `app/services/contact_service.py`
- `app/services/consultation_service.py`
- `docs/implementation_snapshot/DOA-IMP-013.md` (настоящий снимок)

# Какие write functions переведены на explicit short transactions
- `app/services/lead_service.py`:
  - `create_lead`
  - `update_lead_status`
  - `update_lead_notes`
- `app/services/contact_service.py`:
  - `create_contact_attempt`
- `app/services/consultation_service.py`:
  - `create_consultation`
  - `update_consultation_status_result`

# Как теперь определены transaction boundaries
- внешний контекст `with get_connection() as connection:` — short-lived соединение, финальный `commit`/`rollback`
  и `close` по-прежнему централизованы в `app/db/database.py`;
- внутренний `with connection:` — **явная** короткая транзакция: BEGIN на входе, COMMIT/ROLLBACK на выходе;
- внутри внутреннего контекста выполняется только минимальный набор DML (`execute` для write);
- подготовительные вычисления и сборка кортежей параметров выполняются до вызова `_operation()` / до входа во
  внутренний `with connection:`.

# Подтверждение: продуктовая логика не менялась
- публичные сигнатуры и порядок бизнес-проверок (например, `get_lead` + правила перехода статуса у lead,
  валидация статуса consultation) не изменялись;
- в БД уходят те же значения полей, что и до рефакторинга (те же правила `strip`, `or None`, нормализация дат и
  статусов);
- UI/UX и HTTP API приложения не затрагивались.

# Сочетание с WAL, busy_timeout и retry
- WAL и `PRAGMA busy_timeout` по-прежнему применяются в `_configure_connection()` при каждом открытии
  соединения;
- write path остаётся обёрнутым в `run_write_with_retry()` без изменения семантики retry;
- сокращение области транзакции снижает время удержания write-lock при сохранении той же политики повторов
  при transient `database is locked` / `database table is locked`.

# Какая проверка выполнена вручную
- `python -m py_compile` для изменённых модулей сервисов;
- импорт `app.services.lead_service`, `contact_service`, `consultation_service`;
- сценарий: `init_db`, создание lead, обновление status/notes, создание contact attempt, создание и обновление
  consultation — без исключений;
- краткий запуск `uvicorn app.main:app` с проверкой успешного старта процесса.

# Как это соотносится с `DOA-OP-003`
Результат закрывает T04:
- write path использует явные короткие транзакции поверх уже внедрённого WAL, busy_timeout и write-only retry;
- lock window минимизирован на уровне сервисного write path без расширения scope за пределы SQLite hardening.

# Next Steps
- при необходимости последующие OP-задачи по наблюдаемости/нагрузочным сценариям вне текущего SQLite-hardening scope.
