# DOA-IMP-025 — Final Snapshot of OP-006 CRM Layer Lifecycle

## Metadata

- id: DOA-IMP-025
- type: IMP
- parent: DOA-AUD-003
- status: completed
- date: 2026-04-18

---

## Scope

Финальный агрегированный snapshot завершённого lifecycle OP-006:

- CRM layer over Candidate Queue baseline

---

## Lifecycle Closed

### Idea
- DOA-IDEA-005 — CRM Layer Expansion

### Architecture
- DOA-ARCH-005 — CRM Layer Architecture over Candidate Queue Baseline

### Decision
- DOA-DEC-005 — CRM Layer Decisions over Candidate Queue Baseline

### Operational Plan
- DOA-OP-006 — CRM Layer Implementation Plan

### Implementation
- DOA-IMP-021 — CRM DB Schema
- DOA-IMP-022 — CRM Service Layer
- DOA-IMP-023 — CRM API Layer
- DOA-IMP-024 — CRM SSR UI

### Validation
- DOA-VAL-005 — PASSED

### Audit
- DOA-AUD-003 — PASSED

---

## Baseline Before OP-006

До начала OP-006 система уже поддерживала:

- Candidate Queue
- CSV import
- reject without delete
- atomic convert candidate → lead
- SSR UI for /candidates
- SQLite hardened write policy

Этот baseline сохранён.

---

## What Was Added in OP-006

### 1. CRM Storage
Добавлены CRM-таблицы:

- contact_attempts
- consultations

С совместимой idempotent migration logic для существующих БД.

### 2. CRM Service Layer
Добавлены сервисы для:

- create/list contact attempts
- create/list consultations
- update consultation status
- read consultation for SSR/API flows

### 3. CRM API Layer
Добавлены JSON API маршруты под `/api`:

- POST `/api/leads/{lead_id}/contact`
- GET `/api/leads/{lead_id}/contacts`
- POST `/api/leads/{lead_id}/consultations`
- GET `/api/leads/{lead_id}/consultations`
- PATCH `/api/consultations/{consultation_id}`

### 4. CRM SSR UI
Расширен SSR слой:

- /leads
- /leads/{id}

Поддержано:

- список лидов
- карточка лида
- contact attempts history
- consultations history
- SSR формы создания и обновления

---

## Architectural Invariants Preserved

Подтверждено:

- candidates ≠ leads
- CRM начинается только после convert
- convert остаётся atomic
- SQLite write policy сохранена
- /candidates flow не нарушен
- UI remains SSR-first
- configurable FSM не введён

---

## Validation and Audit Result

### Validation
DOA-VAL-005 → PASSED

Подтверждено:

- import candidate
- convert candidate → lead
- create contact attempt
- create consultation
- update consultation
- sorting consistency
- regression check for candidates flow

### Audit
DOA-AUD-003 → PASSED

Подтверждено:

- lifecycle completeness
- baseline compatibility
- storage compliance
- boundary compliance
- UI compliance
- status model compliance
- OP execution traceability
- validation sufficiency

---

## Current Product State

Система теперь поддерживает полный MVP flow:

candidate → lead → contact attempt → consultation → result

Текущее состояние:

- Candidate Queue baseline
- CRM lead management layer
- contact logging
- consultation tracking
- SSR UI
- JSON API for CRM
- validation passed
- audit passed

---

## Known Limitations

Вне текущего baseline остаются:

- full CRUD audit for JSON CRM API
- batch convert
- enrichment
- scraping
- analytics expansion
- multi-user
- configurable FSM
- external integrations

Также в репозитории сохраняется частичная неоднородность путей DocOps-артефактов:

- docs/decision_log vs docs/decisions
- docs/operational_plan vs docs/operations
- docs/validation_reports vs docs/validation

Это не блокирует baseline, но может быть вынесено в отдельный alignment lifecycle.

---

## Rule for Next Lifecycle

Следующий lifecycle НЕ запускать автоматически через новый IDEA document.

Сначала требуется chat-level discussion:

- обсудить направление следующей реализации
- определить product priority
- выделить точки выбора
- только после этого формировать следующий IDEA

---

## Result

OP-006 lifecycle завершён полностью.

CRM layer становится новым product baseline поверх Candidate Queue architecture.

Документ может использоваться как source of truth для перехода в новый чат.
