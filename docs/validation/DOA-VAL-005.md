# DOA-VAL-005 — CRM Layer Validation

## Metadata

- id: DOA-VAL-005
- type: VAL
- parent: DOA-OP-006
- status: completed
- date: 2026-04-18

---

## Scope

Проверка CRM layer:

- DB schema
- service layer
- API layer
- SSR UI

---

## Checks

### V01 — Candidate → Lead convert

Результат: PASS  
Комментарий: Выполнено через SSR-эквивалент: `POST /candidates/import` (CSV с заголовком и одной строкой, `follow_redirects=false` → 303 на `/candidates`), затем `POST /candidates/{id}/convert` → 303, `Location` содержит `/leads/{lead_id}`. Проверено в БД/сервисах: `get_lead(lead_id)` не `None`, у кандидата `status=converted`, `lead_id` совпадает с созданным lead.

---

### V02 — Contact attempt creation

Результат: PASS  
Комментарий: `POST /leads/{lead_id}/contacts` с полями date, message_text, outcome, next_action → 303. `list_contact_attempts(lead_id)` содержит запись с ожидаемым `message_text`; поле `created_at` присутствует и не пустое.

---

### V03 — Consultation creation

Результат: PASS  
Комментарий: `POST /leads/{lead_id}/consultations` (planned_at, status=planned, пустой result) → 303. `list_consultations(lead_id)` содержит запись со статусом `planned`; `created_at` присутствует.

---

### V04 — Consultation update

Результат: PASS  
Комментарий: `POST /leads/{lead_id}/consultations/{id}` (SSR-форма обновления) со status=`completed`, result=`Done` → 303. `get_consultation(id)` возвращает `status=completed`, `result=Done` (данные не обнулись).

---

### V05 — Data consistency

Результат: PASS  
Комментарий: После второй попытки контакта (`message_text=second`) повторный вызов `list_contact_attempts(lead_id)` показывает последнюю запись первой в списке (сортировка «новые сверху» по `created_at`, как в `crm_service`).

---

### V06 — Regression (candidates flow)

Результат: PASS  
Комментарий: `GET /candidates` и `GET /leads` → 200. Импорт CSV (как в V01) отрабатывает. `POST /candidates/{id}/reject` для отдельного кандидата в статусе `new` → 303; `get_candidate` показывает `rejected`. Convert flow кода не менялся; проверка только наблюдением поведения.

---

### V07 — Server stability

Результат: PASS  
Комментарий: `TestClient(app)` поднимает приложение со `startup` (`init_db`); цепочка запросов из V01–V06 завершилась без исключений и без ошибок SQLite в консоли сценария. Дополнительный smoke: `GET /api/health` → JSON `status: ok`. Отдельный длительный ручной запуск `uvicorn` вне TestClient в этой сессии не требовался.

---

## Summary

Общий статус:

- PASSED

Краткий вывод:

Полный сценарий candidate → lead (import + convert) → contact attempt (SSR POST) → consultation create/update → повторная сортировка контактов и регрессия candidates/leads SSR прошли автоматизированной проверкой без изменений кода. CRM JSON-эндпоинты (IMP-023) в этом прогоне не прогонялись полным CRUD-циклом через HTTP; выполнен только smoke `/api/health`. При необходимости явной API-only проверки — отдельный VAL или чеклист.

---

## Notes

- Проверки выполнены **без правок исходного кода** приложения; использованы `starlette.testclient.TestClient`, реальная SQLite БД проекта и сервисы чтения для верификации состояния.
- Для POST-запросов с редиректом использовано `follow_redirects=false`, иначе `TestClient` возвращает финальный **200** после перехода на `/leads/{id}`, что не следует путать с ошибкой convert.
- Ранние отчёты VAL в репозитории лежат в `docs/validation_reports/`; данный документ размещён в **`docs/validation/`** согласно формулировке Step 5 DOA-OP-006.

---

## Next Step

→ DOA-AUD-003 (или snapshot, если система стабильна)
