## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-015
- Status: accepted
- Date: 2026-04-18
- Parent: [DOA-OP-004](../operational_plan/DOA-OP-004.md)
- Tags: [lead-discovery, crm, mvp, imp, operational-acceptance, op-004, multi-instance, sqlite, baseline]

# Summary

Финальный implementation snapshot по завершении цикла **Operational acceptance — multi-instance SQLite verification** ([DOA-OP-004](../operational_plan/DOA-OP-004.md)): зафиксировано приёмочное состояние MVP с двумя независимыми инстансами приложения на **одной** БД SQLite и результат валидации [DOA-VAL-003](../validation_reports/DOA-VAL-003.md). Документ задаёт **новый baseline** после OP-004; изменений коду продукта в рамках цикла не вносилось.

# Scope

- Закрытие **DOA-OP-004** (операционная приёмка двух инстансов).
- **Multi-instance SQLite acceptance** для MVP: согласованность данных и отсутствие необработанных lock-failures в объёме выполненного прогона.

# Артефакты

| Артефакт | Роль |
|----------|------|
| [DOA-OP-004](../operational_plan/DOA-OP-004.md) | Operational plan цикла |
| [DOA-RUN-001](../runbooks/DOA-RUN-001.md) | Runbook T01 |
| [DOA-EXEC-001](../execution_logs/DOA-EXEC-001.md) | Execution log T02 |
| [DOA-VAL-003](../validation_reports/DOA-VAL-003.md) | Validation report T03, verdict |
| [DOA-IMP-014](./DOA-IMP-014.md) | Предыдущий baseline: закрытие OP-003 (SQLite concurrency hardening) |

# Итоговое состояние системы

На момент baseline **DOA-IMP-015** (код без изменений в OP-004; поведение унаследовано от OP-003):

1. **WAL** — включён централизованно при открытии соединения.
2. **Short-lived connections** — модель `get_connection()` на операцию с commit/rollback и закрытием.
3. **Централизованный `busy_timeout`** — в `_configure_connection()`.
4. **Write-only retry** — `run_write_with_retry()` на целевом write path сервисов.
5. **Explicit short transactions** — `with connection:` на write-функциях lead/contact/consultation ([DOA-IMP-013](./DOA-IMP-013.md)).
6. **Два инстанса** — подтверждена работоспособность сценария чередования операций между `127.0.0.1:8000` и `127.0.0.1:8001` с **одним** `DB_PATH` ([DOA-EXEC-001](../execution_logs/DOA-EXEC-001.md), [DOA-VAL-003](../validation_reports/DOA-VAL-003.md)).

# Validation outcome

- **Verdict ([DOA-VAL-003](../validation_reports/DOA-VAL-003.md)):** **passed with limitations**.
- **Ключевой вывод:** для MVP в нормальном **multi-instance** usage (два процесса, один файл БД, сценарий приёмки) SQLite-стек приложения ведёт себя **устойчиво**: операции завершились успешно, данные согласованы, необработанные `database is locked` / `database table is locked` в наблюдаемом прогоне **не зафиксированы**. Оговорки относятся к полноте доказательств и методу исполнения, а не к отказу продукта (см. VAL-003).

# Known limitations

- Нет **stress/load** доказательства для большего числа параллельных писателей или длительной нагрузки.
- **Логи uvicorn** в файл в прогоне не собирались — оценка lock-поведения опиралась на HTTP-ответы и консистентность БД.
- Исполнение приёмки — **HTTP-эквивалент** SSR-форм, не ручной UI-браузер ([DOA-RUN-001](../runbooks/DOA-RUN-001.md) vs [DOA-EXEC-001](../execution_logs/DOA-EXEC-001.md)).
- **Harness** на шаге 6 (извлечение `CONSULTATION_ID` из HTML): ограничение вспомогательного скрипта; идентификатор подтверждён через SQLite; **не** дефект продукта ([DOA-EXEC-001](../execution_logs/DOA-EXEC-001.md)).

# Final conclusion

- **DOA-OP-004** считается **завершённым** по артефактам RUN / EXEC / VAL и настоящему snapshot.
- **Стратегия SQLite** (WAL, lifecycle, busy handling, write retry, короткие транзакции + подтверждённый двухинстансный сценарий) **принята для MVP** в заявленных ограничениях.
- Система готова к **следующему этапу развития** (новый lifecycle по отдельной IDEA/DEC/OP цепочке вне данного документа).
