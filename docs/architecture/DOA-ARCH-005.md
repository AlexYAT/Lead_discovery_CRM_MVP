# DOA-ARCH-005 — CRM Layer Architecture over Candidate Queue Baseline

## Metadata

- id: DOA-ARCH-005
- type: ARCH
- parent: DOA-IDEA-005
- status: draft
- date: 2026-04-18

---

## Context

Система уже имеет зафиксированный baseline:

- Candidate Queue как draft layer
- candidates хранятся отдельно от leads
- import выполняется через CSV
- reject реализован без delete
- convert реализован атомарно:
  - создаётся lead
  - candidate обновляется в той же транзакции
- UI реализован как SSR
- write path для SQLite защищён retry / busy handling policy

Этот baseline считается устойчивым и не должен быть нарушен.

Следующий этап — построение CRM layer поверх уже существующего candidate → lead pipeline.

---

## Architectural Goal

Добавить CRM-слой, который начинается после создания lead и покрывает:

- управление leads
- логирование контактов
- отслеживание консультаций
- фиксированный статусный pipeline
- SSR-представление CRM данных

---

## Architectural Decisions

### 1. Entity Boundary

Сохраняется жёсткая граница:

- candidate = pre-CRM draft entity
- lead = CRM entity

Следствие:

- никакие CRM-действия не выполняются на candidate
- все CRM-сценарии начинаются только после convert в lead

---

### 2. Storage Model

CRM-слой строится на отдельных таблицах.

Целевые сущности:

#### leads
Существующая CRM-сущность, используемая как root entity после convert.

#### contact_attempts
Отдельная таблица для фиксации коммуникаций.

Минимальные поля:
- id
- lead_id
- date
- message_text
- outcome
- next_action
- created_at

#### consultations
Отдельная таблица для фиксации консультаций.

Минимальные поля:
- id
- lead_id
- planned_at
- status
- result
- created_at

Причина выбора:
- нормализованная модель
- SQL-фильтрация и история
- совместимость с аналитикой
- отсутствие JSON-overloading внутри leads

---

### 3. Flow Boundary

Поддерживается следующий поток:

candidate
→ review
→ reject / convert
→ lead
→ contact tracking
→ consultation tracking
→ final business outcome

Граница convert остаётся архитектурной точкой входа в CRM.

Convert не расширяется CRM-логикой сверх текущего baseline.

---

### 4. Status Model

Используется фиксированный status pipeline для leads:

- new
- reviewed
- contacted
- replied
- consultation_booked
- converted
- not_interested

Свойства модели:
- pipeline фиксирован
- динамическая FSM-конфигурация не вводится
- цель — простота MVP и предсказуемость SSR/UI и service layer

---

### 5. UI Architecture

UI остаётся SSR-first.

Новые целевые страницы:

- /leads
- /leads/{id}

Назначение:

#### /leads
- список leads
- базовый обзор статусов
- вход в карточку lead

#### /leads/{id}
- данные lead
- заметки / status
- история contact attempts
- список consultations
- формы добавления interaction records

SPA или отдельный frontend framework не вводятся.

---

### 6. Service Boundary

Новые операции должны быть реализованы через явный service layer.

Ожидаемые направления:
- lead read/update services
- contact_attempt create/list services
- consultation create/list/update services

Изменения должны сохранять текущую SQLite write policy:
- controlled write path
- retry only for transient SQLite busy/locked conditions
- без изменения уже принятого baseline поведения

---

### 7. Compatibility Constraints

Архитектура обязана сохранить совместимость с baseline:

- candidates ≠ leads
- candidate queue остаётся отдельным слоем
- reject остаётся status-based, без delete
- convert остаётся atomic
- /candidates SSR flow не ломается
- SQLite hardening policy сохраняется

---

## Target Module Expansion

Архитектура допускает расширение текущей системы следующими модулями:

### Lead CRM
- lead list
- lead card
- status update
- notes

### Contact Log
- add contact attempt
- view interaction history
- store outcome / next_action

### Consultation Tracking
- create consultation
- update consultation status
- store result

---

## Non-Goals

В этот архитектурный шаг не входят:

- batch convert
- enrichment
- scraping
- analytics expansion beyond minimal counters
- multi-user support
- configurable FSM
- SPA frontend
- external integrations

---

## Expected Architectural Outcome

После реализации по данной архитектуре система должна поддерживать полный MVP-flow:

candidate → lead → contact attempt → consultation → result

При этом baseline candidate queue остаётся стабильным и совместимым.

---

## Next Step

Следующий шаг: DEC-005

DEC должен формально зафиксировать подтверждённые choices:

1. separate tables for CRM entities
2. post-convert CRM boundary
3. SSR-only expansion
4. fixed lead status pipeline
