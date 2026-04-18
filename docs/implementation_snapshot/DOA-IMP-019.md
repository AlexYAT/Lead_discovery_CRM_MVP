## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-019
- Status: accepted
- Date: 2026-04-18
- Parent: [DOA-OP-005](../operational_plan/DOA-OP-005.md)
- Tags: [lead-discovery, crm, mvp, imp, candidate-queue, t05, ssr-ui]

# Summary

Документ фиксирует выполнение **T05** из [DOA-OP-005](../operational_plan/DOA-OP-005.md): минимальный **SSR UI** очереди кандидатов на отдельных маршрутах `/candidates`, без изменения DEC и без затрагивания validation / final snapshot цикла.

# Изменённые / созданные файлы

- `app/web/routes/candidates.py` (новый)
- `app/templates/candidates_list.html` (новый)
- `app/web/__init__.py`
- `app/main.py`
- `app/templates/index.html`
- `docs/implementation_snapshot/DOA-IMP-019.md` (настоящий снимок)

# SSR routes

| Метод | Путь | Назначение |
|-------|------|------------|
| GET | `/candidates` | Список кандидатов + форма импорта |
| POST | `/candidates/import` | Импорт CSV из текстового поля |
| POST | `/candidates/{id}/reject` | Reject (домен T04) |
| POST | `/candidates/{id}/convert` | Convert → редирект на `/leads/{lead_id}` |

Маршрут **`POST /candidates/import`** объявлен **до** `/{candidate_id}/…`, чтобы не пересекаться с числовым id.

# UI-путь импорта

Один **textarea** `csv_text` в форме POST на `/candidates/import` — вставка текста CSV целиком (воспроизводимо, без загрузки файла).

# Отображение reject / convert / converted

- **`new`:** кнопки «Отклонить» и «В CRM (lead)» (две формы POST).
- **`rejected`:** текст «Отклонён», **без** кнопок (повторный reject скрыт; доменный no-op T04 не вызывается из UI).
- **`converted`:** текст «В CRM», кнопка convert **не** показывается; в колонке **Lead** — ссылка **`/leads/{lead_id}`** при наличии `lead_id`.

Ошибки `CandidateImportError` / `CandidateNotFoundError` / `CandidateStateError` возвращают снова страницу списка с **`error_message`** (красный блок).

После успешного **convert** — редирект **303** на карточку лида. После **import** (если импортировано >0 строк) — редирект на `/candidates`. После **reject** — редирект на `/candidates`.

# Проверки (минимальные)

- `GET /candidates` → 200;
- `POST /candidates/import` с валидным CSV → редирект, строки в списке;
- `POST .../reject` → редирект, статус `rejected`;
- `POST .../convert` → 303 на `/leads/{id}`;
- в HTML для `converted` есть ссылка на lead;
- `from app.main import app` — успешно.

# Что не входит в T05

- VAL и финальный snapshot цикла OP-005 (T06–T07);
- фильтр по status в UI;
- batch convert, enrichment, scraping, новые источники данных.
