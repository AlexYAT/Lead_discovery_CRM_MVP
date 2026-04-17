## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-006
- Status: accepted
- Date: 2026-04-17
- Parent: DOA-OP-001
- Tags: [lead-discovery, crm, mvp, imp, t06, dashboard]

# Summary
Документ фиксирует результат выполнения T06 (`Dashboard`) из `DOA-OP-001`: реализован минимальный
SSR-dashboard для контроля воронки с агрегированными метриками по лидам.

# Что реализовано в T06
- добавлен service-слой dashboard с SQL-агрегацией `COUNT + GROUP BY status`;
- добавлен web-route `GET /dashboard`;
- добавлен SSR-шаблон dashboard с простым табличным отображением;
- в dashboard выводятся:
  - общее количество лидов;
  - количество лидов по статусам из MVP-модели.

# Какие файлы созданы/изменены
Созданы:
- `app/services/dashboard_service.py`
- `app/web/routes/dashboard.py`
- `app/templates/dashboard.html`

Изменены:
- `app/services/__init__.py`
- `app/web/__init__.py`
- `app/main.py`
- `app/templates/index.html`

# Как работает dashboard
- Route `GET /dashboard` вызывает `get_lead_dashboard_metrics()`.
- Сервис выполняет:
  - `SELECT COUNT(*) FROM leads` для общего количества;
  - `SELECT status, COUNT(*) FROM leads GROUP BY status` для статусных агрегатов.
- Результат передается в `dashboard.html`, где метрики выводятся в простом SSR-виде (таблица).

# Какие метрики считаются
- `total_leads` — общее количество лидов в таблице `leads`.
- `status_counts` — распределение по статусам:
  - `new`
  - `reviewed`
  - `contacted`
  - `replied`
  - `consultation_booked`
  - `converted`
  - `not_interested`

Для отсутствующих в базе статусов отображается `0`.

# Что НЕ делалось
- не добавлялись графические библиотеки и сложные визуализации;
- не добавлялись фильтры/срезы аналитики;
- не изменялась бизнес-логика Lead/Contact/Consultation;
- не выходили за границы MVP.

# Какая проверка выполнена
- синтаксическая проверка Python-файлов (`py_compile`);
- проверка доступности route `/dashboard`;
- проверка агрегатов на наборе тестовых лидов с разными статусами;
- сверка метрик dashboard с прямыми SQL-запросами к SQLite.

# Соответствие OP
Реализация соответствует T06 в `DOA-OP-001`:
- добавлен минимальный dashboard MVP;
- отображаются ключевые агрегированные метрики воронки;
- соблюдены ограничения по простоте и SSR-подходу.

# Next Steps
- закрыть выполнение `DOA-OP-001`;
- сформировать финальный implementation snapshot по завершению OP-этапа.
