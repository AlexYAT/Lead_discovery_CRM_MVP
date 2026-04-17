## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-011
- Status: accepted
- Date: 2026-04-18
- Parent: DOA-OP-003
- Tags: [lead-discovery, crm, mvp, imp, operational-robustness, t02, wal, connection-lifecycle]

# Summary
Документ фиксирует выполнение T02 из `DOA-OP-003`: внедрён WAL mode и формализован безопасный
short-lived connection lifecycle для SQLite runtime без изменения продуктовой логики.

# Что выполнено в рамках T02
- обновлён `app/db/database.py` для safe-конфигурации соединений per operation/request;
- добавлена централизованная конфигурация SQLite connection через `_configure_connection(...)`;
- обеспечено воспроизводимое включение `journal_mode=WAL`;
- формализована модель короткоживущего соединения через context manager с гарантированным закрытием;
- усилен startup touchpoint через безопасное условное schema-bootstrap поведение.

# Какие файлы созданы/изменены
Изменены:
- `app/db/database.py`

Новые файлы в рамках T02 не создавались.

# Как включён WAL mode
- при каждом открытии соединения применяется `PRAGMA journal_mode = WAL`;
- применение вынесено в централизованный `_configure_connection(connection)`;
- фактическая проверка `PRAGMA journal_mode;` вернула `wal`.

# Как теперь устроен connection lifecycle
- `get_connection()` переведён в контекстный менеджер;
- каждое соединение открывается под одну операцию/запрос;
- после успешной операции выполняется `commit`, при исключении `rollback`;
- в `finally` соединение закрывается явно (`connection.close()`), что исключает неявно висящие connections;
- shared long-lived connection не используется.

# Что было сделано для startup hardening
- `init_db()` сначала проверяет наличие ключевой таблицы (`leads`) через `sqlite_master`;
- если схема уже существует, bootstrap не выполняется повторно;
- это снижает write-давление при параллельном старте инстансов и уменьшает lock-risk на startup.

# Что сознательно НЕ делалось
- не внедрялся write-retry (это T03);
- не внедрялись явные короткие транзакции в write path сервисов (это T04);
- не менялись UI/UX и продуктовые сценарии;
- не добавлялись новые функции или архитектурные расширения beyond T02.

# Какая проверка выполнена
- синтаксическая проверка Python-файлов (`py_compile`);
- проверка фактического `journal_mode` (`wal`);
- проверка запуска приложения через uvicorn;
- проверка доступности страниц:
  - `/`
  - `/leads`
  - `/dashboard`
  (HTTP 200).

# Как это соотносится с `DOA-OP-003`
Результат закрывает T02:
- WAL mode внедрён;
- lifecycle соединений формализован в short-lived model;
- startup path подготовлен к более безопасному multi-instance поведению;
- база готова к следующему этапу T03 (busy handling + write retry).

# Next Steps
- переход к T03 (`Busy handling and write retry`).
