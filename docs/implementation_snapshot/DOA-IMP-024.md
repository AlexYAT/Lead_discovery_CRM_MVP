# DOA-IMP-024 — CRM SSR UI

## Metadata

- id: DOA-IMP-024
- type: IMP
- parent: DOA-OP-006
- status: completed
- date: 2026-04-18

---

## Scope

Реализация SSR UI для CRM layer:

- /leads
- /leads/{id}

---

## Changes

Созданы / изменены SSR routes и templates для CRM UI.

Функциональность:

- список leads
- lead detail page
- отображение contact attempts
- отображение consultations
- формы создания contact attempt / consultation
- обновление consultation status

Файлы:

- app/web/routes/leads.py — чтение/запись CRM через `app.services.crm_service` (без HTTP к `/api`)
- app/templates/leads_list.html — навигация (главная, кандидаты, дашборд)
- app/templates/lead_detail.html — навигация; колонки `created_at` в таблицах истории

---

## Constraints Compliance

Проверено:

- SSR-only подход сохранён
- candidate queue не затронут
- convert flow не изменён
- /candidates остаётся рабочим

---

## Result

- CRM SSR UI реализован
- система готова к validation step (VAL-005)
