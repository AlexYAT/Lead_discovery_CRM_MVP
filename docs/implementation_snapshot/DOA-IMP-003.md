## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-003
- Status: accepted
- Date: 2026-04-17
- Parent: DOA-OP-001
- Tags: [lead-discovery, crm, mvp, imp, t03, lead-crm]

# Summary
Документ фиксирует результат выполнения T03 (`Lead CRM`) из `DOA-OP-001`: реализован минимальный
рабочий контур Lead CRM с SSR-интерфейсом и FSM-валидацией переходов статуса.

# Что выполнено в рамках T03
- добавлен простой service/data слой для работы с сущностью Lead в SQLite;
- реализованы SSR-страницы:
  - список лидов с формой создания;
  - карточка лида;
- реализованы действия:
  - создание лида;
  - просмотр списка;
  - просмотр карточки;
  - обновление статуса;
  - сохранение заметок;
- реализована проверка допустимых переходов статуса через FSM-модель;
- обновлена стартовая страница с переходом в Lead CRM.

# Какие файлы созданы/изменены
Созданы:
- `.gitignore`
- `app/services/__init__.py`
- `app/services/lead_service.py`
- `app/web/__init__.py`
- `app/web/routes/__init__.py`
- `app/web/routes/leads.py`
- `app/templates/leads_list.html`
- `app/templates/lead_detail.html`

Изменены:
- `app/main.py`
- `app/templates/index.html`

Удалены runtime-артефакты из репозитория:
- `app/__pycache__/main.cpython-312.pyc`
- `app/api/routes/__pycache__/base.cpython-312.pyc`
- `app/db/__pycache__/__init__.cpython-312.pyc`
- `app/db/__pycache__/database.cpython-312.pyc`

# Какие функции Lead CRM реализованы
- ручное создание Lead с обязательными полями (`platform`, `profile_name`, `profile_url`);
- отображение списка Lead;
- открытие карточки Lead по `id`;
- обновление `status` только по допустимым переходам;
- сохранение и обновление `notes` в карточке Lead.

# Как реализована FSM-проверка статусов
FSM реализована в `app/services/lead_service.py` через:
- список допустимых статусов `LEAD_STATUSES`;
- словарь переходов `ALLOWED_STATUS_TRANSITIONS`;
- проверку в `update_lead_status(...)`:
  - запрещены неизвестные статусы;
  - запрещены переходы вне `ALLOWED_STATUS_TRANSITIONS`;
  - допустим only no-op для того же статуса.

Используемая модель переходов:
- `new -> reviewed | not_interested`
- `reviewed -> contacted | not_interested`
- `contacted -> replied | not_interested`
- `replied -> consultation_booked | not_interested`
- `consultation_booked -> converted | not_interested`
- `converted` и `not_interested` терминальные.

# Что сознательно НЕ делалось
- не реализован Contact Log UI/CRUD (T04);
- не реализован Consultation UI/CRUD (T05);
- не реализован Dashboard (T06);
- не добавлены AI-компоненты, внешние интеграции и сложные абстракции.

# Какая проверка выполнена
- проверен импорт/запуск приложения на уровне FastAPI app;
- выполнена синтаксическая проверка Python-файлов (`py_compile`);
- выполнены ручные сценарии через FastAPI TestClient:
  - создание лида;
  - отображение лида в списке;
  - открытие карточки;
  - обновление статуса по допустимому переходу;
  - сохранение заметки;
- дополнительно подтверждено блокирование недопустимого перехода FSM.

# Соответствие `DOA-OP-001`
Результат полностью соответствует T03:
- реализован минимальный рабочий контур Lead CRM;
- соблюдены границы этапа без выхода в T04-T06;
- подготовлена кодовая база для следующего этапа OP.

# Next Steps
- перейти к T04 (`Contact Log`) в рамках `DOA-OP-001`.
