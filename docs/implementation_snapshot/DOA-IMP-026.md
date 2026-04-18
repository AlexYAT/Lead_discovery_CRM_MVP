# DOA-IMP-026 — Search Acquisition Layer

## Metadata

- id: DOA-IMP-026
- type: IMP
- parent: DOA-OP-007
- status: implemented
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

Реализовано:

- получение кандидатов через primary search provider
- заложена архитектурная точка для fallback provider (реализация не включена в MVP)
- ограничение объёма выборки (bounded recall)
- подготовка raw candidate results для следующего слоя
- query strategy (predefined patterns) не реализована как отдельный модуль и будет добавлена в следующих шагах

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

- реализован Search Acquisition Layer (минимальная версия)
- pipeline способен возвращать raw candidate results
- реализована базовая архитектура search provider (mock)
- система готова к внедрению classification layer

---

## Implementation Details (MVP)

Реализация выполнена в:

app/discovery/search/

Состав:

- models.py:
  - структура SearchHit (text, source_link)

- search_provider.py:
  - интерфейс SearchProvider

- brave_provider.py:
  - mock provider (детерминированные результаты)

- service.py:
  - функция search_candidates(query, limit)

Характер реализации:

- используется mock provider (без внешних API)
- deterministic output
- bounded recall (limit)
- независимость от CRM

---

## Next Step

→ DOA-IMP-027 (LLM Classification Layer)
