## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-002
- Status: accepted
- Date: 2026-04-17
- Parent: DOA-OP-001
- Tags: [lead-discovery, crm, mvp, imp, t02, sqlite-schema]

# Summary
Документ фиксирует результат выполнения T02 (`Storage and domain schema`) из `DOA-OP-001`: добавлен
минимальный SQLite bootstrap и доменная схема MVP для сущностей Lead, Contact Attempt и Consultation.

# Что выполнено в рамках T02
- добавлен модуль инициализации SQLite-схемы;
- определен локальный путь базы данных MVP и прозрачный bootstrap-подход;
- реализованы таблицы `leads`, `contact_attempts`, `consultations`;
- добавлены связи через `lead_id` и индексы по внешним ключам;
- интегрирован startup hook, который вызывает инициализацию схемы при запуске приложения.

# Какие файлы созданы/изменены
Созданы:
- `app/db/__init__.py`
- `app/db/database.py`
- `app/db/schema.sql`

Изменены:
- `app/main.py` (подключение `init_db()` на startup)

Служебные артефакты Python bytecode в репозитории:
- `app/db/__pycache__/__init__.cpython-312.pyc`
- `app/db/__pycache__/database.cpython-312.pyc`

Runtime-артефакт локальной проверки (не включен в commit):
- `data/lead_discovery_crm_mvp.db`

# Какие таблицы и связи реализованы
Таблицы:
- `leads`
- `contact_attempts`
- `consultations`

Связи:
- `contact_attempts.lead_id` -> `leads.id` (FOREIGN KEY, `ON DELETE CASCADE`)
- `consultations.lead_id` -> `leads.id` (FOREIGN KEY, `ON DELETE CASCADE`)

Индексы:
- `idx_contact_attempts_lead_id`
- `idx_consultations_lead_id`

# Как выполнена инициализация schema
- SQL-схема хранится в `app/db/schema.sql`.
- Функция `init_db()` в `app/db/database.py` читает схему и выполняет `executescript(...)`.
- Инициализация запускается:
  - автоматически через startup hook в `app/main.py`;
  - вручную воспроизводимо через `python -c "from app.db import init_db; init_db()"`.

# Что сознательно НЕ делалось
- не реализован Lead CRM UI/CRUD (T03);
- не реализован Contact Log UI/CRUD (T04);
- не реализован Consultation UI/CRUD (T05);
- не реализован Dashboard (T06);
- не добавлена сложная миграционная система (только MVP bootstrap).

# Какая проверка выполнена
- выполнена синтаксическая проверка Python-файлов (`py_compile`);
- выполнен запуск bootstrap инициализации SQLite;
- проверено наличие таблиц `leads`, `contact_attempts`, `consultations`;
- проверено наличие внешних ключей на `leads`.

# Соответствие `DOA-OP-001`
Результат полностью соответствует T02:
- реализованы storage schema и domain schema для MVP;
- обеспечен воспроизводимый MVP-подход к инициализации;
- подготовлена база для перехода к T03 без выхода за границы OP.

# Next Steps
- перейти к T03 (`Lead CRM`) в рамках `DOA-OP-001`.
