# DOA-ARCH-006 — VK Lead Discovery Architecture

## Metadata

- id: DOA-ARCH-006
- type: ARCH
- parent: DOA-DEC-006
- status: draft
- date: 2026-04-18

---

## Context

- CRM baseline реализован (Candidate Queue → Lead → CRM)
- отсутствует входящий поток лидов
- DOA-DEC-006 зафиксировал стратегию:
  Search Engine + LLM-based classification
- pipeline предполагает периодический запуск, а не постоянный streaming

---

## Architectural Goal

Создать discovery pipeline, который:

- находит кандидатов во внешнем источнике (VK через search layer)
- фильтрует кандидатов по наличию pain signals
- передаёт релевантных кандидатов в Candidate Queue
- не нарушает существующий CRM baseline

---

## High-Level Architecture

Pipeline состоит из двух основных слоёв:

### 1. Recall Layer (Search)

Задача:

- обнаружение потенциальных кандидатов

Источник:

- внешний search provider

Primary:

- Brave Search

Fallback:

- альтернативный search provider (generic web search / platform-specific search)

Роль:

- получение списка кандидатов (post / comment / discussion)
- базовая релевантность через search ranking

---

### 2. Precision Layer (LLM Classification)

Задача:

- определить наличие pain signal

Функция:

- классификация текста кандидата:
  - pain / no pain
  - optional: confidence

Результат:

- отбор кандидатов для дальнейшей обработки

---

### 3. Candidate Normalization Layer

Задача:

- привести данные к формату системы

Поля:

- text
- author
- source_link
- source (VK)
- optional metadata

---

### 4. Candidate Ingestion Layer

Задача:

- передать кандидатов в существующую Candidate Queue

Требования:

- совместимость с текущей моделью candidates
- отсутствие изменений convert flow
- соблюдение deduplication (если уже есть в системе)

---

## End-to-End Flow

Search Query  
→ Recall Layer (Brave Search)  
→ Raw Results  
→ Precision Layer (LLM classification)  
→ Filtered Candidates  
→ Normalization  
→ Candidate Queue  
→ Manual Qualification  
→ Lead CRM  

---

## Execution Model

- запуск вручную или по расписанию
- не требуется постоянный поток
- допускается batch-обработка
- допускается ограничение объёма выборки

---

## Integration with Existing System

Система должна:

- использовать существующую Candidate Queue
- не изменять convert_candidate_to_lead
- не изменять CRM layer (contact_attempts / consultations)
- не изменять SSR flows
- не изменять API contracts

---

## Architectural Constraints

- только публичные данные
- отсутствие агрессивного scraping
- соблюдение правил платформ
- отсутствие автоматической коммуникации
- минимальная нагрузка на источники

---

## Design Decisions

- разделение на recall и precision layer
- использование search provider как primary discovery механизма
- использование LLM только для классификации (не для генерации)
- отказ от heuristic-based filtering на уровне MVP
- batch-oriented execution вместо streaming

---

## Failure Handling

- при недоступности primary search:
  → использовать fallback provider

- при ошибке классификации:
  → кандидат отбрасывается или помечается как uncertain

- при отсутствии результатов:
  → pipeline завершает выполнение без ошибок

---

## Non-Goals

- real-time streaming ingestion
- автоматическая коммуникация с пользователями
- построение сложной scoring системы
- multi-source orchestration (на MVP этапе)

---

## Expected Outcome

- появляется внешний источник кандидатов
- формируется поток данных в Candidate Queue
- повышается качество кандидатов за счёт LLM-фильтрации
- система остаётся простой и управляемой

---

## Next Step

→ DOA-OP-007 (план реализации discovery pipeline)
