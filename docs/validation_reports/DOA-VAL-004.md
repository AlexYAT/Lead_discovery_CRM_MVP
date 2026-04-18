# Validation Report: DOA-VAL-004

## Document Metadata

- **ID:** DOA-VAL-004
- **Doc type:** validation_report
- **Status:** accepted
- **Date:** 2026-04-18
- **Parent:** [DOA-OP-005](../operational_plan/DOA-OP-005.md)
- **Tags:** [lead-discovery, crm, mvp, val, candidate-queue, op-005-t06, mvp-iteration]

---

## Scope

- Валидация **MVP-итерации candidate queue** по исполнению [DOA-OP-005](../operational_plan/DOA-OP-005.md) (T01–T05): **storage**, **CSV import**, **reject / convert**, **SSR UI** на `/candidates`, согласованность с [DOA-DEC-004](../decision_log/DOA-DEC-004.md) (отдельная таблица, lifecycle, одиночный convert, `converted`).
- Покрытие: функциональные проверки перечисленных ниже **V01–V15** на уровне **ручного/скриптового** прогона (локальный Python, временные файлы БД, `TestClient` для HTTP).

**Вне scope:** stress/load/performance; batch convert; enrichment; scraping; auto discovery; полный регрессионный UI всех экранов приложения; multi-instance повторная приёмка.

---

## Артефакты

| Артефакт | Роль |
|----------|------|
| [DOA-OP-005](../operational_plan/DOA-OP-005.md) | operational plan цикла |
| [DOA-AUD-002](../audit_check/DOA-AUD-002.md) | аудит интеграции (T01) |
| [DOA-IMP-016](../implementation_snapshot/DOA-IMP-016.md) | T02 storage |
| [DOA-IMP-017](../implementation_snapshot/DOA-IMP-017.md) | T03 import |
| [DOA-IMP-018](../implementation_snapshot/DOA-IMP-018.md) | T04 reject/convert |
| [DOA-IMP-019](../implementation_snapshot/DOA-IMP-019.md) | T05 SSR UI |

---

## Validation checks

| ID | Проверка | Результат |
|----|-----------|-----------|
| **V01** | `init_db()` создаёт таблицу `candidates` на **новой** БД и на **существующей** БД, где уже есть только `leads` | **pass** |
| **V02** | `create_candidate` / `list_candidates` / `get_candidate` | **pass** |
| **V03** | Валидный CSV import создаёт candidates со статусом `new` | **pass** |
| **V04** | Пустые строки в CSV не ломают импорт (ожидаемое число созданных строк) | **pass** |
| **V05** | Невалидный CSV → `CandidateImportError` (fail-fast), без частичной записи лишних строк после предыдущего валидного импорта в отдельной БД | **pass** |
| **V06** | `reject` переводит в `rejected`, строка в БД **не** удаляется | **pass** |
| **V07** | `convert` создаёт lead, candidate `converted` и `lead_id` установлен | **pass** |
| **V08** | Повторный `convert` запрещён (`CandidateStateError`) | **pass** |
| **V09** | `reject` после `converted` и `convert` после `rejected` — доменные ошибки | **pass** (подпункты V09a/V09b в прогоне) |
| **V10** | `GET /candidates` — HTTP 200 | **pass** |
| **V11** | `POST /candidates/import` — импорт отражается в списке | **pass** |
| **V12** | `POST /candidates/{id}/reject` — статус в SSR | **pass** |
| **V13** | `POST /candidates/{id}/convert` — 303 на `/leads/{id}` | **pass** |
| **V14** | У `converted` в HTML списка есть ссылка на lead | **pass** |
| **V15** | `GET /leads/{id}` после convert — 200, данные лида (имя профиля) отображаются | **pass** |

**Метод:** единый воспроизводимый Python-прогон (временные файлы `*.db`, смена `app.db.database.DB_PATH` в процессе, `starlette.testclient.TestClient` для V10–V15). Дефектов, требующих правки кода вне T06, **не** выявлено.

---

## Known limitations

- Нет нагрузочного / многопользовательского теста.
- SSR проверен через `TestClient`, не полным ручным браузерным прогоном.
- Не проверялась каждая комбинация FSM lead после множественных конверсий (минимальная карточка одного лида).

---

## Verdict

**passed**

Обоснование: проверки **V01–V15** выполнены с результатом **pass**; критерии OP-005 для итерации candidate queue (отдельное хранение, bootstrap, import, reject/convert, UI и связь с CRM) на наблюдаемом уровне **выполняются**. Оговорки ограничены объёмом проверки (см. Known limitations), а не отказом функциональности.

---

## Findings

- Критических или блокирующих несоответствий DEC/ARCH/реализации в ходе T06 **не зафиксировано**.
