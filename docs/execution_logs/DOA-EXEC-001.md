# Execution log: DOA-EXEC-001 — Multi-instance run (T02 / DOA-OP-004)

## Document metadata

- **ID:** DOA-EXEC-001
- **Type:** execution_log
- **Status:** draft
- **Date:** 2026-04-18
- **Parent:** [DOA-OP-004](../operational_plan/DOA-OP-004.md)
- **Runbook:** [DOA-RUN-001](../runbooks/DOA-RUN-001.md)
- **Tags:** [lead-discovery, crm, mvp, sqlite, multi-instance, op-004-t02]

## Environment

| Поле | Значение |
|------|----------|
| **Дата/время прогона (фиксация окончания проверок)** | 2026-04-18 00:51:08 +07:00 (локальное время исполнителя) |
| **Python version** | 3.12.10 |
| **DB_PATH (resolved)** | `D:\Work\Lead discovery CRM MVP\Project\data\lead_discovery_crm_mvp.db` |
| **Instance A** | `http://127.0.0.1:8000` — `uvicorn app.main:app --host 127.0.0.1 --port 8000` |
| **Instance B** | `http://127.0.0.1:8001` — `uvicorn app.main:app --host 127.0.0.1 --port 8001` |
| **Рабочий каталог** | `D:\Work\Lead discovery CRM MVP\Project` |
| **Метод исполнения шагов** | HTTP POST/GET эквивалентны полям SSR-форм из [DOA-RUN-001](../runbooks/DOA-RUN-001.md) (`application/x-www-form-urlencoded`, редиректы обрабатывались клиентом). Браузер не использовался; логика запросов соответствует шагам 1–6 runbook. |

Перед прогоном: `init_db()` выполнен; файл БД присутствовал.

---

## Execution steps

| Шаг | Инстанс | Действие (содержательно) | Результат | Комментарий |
|-----|---------|---------------------------|-----------|-------------|
| 1 | **A** | POST `/leads` — platform `multi_instance_test`, profile_name `runbook_t01_exec`, profile_url `https://example.com/p/runbook-t01-exec` | **ok** | Финальный URL после редиректа: `/leads/12` → **`LEAD_ID = 12`**. Первый прогон сценария: извлечение id из URL изначально дало сбой в regex вспомогательного скрипта (исправлено: id взят из финального URL). |
| 2 | **B** | POST `/leads/12/status` — `new_status=reviewed` | **ok** | Редирект на карточку B; статус сменён с `new` на `reviewed`. |
| 3 | **A** | POST `/leads/12/notes` — текст `notes_from_instance_A` | **ok** | HTTP 200, редирект на карточку A. |
| 4 | **B** | POST `/leads/12/contacts` — message `msg_from_B`, outcome `sent`, next_action `wait_reply` | **ok** | HTTP 200. |
| 5 | **A** | POST `/leads/12/consultations` — planned_at `2026-06-01 10:00:00`, status `planned` | **ok** | HTTP 200; в БД появилась строка консультации с **`CONSULTATION_ID = 6`**. |
| 6 | **B** | POST `/leads/12/consultations/<id>` — status `completed`, result `result_from_B` | **ok** (см. ниже) | Автоматическое извлечение `<id>` из HTML в том же скрипте **не сработало** (ошибка шаблона regex в harness, не приложения). Идентификатор подтверждён запросом к SQLite: `id=6`. Выполнен POST на B: `/leads/12/consultations/6` — **ok**, HTTP 200, редирект на `/leads/12`. |

Идентификаторы сценария:

- **`LEAD_ID`:** 12  
- **`CONSULTATION_ID`:** 6  

---

## Observations

| Тема | Наблюдение |
|------|------------|
| **Задержки** | Заметных задержек между шагами не фиксировалось; ответы пришли в пределах ожидания локального вызова. |
| **Retry** | На стороне клиента признаков повторных попыток не видно. Поведение `run_write_with_retry` при отсутствии transient lock не проявляется в HTTP-ответе. |
| **Ошибки SQLite** | В телах успешных ответов и при проверке БД **не** зафиксировано сообщений `database is locked` / `database table is locked`. |
| **Поведение UI (косвенно)** | SSR после POST возвращает редиректы 303→200; HTML карточки с A и B после шагов согласован с ожидаемыми полями (проверка через GET и выборка SQLite). |
| **Логи серверов** | Вывод **uvicorn** в файлы в рамках этого прогона **не** перенаправлялся; наблюдение за ошибками SQLite опиралось на отсутствие 500 при шагах и на консистентность данных в БД. |

### Контроль согласованности данных (SQLite после завершения шага 6)

```
leads (id=12): status=reviewed, notes содержат notes_from_instance_A
contact_attempts: сообщение msg_from_B для lead_id=12
consultations (id=6): status=completed, result=result_from_B
```

---

## Logs

**Клиентский прогон (сводка stdout скрипта):**

- После исправления извлечения `LEAD_ID`: шаги 1–5 вернули **HTTP 200** на финальные GET после редиректов; ошибок в выводе клиента нет.
- На этапе автоматического разбора HTML для шага 6 список id оказался пустым из-за ошибки в regex harness → выполнен **ручной** уточняющий POST с `consultation_id=6` (см. шаг 6 выше).

**Выдержки:** полных traceback или строк `database is locked` в логах **не** получено (логи uvicorn не собирались).

---

## Intermediate verdict

**partial**

**Обоснование:** с точки зрения **приложения и общей БД** все шесть операций runbook выполнены успешно, данные согласованы, блокировок SQLite на наблюдаемом пути не проявлено. С точки зрения **строго автоматизированного** прохождения без вмешательства шаг 6 потребовал подстановки `CONSULTATION_ID` из прямой проверки БД из-за дефекта вспомогательного парсера HTML (не runbook и не продукт).

Итоговое решение о приёмке цикла — в отдельном **DOA-VAL-003** (планируемый validation report по OP-004).

---

## Подготовка данных для validation report

- Зафиксировать в VAL: метод исполнения (HTTP-эквивалент runbook), порты 8000/8001, `LEAD_ID=12`, `CONSULTATION_ID=6`, **intermediate verdict = partial** с разделением «продукт ok» vs «harness шаг 6».
- Указать ограничение: **логи uvicorn в файл не писались** — при необходимости повторить прогон со сбором stdout/stderr обоих процессов для VAL.
