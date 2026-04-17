## Metadata
- Project: DOA
- Doc type: operational_plan
- ID: DOA-OP-003
- Status: accepted
- Date: 2026-04-17
- Parent: DOA-DEC-003
- Tags: [lead-discovery, crm, mvp, operational-robustness, sqlite-concurrency, hardening]

# Summary
Документ задаёт операционный план реализации SQLite concurrency hardening для single-user multi-instance usage.

# Goal
- повысить устойчивость runtime при 2+ инстансах;
- внедрить принятые решения по SQLite concurrency;
- подтвердить отсутствие `database is locked` в нормальном usage;
- сохранить текущую продуктовую функциональность без расширения scope.

# Scope of Execution
## Включить в план
- анализ текущего SQLite access path;
- внедрение WAL mode;
- пересмотр lifecycle соединений;
- настройку busy_timeout;
- ограниченный retry для write-операций;
- явные короткие транзакции;
- проверку concurrent CRUD сценариев из 2 инстансов;
- финальную фиксацию implementation snapshot.

## Не включать
- переход на PostgreSQL;
- multi-user auth/roles;
- distributed locking;
- новые продуктовые функции;
- UI/UX изменения.

# Execution Strategy
Реализация выполняется в этапах T01-T06 с фокусом на runtime hardening без изменения продуктовой логики.

## T01 — SQLite access audit
- проанализировать текущий способ открытия соединений и write path;
- найти места, где возможны долгие lock windows;
- определить минимальные точки hardening без смены продуктовой логики.

Deliverable:
- зафиксированный список runtime touchpoints для SQLite hardening.

## T02 — WAL mode and connection lifecycle hardening
- внедрить WAL mode;
- внедрить short-lived connection per operation/request;
- зафиксировать безопасный способ открытия/закрытия соединений.

Deliverable:
- runtime работает с WAL и новым connection lifecycle.

## T03 — Busy handling and write retry
- внедрить busy_timeout;
- добавить ограниченный retry только для write-операций;
- избежать влияния retry на read path.

Deliverable:
- write path устойчив к кратковременным lock collisions.

## T04 — Explicit short transactions
- сделать write-операции короткими и явными;
- минимизировать время удержания lock;
- зафиксировать транзакционные границы в коде.

Deliverable:
- write операции имеют прозрачные короткие transaction boundaries.

## T05 — Concurrent validation from two instances
- подготовить и выполнить проверку concurrent usage из 2 инстансов;
- проверить базовые CRUD сценарии без потери записей;
- проверить отсутствие `database is locked` в normal usage;
- зафиксировать наблюдаемые результаты.

Deliverable:
- подтверждение runtime robustness или честно зафиксированные остаточные ограничения.

## T06 — Implementation snapshot
- создать новый implementation_snapshot по итогам выполнения OP;
- зафиксировать, какие технические изменения внесены;
- зафиксировать результаты concurrent validation;
- обозначить остаточные ограничения SQLite, если они остались.

Deliverable:
- итоговый IMP operational robustness cycle.

# Deliverables
- T01: список runtime touchpoints и lock-risk зон для SQLite access path.
- T02: внедрённый WAL и short-lived lifecycle соединений.
- T03: busy_timeout и write-only retry policy в runtime.
- T04: короткие явные transaction boundaries для write paths.
- T05: результаты concurrent validation из 2 инстансов.
- T06: итоговый implementation snapshot с технической фиксацией цикла.

# Definition of Done for execution
OP считается выполненным, если:
- WAL внедрён;
- lifecycle соединений приведён к short-lived model;
- busy_timeout и write retry реализованы;
- write path использует короткие явные транзакции;
- concurrent usage из 2 инстансов проверен;
- в нормальном usage не наблюдаются `database is locked`;
- implementation snapshot создан.

# Risks and Controls
- Риск: неполное покрытие write paths.  
  Контроль: аудит всех write touchpoints на T01 и обязательная проверка после T04.
- Риск: ложное чувство надёжности при узком наборе concurrent test cases.  
  Контроль: минимум два инстанса и повторяемые CRUD-сценарии с фиксацией результатов.
- Риск: скрытые lock windows в старом коде.  
  Контроль: ревизия transaction boundaries и устранение длинных write sequences.
- Риск: retry masking проблем при слишком агрессивной политике.  
  Контроль: ограниченный retry только для writes с прозрачной фиксацией поведения.
- Риск: ограничения SQLite как single-file DB.  
  Контроль: явная фиксация остаточных ограничений в IMP и отсутствие ложных multi-user обещаний.

# Next Steps
- выполнение задач только в рамках данного OP;
- после завершения перейти к следующему lifecycle с новыми operational или functional целями.
