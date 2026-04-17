## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-005
- Status: accepted
- Date: 2026-04-17
- Parent: DOA-OP-001
- Tags: [lead-discovery, crm, mvp, imp, t05, consultation-management]

# Summary
Документ фиксирует результат выполнения T05 (`Consultation Management`) из `DOA-OP-001`: реализован
минимальный контур управления консультациями как отдельной сущностью, привязанной к Lead через `lead_id`.

# Что реализовано в T05
- добавлен service-слой для консультаций (`create`, `list by lead`, `get`, `update status/result`);
- в карточку Lead добавлена SSR-форма создания Consultation;
- в карточке отображается список консультаций текущего лида;
- реализовано обновление `status` и `result` для существующей консультации;
- сохранен минимальный MVP-подход без усложнения lifecycle консультаций.

# Какие файлы созданы/изменены
Созданы:
- `app/services/consultation_service.py`

Изменены:
- `app/services/__init__.py`
- `app/web/routes/leads.py`
- `app/templates/lead_detail.html`

# Как работает consultation management
- Создание:
  - `POST /leads/{lead_id}/consultations`
  - форма принимает `planned_at`, `status`, `result`.
- Отображение:
  - список консультаций загружается в карточке лида через `list_consultations_by_lead(...)`.
- Обновление:
  - `POST /leads/{lead_id}/consultations/{consultation_id}`
  - обновляет поля `status` и `result` выбранной консультации.
- Статусы консультаций ограничены MVP-набором:
  - `planned`, `confirmed`, `completed`, `cancelled`.

# Как консультации связаны с Lead
- используется существующая таблица `consultations` со связью `lead_id -> leads.id`;
- при создании консультации `lead_id` берется из URL карточки лида;
- при выборке используется фильтр `WHERE lead_id = ?`;
- при обновлении дополнительно проверяется принадлежность консультации текущему `lead_id`.

# Что НЕ делалось
- не реализован Dashboard (T06);
- не изменялась логика Contact Log;
- не добавлялись автоматические изменения статуса Lead;
- не усложнялся lifecycle консультаций (без сложных автоматов/интеграций).

# Какая проверка выполнена
- синтаксическая проверка Python-файлов (`py_compile`);
- сценарий создания lead;
- сценарий создания consultation;
- проверка отображения consultation в карточке;
- обновление статуса consultation;
- сохранение и отображение `result`;
- проверка связи по `lead_id` в SQLite.

# Соответствие OP
Реализация соответствует T05 в `DOA-OP-001`:
- реализован минимальный `Consultation Management`;
- обеспечены create/list/update в границах MVP;
- сохранено разделение сущностей по DEC-решению (`Consultation` отдельно от `Lead`).

# Next Steps
- перейти к T06 (`Dashboard`) в рамках `DOA-OP-001`.
