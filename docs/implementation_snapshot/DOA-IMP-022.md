# DOA-IMP-022 — CRM Service Layer

## Metadata

- id: DOA-IMP-022
- type: IMP
- parent: DOA-OP-006
- status: completed
- date: 2026-04-18

---

## Scope

Реализация service layer для CRM:

- contact_attempts
- consultations

---

## Changes

Создан:

- app/services/crm_service.py

---

## Functions

### contact_attempts

- create_contact_attempt
- list_contact_attempts

### consultations

- create_consultation
- list_consultations
- update_consultation_status

---

## Constraints Compliance

Проверено:

- convert flow не изменён
- candidate queue не затронут
- SQLite write policy сохранена

---

## Result

- CRM service layer реализован
- готово для следующего шага (API layer)
