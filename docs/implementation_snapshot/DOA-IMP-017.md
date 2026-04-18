## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-017
- Status: accepted
- Date: 2026-04-18
- Parent: [DOA-OP-005](../operational_plan/DOA-OP-005.md)
- Tags: [lead-discovery, crm, mvp, imp, candidate-queue, t03, csv-import]

# Summary

Документ фиксирует выполнение **T03** из [DOA-OP-005](../operational_plan/DOA-OP-005.md): импорт кандидатов из **одного** простого формата (CSV) в таблицу `candidates` со статусом `new`, без создания `leads`, без reject/convert и без UI.

# Формат импорта

- **CSV**, первая строка — заголовок.
- **Обязательные колонки:** `platform`, `profile_name`, `profile_url`.
- **Опциональная колонка:** `notes` (может отсутствовать или быть пустой).
- Значения ячеек **trim**; полностью **пустые строки данных** пропускаются.

# Где реализована import-логика

- `app/services/candidate_service.py`:
  - исключение `CandidateImportError`;
  - функция `import_candidates_from_csv(csv_text: str) -> int` (количество созданных candidates).

# Поведение при невалидных строках

**Fail-fast:** при первой **некорректной** строке данных (строка не полностью пустая, но отсутствует одно из обязательных полей после trim) выбрасывается `CandidateImportError` с указанием номера строки (нумерация с **2** для первой строки данных под заголовком). До записи в БД все строки **сначала** валидируются в памяти; затем все валидные строки пишутся в **одной** короткой транзакции — при ошибке валидации **нет** частичной записи.

Отдельные случаи:

- отсутствует обязательная **колонка** в заголовке → `CandidateImportError` до обхода строк;
- пустой или только-whitespace файл → возврат `0`.

# Write path / SQLite hardening

- Одна операция записи: `run_write_with_retry` оборачивает один вызов, внутри которого `with get_connection()` + `with connection:` и цикл `INSERT` — одна явная короткая транзакция на весь успешно распарсенный батч.
- `leads` не создаются.

# Изменённые файлы

- `app/services/candidate_service.py`
- `app/services/__init__.py`
- `docs/implementation_snapshot/DOA-IMP-017.md` (настоящий снимок)

# Что сознательно не входит в T03

- reject / convert (T04);
- SSR UI очереди (T05);
- batch convert, scraping, enrichment, auto discovery (вне DEC/OP).
