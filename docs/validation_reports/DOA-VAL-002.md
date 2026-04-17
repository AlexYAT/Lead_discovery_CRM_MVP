# Validation Report: DOA-VAL-002

## Document Metadata

- **ID:** DOA-VAL-002
- **Doc type:** validation_report
- **Status:** accepted
- **Date:** 2026-04-18
- **Parent:** [DOA-OP-003](../operational_plan/DOA-OP-003.md) (Operational robustness — SQLite concurrency hardening)
- **Tags:** [lead-discovery, crm, mvp, val, sqlite-hardening, t05, op-003]

## Scope

Валидация завершённого технического цикла **T01–T04** в рамках `DOA-OP-003`: согласованность WAL, short-lived connections, централизованного `busy_timeout`, write-only retry и explicit short transactions в целевом write path сервисов, а также отсутствие нежелательных изменений read path и публичных контрактов API сервисов.

Исключения из scope (явно):

- нагрузочное / многопоточное доказательство отсутствия lock contention;
- изменение кода продукта или UI/UX.

## Артефакты, на которые опиралась валидация

| Артефакт | Роль |
|----------|------|
| [DOA-IMP-010](../implementation_snapshot/DOA-IMP-010.md) | T01 — аудит SQLite access path |
| [DOA-IMP-011](../implementation_snapshot/DOA-IMP-011.md) | T02 — WAL + short-lived connection lifecycle |
| [DOA-IMP-012](../implementation_snapshot/DOA-IMP-012.md) | T03 — `busy_timeout` + write-only retry |
| [DOA-IMP-013](../implementation_snapshot/DOA-IMP-013.md) | T04 — explicit short transactions в сервисах |
| `app/db/database.py` | Источник истины по pragma, `get_connection`, `run_write_with_retry` |
| `app/services/lead_service.py`, `contact_service.py`, `consultation_service.py` | Целевой write/read path CRM-сущностей |
| `app/services/dashboard_service.py` | Дополнительный read-only touchpoint к БД |

## Проверки и результаты

### V-01 — WAL включён и применяется при открытии соединения

- **Метод:** статический обзор `_configure_connection` в `app/db/database.py` (`PRAGMA journal_mode = WAL`); runtime — `PRAGMA journal_mode` через `get_connection()`.
- **Результат:** **pass** — в коде pragma задан; при выполнении `get_connection()` фактический режим `wal` (нижний регистр в ответе SQLite).

### V-02 — Short-lived connections

- **Метод:** обзор `get_connection()`: `yield` + `commit`/`rollback` + `finally: connection.close()`.
- **Результат:** **pass** — модель короткоживущего соединения на операцию сохранена, long-lived connection в коде не вводился.

### V-03 — `busy_timeout` централизован

- **Метод:** обзор `_configure_connection`; `PRAGMA busy_timeout` после открытия соединения; сравнение с константой `SQLITE_BUSY_TIMEOUT_MS`.
- **Результат:** **pass** — `PRAGMA busy_timeout` возвращает `5000`, совпадает с `SQLITE_BUSY_TIMEOUT_MS` в `database.py`.

### V-04 — Write-only retry: наличие, семантика, область применения

- **Метод:** обзор `run_write_with_retry` и `grep` по репозиторию на `run_write_with_retry`.
- **Результат:** **pass** — helper в `database.py`; используется только в `lead_service`, `contact_service`, `consultation_service` для write-операций. `dashboard_service` и read-функции сервисов retry не импортируют и не вызывают.

### V-05 — Explicit short transactions на всех целевых write-функциях

- **Метод:** статический обзор: наличие вложенного `with connection:` внутри `with get_connection()` для каждой write-функции, перечисленной в DOA-IMP-013.
- **Результат:** **pass** — `create_lead`, `update_lead_status`, `update_lead_notes`, `create_contact_attempt`, `create_consultation`, `update_consultation_status_result` содержат `with connection:` вокруг DML.

### V-06 — Read path без лишних transaction-hardening изменений

- **Метод:** сравнение read-функций (`list_*`, `get_*`) с ожиданием: `get_connection` без вложенного `with connection:` и без `run_write_with_retry`; проверка `dashboard_service`.
- **Результат:** **pass** — read path использует только `get_connection` для SELECT; явные короткие транзакции T04 на read не распространялись.

### V-07 — Публичный контракт API функций сервисов (сигнатуры)

- **Метод:** визуальная сверка объявлений публичных функций в трёх сервисах с ожидаемым набором параметров и возвращаемых типов из scope T01–T04 (без диффа к историческим коммитам — контракт подтверждён неизменностью исходников в текущей ветке).
- **Результат:** **pass** — изменений сигнатур в рамках валидации не выявлено.

### V-08 — Импорт / компиляция затронутых модулей

- **Метод:** `python -m py_compile` для `database.py`, `lead_service.py`, `contact_service.py`, `consultation_service.py`, `dashboard_service.py`.
- **Результат:** **pass**.

### V-09 — Старт приложения

- **Метод:** `from app.main import app`; краткий запуск `uvicorn app.main:app`, HTTP `GET /`.
- **Результат:** **pass** — приложение загружается; HTTP 200 на `/`.

### V-10 — Smoke write-сценарии (end-to-end через сервисы)

- **Метод:** после `init_db()`: `create_lead` → `get_lead` → `update_lead_status` → `update_lead_notes` → `create_contact_attempt` → `create_consultation` → `update_consultation_status_result` → `get_consultation`.
- **Результат:** **pass** — исключений нет, данные согласованы с ожиданиями (статус после обновлений).

### V-11 — Отсутствие ошибок SQLite locking на базовом сценарии

- **Метод:** наблюдение за выполнением V-10 и V-09 (одиночный процесс, последовательные вызовы).
- **Результат:** **pass (ограниченно)** — ошибок `database is locked` / `database table is locked` в этом прогоне не зафиксировано. Доказательство устойчивости под параллельной нагрузкой в scope не входит (см. Known limitations).

## Known limitations

- Не выполнялось стресс-тестирование параллельных писателей / нескольких процессов uvicorn; утверждения о retry и `busy_timeout` основаны на коде и на отсутствии lock-ошибок в **однопоточном** smoke.
- `init_db()` остаётся отдельным touchpoint с `get_connection` без паттерна T04 (`with connection:`) — вне целевого набора write-функций сервисов из IMP-013; поведение не менялось в рамках T04.

## Verdict

**Validation passed** — по результатам статического аудита и выполненных минимальных runtime-проверок цикл **T01–T04** для `DOA-OP-003` технически согласован: WAL, short-lived connections, централизованный `busy_timeout`, write-only retry и explicit short transactions на целевом write path работают в текущей кодовой базе без противоречий; read path и контракты сервисных функций в ожидаемых границах не нарушены.

**Ответ на вопрос scope:** после T04 цикл **OP-003** по SQLite hardening **можно считать технически валидированным** в объёме настоящего отчёта (с указанными limitations по нагрузочному охвату).

## Ссылки на implementation snapshots

- [DOA-IMP-010](../implementation_snapshot/DOA-IMP-010.md) — T01  
- [DOA-IMP-011](../implementation_snapshot/DOA-IMP-011.md) — T02  
- [DOA-IMP-012](../implementation_snapshot/DOA-IMP-012.md) — T03  
- [DOA-IMP-013](../implementation_snapshot/DOA-IMP-013.md) — T04  
