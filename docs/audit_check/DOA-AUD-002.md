## Metadata
- Project: DOA
- Doc type: audit_check
- ID: DOA-AUD-002
- Status: accepted
- Date: 2026-04-18
- Parent: [DOA-OP-005](../operational_plan/DOA-OP-005.md)
- Lifecycle: OP-005 **T01** (schema & integration audit перед реализацией candidates)
- Tags: [lead-discovery, crm, mvp, sqlite, candidate-queue, integration-audit, t01]

# Summary

Аудит текущей схемы БД и **точек интеграции** приложения перед внедрением слоя **candidates** по [DOA-DEC-004](../decision_log/DOA-DEC-004.md) и [DOA-OP-005](../operational_plan/DOA-OP-005.md). Цель — минимизировать регрессию по `leads` / FSM и зафиксировать, где потребуются изменения в T02+.

Источник истины по фактической схеме: `app/db/schema.sql` (состояние репозитория на момент аудита).

---

## Current DB schema

### Таблица `leads`

| Колонка | Тип / ограничение | Примечание |
|---------|-------------------|------------|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | |
| `platform` | TEXT NOT NULL | |
| `profile_name` | TEXT NOT NULL | |
| `profile_url` | TEXT NOT NULL | |
| `source_url` | TEXT | nullable |
| `source_text` | TEXT | nullable |
| `detected_theme` | TEXT | nullable |
| `score` | REAL | nullable |
| `status` | TEXT NOT NULL DEFAULT `'new'` | FSM лида (не трогать в рамках candidate scope) |
| `notes` | TEXT | nullable |
| `created_at` | TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP | |

### Таблица `contact_attempts`

| Колонка | Ограничение |
|---------|--------------|
| `id` | PK |
| `lead_id` | NOT NULL, **FK → leads(id) ON DELETE CASCADE** |
| `date`, `message_text`, `outcome`, `next_action` | |

Индекс: `idx_contact_attempts_lead_id` на `lead_id`.

### Таблица `consultations`

| Колонка | Ограничение |
|---------|--------------|
| `id` | PK |
| `lead_id` | NOT NULL, **FK → leads(id) ON DELETE CASCADE** |
| `planned_at`, `status`, `result` | |

Индекс: `idx_consultations_lead_id` на `lead_id`.

### Связи (текущие)

- `contact_attempts.lead_id` → `leads.id`
- `consultations.lead_id` → `leads.id`
- Каскадное удаление дочерних строк при удалении лида (на момент аудита поведение задано схемой).

---

## Planned changes

### Новая таблица `candidates` (план по DEC/ARCH; DDL на T02)

Отдельная таблица, **не** слияние с `leads`.

| Поле | Назначение |
|------|------------|
| `id` | PK |
| `platform` | TEXT NOT NULL |
| `profile_name` | TEXT NOT NULL |
| `profile_url` | TEXT NOT NULL |
| `notes` | TEXT, nullable |
| `status` | TEXT NOT NULL — lifecycle очереди (`new`, `rejected`, `converted`, … точный enum на T02/DEC) |
| `lead_id` | INTEGER **NULL** до convert; после успешной конверсии → id созданного лида |
| `created_at` / `updated_at` | Рекомендуется для сортировки очереди и аудита (согласовать с существующим стилем `leads.created_at` как TEXT ISO) |

**Связь с `leads`:** опционально **FK** `candidates(lead_id) REFERENCES leads(id)` — решение на T02 (учесть порядок создания: сначала lead при convert, затем update candidate). Альтернатива без FK — только в DEC/IMP, если упрощает bootstrap.

**Инварианты DEC:** нет физического DELETE при reject; терминальный статус после convert — **`converted`**; только одиночная конверсия в MVP.

---

## Integration points

| Область | Файл / модуль | Роль при добавлении candidates |
|---------|----------------|--------------------------------|
| Схема + bootstrap | `app/db/schema.sql` | Добавление `CREATE TABLE candidates` и индексов. |
| Bootstrap логика | `app/db/database.py` — `init_db()` | Сейчас: если таблица **`leads`** существует, **весь** `executescript` пропускается → **новая таблица на существующей БД не создастся автоматически** (см. Risks). Потребуется изменение стратегии миграции на T02 (не в рамках T01). |
| Соединения / retry | `app/db/database.py` | Без смены контракта; новые write-функции candidates — по тем же паттернам, что lead/contact/consultation. |
| Создание лида | `app/services/lead_service.py` — `create_lead` | **Вызов из convert:** reuse существующей логики создания lead (поля из candidate → параметры `create_lead`); **не** менять сигнатуру и FSM без отдельного DEC. |
| Новый слой | `app/services/candidate_service.py` (план) | CRUD candidates, `reject`, `convert_to_lead` (домен). |
| SSR лиды | `app/web/routes/leads.py` | Без обязательных изменений для T01; опционально ссылки с очереди после convert. |
| Новые маршруты | `app/web/routes/candidates.py` (план) + `app/web/__init__.py` | Префикс вне `/leads` (ARCH-004). |
| Точка монтирования | `app/main.py` | `include_router` для candidate router; `startup_init_db` уже вызывает `init_db`. |
| API health | `app/api/routes/base.py` | Без конфликта имён; кандидаты не обязаны в `/api` в MVP. |
| Главная | `app/templates/index.html` (контекст из `main.py`) | Позже: ссылка «Очередь кандидатов» — не часть T01-кода. |

---

## Risks

| Риск | Описание |
|------|----------|
| **`init_db` и существующая БД** | Условие «есть `leads`» → **ранний return** означает, что развертывание только через дополнение `schema.sql` **не** применится к уже созданному файлу `data/*.db`. Нужна явная стратегия **миграции** (отдельный шаг bootstrap: `CREATE TABLE IF NOT EXISTS candidates`, проверка версии схемы и т.д.) на T02. |
| **Имена** | Таблица `candidates` vs зарезервированные слова SQLite — имя допустимо; избегать дубля с представлениями/алиасами в SQL внутри сервисов. |
| **FK и порядок транзакций** | При convert: создание строки в `leads` и обновление `candidates.lead_id` + `status=converted` должны быть согласованы (одна короткая транзакция или два шага с чётким rollback — T04). |
| **Дубли `profile_url`** | Между `candidates` и `leads` и внутри очереди — см. OP-005 Risks; не ломает схему, но влияет на UX/валидацию. |
| **Регрессия CRM** | Любой вызов `create_lead` из convert не должен менять обязательные поля lead или FSM стартового статуса без согласования. |

---

## Notes

- **Не** менять колонки/семантику таблицы **`leads`** и правила **FSM** в `lead_service` в рамках candidate scope ([DOA-DEC-004](../decision_log/DOA-DEC-004.md)).
- Candidates — **отдельный** поток данных до явного convert.
- Импорт (T03) и UI (T05) касаются новых файлов и маршрутов преимущественно; текущие шаблоны лидов можно не трогать до появления ссылок из очереди.

---

## Next step (DocOps)

- **T02** ([DOA-OP-005](../operational_plan/DOA-OP-005.md)): реализация DDL + стратегия миграции для существующих БД + `candidate_service` skeleton по результатам настоящего аудита.
