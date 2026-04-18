# DOA-IMP-026 — Search Acquisition Layer

## Metadata

- id: DOA-IMP-026
- type: IMP
- parent: DOA-OP-007
- status: planned
- date: 2026-04-18

---

## Context

Данный snapshot фиксирует реализацию первого слоя discovery pipeline:

Search Acquisition Layer.

Основано на:

- DOA-ARCH-006
- DOA-OP-007 (Step 1)

---

## Scope

Планируется реализовать:

- получение кандидатов через primary search provider
- поддержка архитектурной точки для fallback provider
- ограничение объёма выборки (bounded recall)
- подготовка raw candidate results для следующего слоя

Не реализовано:

- classification (следующий шаг)
- ingestion в Candidate Queue
- operator execution

---

## Query Strategy (важно)

Введена стратегия формирования поисковых запросов:

- система использует набор predefined query patterns
- каждый запрос направлен на выявление pain signals
- примеры категорий запросов:
  - отношения
  - тревожность
  - повторяющиеся проблемы
  - эмоциональное состояние
  - кризисные ситуации

Цель:

- повысить релевантность recall
- снизить нагрузку на classification layer

---

## Search Layer Design

Компоненты:

- search provider interface
- primary provider (Brave)
- fallback provider (абстрактный)

Поведение:

- выполнение одного или нескольких поисковых запросов
- агрегирование результатов
- нормализация raw результатов (минимальная)

---

## Output Contract

Search layer возвращает:

- text (content)
- source_link
- optional metadata

Без:

- классификации
- фильтрации по качеству

---

## Constraints

- только публичные данные
- отсутствие агрессивного scraping
- ограничение количества результатов
- соблюдение правил платформ

---

## Observations

- качество результатов зависит от query strategy
- search уже выполняет первичную фильтрацию
- возможен шум, который будет обработан в следующем слое

---

## Result

- запланирована реализация Search Acquisition Layer
- pipeline будет получать входной поток кандидатов после реализации
- система будет готова к внедрению classification layer

---

## Next Step

→ DOA-IMP-027 (LLM Classification Layer)
