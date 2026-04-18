# DOA-IDEA-005 — CRM Layer Expansion (Lead Management & Interaction Tracking)

## Metadata

- id: DOA-IDEA-005
- type: IDEA
- parent: DOA-FSN-002
- status: draft
- date: 2026-04-18

---

## Context

Система находится в состоянии завершённого lifecycle DOA-OP-005.

Текущий product baseline:

- Candidate Queue (draft layer перед CRM)
- Хранение candidates (SQLite)
- CSV import с fail-fast валидацией
- reject (без удаления)
- convert (atomic):
  - создание lead
  - обновление candidate
  - одна транзакция
- SSR UI:
  - /candidates
  - действия reject / convert
- SQLite write path защищён (retry / busy handling)

Candidate Queue является точкой входа в CRM.

---

## Problem

Текущая система покрывает только этап:

candidate → lead

После создания lead отсутствует:

- управление лидами
- фиксация коммуникации
- отслеживание статусов
- управление консультациями
- видимость воронки

Система не реализует CRM-часть MVP.

---

## Goal

Расширить систему до полноценного CRM MVP:

- управление leads
- фиксация контактов (contact attempts)
- отслеживание статусов
- управление консультациями
- базовая аналитика

---

## Scope (High-Level)

Добавить поверх текущего baseline:

### 1. Lead Management
- список leads (/leads)
- карточка lead
- обновление статуса
- заметки

### 2. Contact Log
- фиксация попыток контакта
- outcome + next_action
- история взаимодействия

### 3. Consultation Tracking
- планирование консультаций
- статус (planned / done / cancelled)
- результат

### 4. Status Pipeline
- new → reviewed → contacted → replied → consultation → converted / rejected

### 5. UI (SSR)
- /leads
- /leads/{id}
- формы добавления контактов
- отображение истории

---

## Constraints

НЕЛЬЗЯ нарушать:

- candidates ≠ leads
- atomic convert
- SQLite write policy
- SSR-first UI
- create-only DocOps

---

## Expected Outcome

После реализации:

- система покрывает полный цикл:
  candidate → lead → contact → consultation → result

- пользователь может:
  - управлять лидами
  - вести коммуникацию
  - отслеживать статус
  - фиксировать результат

---

## Next Step

→ DOA-ARCH-005 (архитектура CRM слоя)
