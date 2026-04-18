# DOA-IMP-021 — CRM DB Schema (contact_attempts, consultations)

## Metadata

- id: DOA-IMP-021
- type: IMP
- parent: DOA-OP-006
- status: completed
- date: 2026-04-18

---

## Scope

Реализация DB schema для CRM layer:

- contact_attempts
- consultations

---

## Changes

Изменён:

- app/db/database.py
- app/db/schema.sql

Добавлено / зафиксировано:

- CREATE TABLE IF NOT EXISTS contact_attempts (DDL в schema.sql; колонка created_at по IMP-021)
- CREATE TABLE IF NOT EXISTS consultations (DDL в schema.sql; колонка created_at по IMP-021)
- идемпотентное дополнение колонки created_at для уже существующих БД в init_db() (константный DEFAULT в ALTER + backfill, т.к. SQLite не принимает CURRENT_TIMESTAMP в ADD COLUMN)

---

## Details

### contact_attempts

- привязка к lead_id
- хранение истории коммуникации
- created_at обязателен (DEFAULT CURRENT_TIMESTAMP)

### consultations

- привязка к lead_id
- planned_at + status
- хранение результата
- created_at обязателен (DEFAULT CURRENT_TIMESTAMP)

---

## Constraints Compliance

Проверено:

- существующие таблицы leads и candidates не изменены по смыслу (только расширение CRM-таблиц и миграция колонок)
- init_db остаётся idempotent
- convert flow не затронут
- candidate queue не затронут

---

## Result

- схема БД расширена
- система запускается без ошибок
- готово для следующего шага (service layer)
