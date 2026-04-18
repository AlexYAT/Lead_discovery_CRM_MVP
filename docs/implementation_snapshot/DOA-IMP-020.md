## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-020
- Status: accepted
- Date: 2026-04-18
- Parent: [DOA-OP-005](../operational_plan/DOA-OP-005.md)
- Tags: [lead-discovery, crm, mvp, imp, candidate-queue, op-005, cycle-close, t07, final]

# Summary

Финальный **aggregate** implementation snapshot по завершении цикла **candidate queue MVP iteration** ([DOA-OP-005](../operational_plan/DOA-OP-005.md)): curated inbound / draft layer внедрён, провалидирован ([DOA-VAL-004](../validation_reports/DOA-VAL-004.md), verdict **passed**), готов как **новый product baseline** MVP без дублирования пошагового содержания промежуточных IMP-016–019.

# Scope

- Закрытие **DOA-OP-005** (операционный план первой итерации candidate queue).
- Продуктовый scope: **draft layer** до CRM — отдельные `candidates`, импорт, отбор, одиночный переход в `leads`.

# Артефакты цикла

| Артефакт | Роль |
|----------|------|
| [DOA-OP-005](../operational_plan/DOA-OP-005.md) | Parent operational plan |
| [DOA-DEC-004](../decision_log/DOA-DEC-004.md) | Decision baseline (таблица, lifecycle, одиночный convert, `converted`) |
| [DOA-AUD-002](../audit_check/DOA-AUD-002.md) | T01 — интеграция и схема |
| [DOA-IMP-016](./DOA-IMP-016.md) | T02 — storage + bootstrap |
| [DOA-IMP-017](./DOA-IMP-017.md) | T03 — CSV import |
| [DOA-IMP-018](./DOA-IMP-018.md) | T04 — reject / атомарный convert |
| [DOA-IMP-019](./DOA-IMP-019.md) | T05 — SSR UI `/candidates` |
| [DOA-VAL-004](../validation_reports/DOA-VAL-004.md) | T06 — validation (**passed**) |

# Что реализовано по циклу (сводно)

- Отдельная таблица **`candidates`** и **`lead_id`** для traceability; FK на `leads` при необходимости (см. схему).
- **Bootstrap** для уже существующей БД: идемпотентный `init_db()` + `CREATE IF NOT EXISTS` в `schema.sql` (см. IMP-016 / AUD-002).
- **Storage:** `create_candidate`, `list_candidates`, `get_candidate` с паттернами SQLite hardening на write.
- **CSV import** одного формата (обязательные колонки + опциональные `notes`), fail-fast; только строки `candidates` со статусом `new`.
- **Reject** без DELETE; **convert** одиночный, атомарный (INSERT `leads` + UPDATE `candidate` в одной короткой транзакции), терминальный статус **`converted`**.
- **SSR:** маршруты `/candidates`, import textarea, reject/convert, редирект на **`/leads/{lead_id}`**, ссылка на lead для converted.
- **CRM:** существующий flow лидов после convert **не** заменён; FSM lead **не** расширялся в рамках OP-005.

# Что подтверждено validation (DOA-VAL-004)

- Цикл **OP-005** по критериям плана и DEC проверен набором **V01–V15**.
- **Verdict: passed** — блокирующих дефектов в границах итерации не зафиксировано.

# Что сознательно не входит в baseline

- Batch convert, scraping, enrichment, auto discovery.
- Сложная аналитика по очереди, multi-user, расширение **lead FSM** и новые источники данных — только отдельный DocOps-lifecycle.

# Final conclusion

- **DOA-OP-005** считается **завершённым** по артефактам T01–T06 и настоящему финальному snapshot **T07**.
- **Candidate queue** принят как **новый product baseline** MVP поверх стабильного SQLite/CRM слоя.
- Система готова к **следующему lifecycle** (новая IDEA/ARCH/DEC/OP цепочка вне данного документа).
