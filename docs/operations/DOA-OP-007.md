# DOA-OP-007 — VK Lead Discovery Implementation Plan

## Metadata

- id: DOA-OP-007
- type: OP
- parent: DOA-ARCH-006
- status: planned
- date: 2026-04-18

---

## Context

Настоящий план описывает реализацию discovery pipeline для VK Lead Discovery.

Архитектура зафиксирована в DOA-ARCH-006.
Стратегия discovery зафиксирована в DOA-DEC-006.

Система уже имеет стабильный baseline:

- Candidate Queue
- convert candidate → lead
- CRM layer
- SSR UI
- JSON API
- validation/audit passed for previous lifecycle

Новый pipeline должен добавлять источник кандидатов, не нарушая существующий baseline.

---

## Operational Goal

Реализовать MVP pipeline, который:

- получает кандидатов через search layer
- фильтрует их через LLM classification
- нормализует результаты
- импортирует их в Candidate Queue
- допускает ручной или периодический запуск

---

## Execution Strategy

Реализация выполняется по слоям:

1. Search acquisition
2. Classification
3. Normalization
4. Candidate ingestion
5. Operator entrypoint / execution trigger
6. Validation

Подход:

- batch-oriented
- docs-first
- incremental implementation
- отдельный implementation snapshot на каждый значимый слой

---

## Execution Plan

### Step 1 — Search Acquisition Layer (IMP-026)

Цель:

Реализовать слой получения raw candidate results из primary search provider.

Требования:

- поддержка primary search provider
- архитектурная точка для fallback provider
- получение результатов discovery без привязки к CRM
- ограничение объёма выборки
- работа только с публичными результатами

Результат:

- pipeline умеет получать raw results для дальнейшей обработки

---

### Step 2 — LLM Classification Layer (IMP-027)

Цель:

Реализовать classification layer для pain-signal detection.

Требования:

- классификация candidate text как pain / no pain
- optional confidence
- без генеративного поведения
- результат пригоден для pipeline filtering

Результат:

- raw results могут быть отфильтрованы по качеству

---

### Step 3 — Normalization Layer (IMP-028)

Цель:

Привести отобранные результаты к формату системы.

Минимальный ожидаемый набор полей:

- text
- author
- source_link
- source
- optional metadata

Требования:

- единый внутренний формат
- совместимость с Candidate Queue ingestion
- отсутствие привязки к UI

Результат:

- pipeline выдаёт normalized candidates

---

### Step 4 — Candidate Ingestion Layer (IMP-029)

Цель:

Передавать normalized candidates в существующую Candidate Queue.

Требования:

- не изменять convert flow
- не обходить candidate lifecycle
- использовать существующую модель candidates
- учитывать deduplication / duplicate tolerance согласно текущему baseline

Результат:

- discovery pipeline начинает создавать кандидатов в системе

---

### Step 5 — Execution Entry Point (IMP-030)

Цель:

Добавить операторский способ запуска pipeline.

Допустимые формы:

- debug/manual run
- bounded execution trigger
- минимальный операторский entrypoint для MVP

Требования:

- отсутствие real-time streaming
- отсутствие постоянного фонового процесса
- отсутствие автоматической коммуникации

Результат:

- pipeline можно запускать управляемо

---

### Step 6 — Validation (VAL-006)

Цель:

Проверить:

- search layer возвращает raw results
- classification фильтрует кандидатов
- normalization выдаёт корректный формат
- ingestion создаёт candidates
- Candidate Queue остаётся рабочей
- convert и CRM flow не регрессируют

Результат:

- подтверждена работоспособность discovery pipeline

---

## Implementation Order

1. IMP-026 — Search Acquisition Layer
2. IMP-027 — LLM Classification Layer
3. IMP-028 — Normalization Layer
4. IMP-029 — Candidate Ingestion Layer
5. IMP-030 — Execution Entry Point
6. VAL-006

---

## Compatibility Constraints

План обязан сохранить:

- Candidate Queue как входной слой
- candidate → lead convert без изменений
- CRM layer без изменений
- SSR baseline без деградации
- отсутствие автоматической коммуникации
- использование только публичных данных

---

## Non-Goals in This Plan

В этот operational plan не входят:

- multi-source orchestration
- streaming ingestion
- advanced scoring system
- automated outreach
- enrichment beyond normalized discovery payload
- deep analytics for discovery quality

---

## Expected Result

После выполнения OP-007 система должна поддерживать новый discovery flow:

Search Provider  
→ Raw Results  
→ LLM Classification  
→ Normalization  
→ Candidate Queue  
→ Manual Qualification  
→ Lead CRM  

При этом существующий CRM baseline должен остаться неизменным.

---

## Next Step

→ DOA-IMP-026

Начать с Search Acquisition Layer.
