# DOA-IMP-029 — Candidate Ingestion Layer

## Metadata

- id: DOA-IMP-029
- type: IMP
- parent: DOA-OP-007
- status: implemented
- date: 2026-04-18

---

## Context

Данный snapshot фиксирует реализацию четвёртого слоя discovery pipeline:

Candidate Ingestion Layer.

Основано на:

- DOA-ARCH-006
- DOA-OP-007 (Step 4)

---

## Scope

Реализовано:

- импорт normalized candidates в существующую Candidate Queue
- маппинг normalized contract → candidate model
- возврат созданных candidate ids
- совместимость с существующим candidate lifecycle

Не реализовано:

- отдельная deduplication strategy
- operator execution
- full end-to-end trigger

---

## Implementation Details (MVP)

Реализация выполнена в:

app/discovery/ingestion/

Состав:

- service.py
- __init__.py

Ingestion использует существующий candidate baseline и не вводит новую discovery-specific storage model.

---

## Mapping

Использовано преобразование (фактическая схема таблицы `candidates` — только `platform`, `profile_name`, `profile_url`, `notes`):

- `NormalizedCandidate.source` → `candidates.platform` (fallback `"vk"`)
- `NormalizedCandidate.author` → `candidates.profile_name`, при отсутствии — строка **`VK discovery`**
- `NormalizedCandidate.source_link` → `candidates.profile_url` (обязательный URL поста/источника)
- `NormalizedCandidate.text`, `detected_theme`, `score`, `metadata` → сериализуются в **`candidates.notes`** как один JSON-объект с ключами `discovery`, `text`, `detected_theme`, `score`, `metadata` (без миграции схемы)

Отдельных колонок `source_text`, `source_url`, `detected_theme`, `score` в baseline нет — значения сохранены через `notes`.

---

## Duplicate handling (фактическое поведение)

- Отдельной deduplication нет: каждый вызов `ingest_candidates` создаёт новую строку `candidates` со статусом `new`.
- Если позже появится dedup на уровне candidate layer, ingestion можно будет направить через него без смены контракта `ingest_candidates`.

---

## Constraints Compliance

Проверено:

- Candidate Queue используется как входной слой
- convert flow не изменён
- CRM baseline не затронут
- ingestion не меняет UI и SSR

---

## Result

- реализован Candidate Ingestion Layer
- discovery pipeline теперь способен создавать candidates в системе
- система готова к следующему шагу: execution entrypoint / validation

---

## Next Step

→ DOA-IMP-030 (Execution Entry Point)
