# DOA-IMP-023 — CRM API Layer

## Metadata

- id: DOA-IMP-023
- type: IMP
- parent: DOA-OP-006
- status: completed
- date: 2026-04-18

---

## Scope

Реализация API layer для CRM:

- contact_attempts
- consultations

---

## Changes

Созданы / изменены файлы API layer для маршрутов CRM:

- app/api/routes/crm.py (новый роутер, префикс `/api`, тег `CRM API`)
- app/main.py (подключение `crm_api_router`)

Для PATCH-эндпоинта без дублирования SQL в route layer в `app/services/crm_service.py` добавлена read-only функция `get_consultation` (проверка существования записи, те же поля, что у списка).

Использованы сервисы:

- create_contact_attempt
- list_contact_attempts
- create_consultation
- list_consultations
- update_consultation_status
- get_consultation (read-only, для 404)

---

## Endpoints

В кодовой базе JSON-API живёт под префиксом `/api` (как `/api/health`). Добавлены:

- POST `/api/leads/{lead_id}/contact`
- GET `/api/leads/{lead_id}/contacts`
- POST `/api/leads/{lead_id}/consultations`
- GET `/api/leads/{lead_id}/consultations`
- PATCH `/api/consultations/{consultation_id}`

Логические пути из DOA-OP-006 (`/leads/{id}/…`, `/consultations/{id}`) соответствуют этим маршрутам с префиксом `/api`, чтобы не пересекаться с SSR (`/leads/…` без `/api`).

---

## Constraints Compliance

Проверено:

- convert flow не изменён
- candidate queue не затронут
- router structure сохранена (отдельный модуль в `app/api/routes/`, подключение в `main.py` рядом с `base_router`)
- baseline SSR endpoints (`/leads`, `/candidates`, …) не сломаны

---

## Result

- CRM API layer реализован
- готово для следующего шага (SSR UI)
