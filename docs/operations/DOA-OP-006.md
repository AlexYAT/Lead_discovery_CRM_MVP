# DOA-OP-006 — CRM Layer Implementation Plan

## Metadata

- id: DOA-OP-006
- type: OP
- parent: DOA-DEC-005
- status: planned
- date: 2026-04-18

---

## Context

Настоящий план описывает реализацию CRM layer поверх Candidate Queue baseline.

Архитектура зафиксирована в DOA-ARCH-005.  
Решения зафиксированы в DOA-DEC-005.

Baseline не должен быть нарушен:

- candidates ≠ leads
- atomic convert сохраняется
- SQLite write policy сохраняется
- SSR /candidates остаётся без изменений

---

## Execution Strategy

Реализация выполняется:

- по слоям (layer-based)
- в порядке storage → services → API → UI
- с фиксацией результата через отдельные implementation snapshots

---

## Execution Plan

### Step 1 — DB Schema (IMP-021)

Цель:

Добавить таблицы CRM слоя:

- contact_attempts
- consultations

Требования:

- foreign key → leads.id
- created_at обязательный
- минимально необходимые поля из ARCH-005

Ограничения:

- не менять существующие таблицы
- не ломать init_db (idempotent)

Результат:

- схема БД обновлена
- система запускается без ошибок

---

### Step 2 — Service Layer (IMP-022)

Цель:

Реализовать сервисы:

- create_contact_attempt
- list_contact_attempts
- create_consultation
- list_consultations
- update_consultation_status

Требования:

- использовать существующую write policy (retry)
- не менять convert flow
- работать только с lead_id

---

### Step 3 — API Layer (IMP-023)

Цель:

Добавить API маршруты:

- POST /leads/{id}/contact
- GET /leads/{id}/contacts
- POST /leads/{id}/consultations
- GET /leads/{id}/consultations
- PATCH /consultations/{id}

Требования:

- не ломать существующие endpoints
- следовать текущей структуре router

---

### Step 4 — SSR UI (IMP-024)

Цель:

Добавить UI страницы:

- /leads
- /leads/{id}

Функциональность:

- список leads
- карточка lead
- отображение contact history
- отображение consultations
- формы добавления записей

Ограничения:

- SSR-only
- не вводить SPA

---

### Step 5 — Validation (VAL-005)

Цель:

Проверить:

- корректность CRUD
- корректность связей lead → contact / consultation
- отсутствие регрессий в /candidates
- стабильность convert

---

## Implementation Order

1. IMP-021 — DB
2. IMP-022 — services
3. IMP-023 — API
4. IMP-024 — UI
5. VAL-005

---

## Expected Result

После выполнения OP-006 система должна поддерживать:

candidate → lead → contact → consultation → result

С сохранением полной совместимости с baseline.

---

## Next Step

→ DOA-IMP-021

Начать с DB schema.
