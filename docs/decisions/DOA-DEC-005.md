# DOA-DEC-005 — CRM Layer Decisions over Candidate Queue Baseline

## Metadata

- id: DOA-DEC-005
- type: DEC
- parent: DOA-ARCH-005
- status: accepted
- date: 2026-04-18

---

## Context

В рамках DOA-IDEA-005 и DOA-ARCH-005 был определён следующий шаг развития системы:

построение CRM layer поверх уже существующего Candidate Queue baseline.

На момент принятия решения система уже поддерживает:

- Candidate Queue как pre-CRM layer
- CSV import
- reject без delete
- atomic convert из candidate в lead
- SSR UI для /candidates
- SQLite hardened write policy

Необходимо зафиксировать архитектурные выборы для следующего lifecycle реализации CRM-слоя.

---

## Decision 1 — Separate Tables for CRM Entities

Принято решение использовать отдельные таблицы для CRM-сущностей.

Подход:

- leads остаётся root CRM entity
- contact_attempts вводится как отдельная таблица
- consultations вводится как отдельная таблица

Обоснование:

- нормализованная структура хранения
- удобная SQL-фильтрация и история
- совместимость с будущей аналитикой
- отказ от JSON-overloading внутри leads

Следствие:

- CRM данные не хранятся вложенно в leads как JSON blob
- история коммуникаций и консультаций моделируется как отдельные связанные записи

---

## Decision 2 — Post-Convert CRM Boundary

Принято решение, что CRM начинается только после convert:

candidate → lead → CRM flow

Обоснование:

- сохраняется жёсткая граница candidate и lead
- не нарушается существующий baseline Candidate Queue
- convert остаётся единственной архитектурной точкой входа в CRM

Следствие:

- никакие CRM-операции не выполняются над candidate
- contact attempts и consultations разрешены только для lead

---

## Decision 3 — SSR-Only UI Expansion

Принято решение расширять UI только в рамках SSR-first архитектуры.

Подход:

- добавляются SSR страницы:
  - /leads
  - /leads/{id}

Обоснование:

- совместимость с существующим UI baseline
- минимизация архитектурного риска
- отсутствие необходимости вводить SPA/frontend framework на этапе MVP

Следствие:

- отдельный SPA frontend не вводится
- CRM UI развивается как часть текущего SSR слоя

---

## Decision 4 — Fixed Lead Status Pipeline

Принято решение использовать фиксированный pipeline статусов для leads:

- new
- reviewed
- contacted
- replied
- consultation_booked
- converted
- not_interested

Обоснование:

- простота MVP
- предсказуемое поведение service/UI слоя
- отсутствие необходимости configurable FSM на текущем этапе

Следствие:

- динамическая конфигурация pipeline не вводится
- FSM expansion считается out of scope для данного lifecycle

---

## Compatibility Constraints

Настоящее решение не должно нарушать текущий baseline:

- candidates ≠ leads
- candidate queue остаётся отдельным pre-CRM слоем
- reject остаётся status-based и без delete
- convert остаётся atomic
- /candidates SSR flow сохраняется
- SQLite write policy сохраняется без ослабления

---

## Alternatives Considered

### Alternative A — JSON storage inside leads
Отклонено:
- ухудшает SQL access
- мешает аналитике
- размывает границы CRM model

### Alternative B — CRM actions on candidates
Отклонено:
- нарушает boundary candidate vs lead
- усложняет lifecycle

### Alternative C — SPA frontend
Отклонено:
- не соответствует SSR baseline
- избыточно для MVP

### Alternative D — Configurable FSM
Отклонено:
- преждевременная сложность
- не требуется для MVP

---

## Result

Следующий lifecycle реализации CRM-слоя должен строиться на следующих обязательных принципах:

1. separate tables for CRM entities
2. CRM starts only after convert to lead
3. UI expands only via SSR
4. lead statuses remain fixed

---

## Next Step

Следующий шаг:

DOA-OP-006

Operational plan должен декомпозировать реализацию CRM layer на исполнимые шаги без нарушения baseline.
