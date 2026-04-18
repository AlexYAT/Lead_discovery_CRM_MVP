## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-016
- Status: accepted
- Date: 2026-04-18
- Parent: [DOA-OP-005](../operational_plan/DOA-OP-005.md)
- Tags: [lead-discovery, crm, mvp, imp, candidate-queue, t02, storage]

# Summary

Документ фиксирует выполнение **T02** из [DOA-OP-005](../operational_plan/DOA-OP-005.md): таблица **`candidates`**, исправление **bootstrap** для уже существующих SQLite-файлов и минимальный **service layer** (create/list/get) без import, reject, convert и UI.

# Что выполнено в рамках T02

- добавлена таблица `candidates` в `app/db/schema.sql` с индексом для очереди;
- изменён `init_db()` так, чтобы DDL применялся и к **существующим** БД (см. ниже);
- добавлен `app/services/candidate_service.py` с функциями хранения;
- экспорт символов в `app/services/__init__.py`.

# Какие файлы изменены / созданы

- `app/db/schema.sql`
- `app/db/database.py`
- `app/services/candidate_service.py` (новый)
- `app/services/__init__.py`
- `docs/implementation_snapshot/DOA-IMP-016.md` (настоящий снимок)

# Таблица `candidates`

- Поля: `id`, `platform`, `profile_name`, `profile_url`, `notes`, `status` (DEFAULT `'new'`), `lead_id` (NULL, FK на `leads(id)` с `ON DELETE SET NULL`), `created_at`, `updated_at` (TEXT, `CURRENT_TIMESTAMP` в стиле `leads`).
- Индекс: `idx_candidates_status_created_at` на `(status, created_at)` для списка очереди.

# Bootstrap / migration для существующей БД

**Проблема (DOA-AUD-002):** при раннем `return`, если таблица `leads` уже есть, полный `schema.sql` не выполнялся — таблица `candidates` не появлялась.

**Решение:** `init_db()` **всегда** выполняет `connection.executescript(schema_sql)`. Все DDL в `schema.sql` используют `CREATE TABLE IF NOT EXISTS` / `CREATE INDEX IF NOT EXISTS`, поэтому повторный запуск **идемпотентен**: на новой БД создаётся полная схема, на существующей — добавляются только отсутствующие объекты (в т.ч. `candidates`), без удаления `leads` и без изменения FSM.

# Функции в `candidate_service`

| Функция | Назначение |
|---------|------------|
| `create_candidate(platform, profile_name, profile_url, notes="")` | INSERT, статус `new`, write path с `run_write_with_retry` и `with connection:` |
| `list_candidates(*, status_filter=None, limit=None)` | SELECT с опциональным фильтром по `status`, сортировка по `created_at` / `id` |
| `get_candidate(candidate_id)` | SELECT по `id`, read path без retry |

# Что сознательно не входит в T02

- import кандидатов (T03);
- reject / convert (T04);
- SSR UI очереди (T05);
- validation / final snapshot цикла (T06–T07).

# Проверка (минимальная)

- `python -m py_compile` для затронутых модулей;
- `init_db()` на проектной БД и на временной БД только с `leads` — таблица `candidates` присутствует;
- `create_candidate` / `list_candidates` / `get_candidate`;
- `from app.main import app` успешно.
