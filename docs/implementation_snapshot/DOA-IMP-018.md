## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-018
- Status: accepted
- Date: 2026-04-18
- Parent: [DOA-OP-005](../operational_plan/DOA-OP-005.md)
- Tags: [lead-discovery, crm, mvp, imp, candidate-queue, t04, reject, convert]

# Summary

Документ фиксирует выполнение **T04** из [DOA-OP-005](../operational_plan/DOA-OP-005.md): доменная логика **reject** и **convert** для `candidates` по [DOA-DEC-004](../decision_log/DOA-DEC-004.md), без SSR UI и без изменений import/FSM lead.

# Изменённые файлы

- `app/services/candidate_service.py`
- `app/services/__init__.py`
- `docs/implementation_snapshot/DOA-IMP-018.md` (настоящий снимок)

# Добавленные функции и исключения

| Элемент | Назначение |
|---------|------------|
| `CandidateNotFoundError` | Нет строки candidate по `id` |
| `CandidateStateError` | Недопустимый переход / повторная операция |
| `reject_candidate(candidate_id)` | `new`→`rejected`; повторный `rejected` — **no-op**; `converted` — ошибка |
| `convert_candidate_to_lead(candidate_id) -> int` | Только из `new`; INSERT `leads` + UPDATE candidate `lead_id` + `converted`; возврат `lead_id` |

Константы статусов очереди: `rejected`, `converted` (рядом с `new` в коде).

# Стратегия повторных и недопустимых переходов

- **reject:** из `new` → `rejected`. Повторный вызов при уже **`rejected`** — **no-op** (идемпотентность). При **`converted`** — `CandidateStateError` («нельзя отклонить уже конвертированного»).
- **convert:** только из **`new`**. При **`rejected`** или **`converted`** — `CandidateStateError` (в т.ч. повторный convert = уже `converted`).
- Иные статусы (если появятся позже) — `CandidateStateError` на reject/convert.

# Атомарность convert

Одна операция `run_write_with_retry` → один `with get_connection()` → один вложенный **`with connection:`**, внутри которого последовательно:

1. `SELECT` candidate (проверка статуса `new`);
2. `INSERT INTO leads` с тем же набором полей/семантикой, что и у `create_lead` для пустых опциональных полей и `notes` из candidate;
3. `UPDATE candidates SET lead_id=?, status='converted', … WHERE id=? AND status='new'`; если `rowcount != 1` — `CandidateStateError` (и **rollback** всей транзакции, в т.ч. INSERT lead — orphan lead не остаётся).

Публичный `create_lead` не вызывается, чтобы не открывать второе соединение; логика вставки lead **совпадает** с продуктовой (без изменения FSM старта `new`).

# Проверки (минимальные)

- `reject` на `new` → `rejected`, строка в БД сохраняется.
- Повторный `reject` на `rejected` — no-op.
- `convert` на `new` → lead создан, candidate `converted` и `lead_id` установлен.
- Повторный `convert` — `CandidateStateError`.
- `convert` после `rejected` — `CandidateStateError`.
- `reject` после `converted` — `CandidateStateError`.
- `from app.main import app` — успешно.

# Что не входит в T04

- SSR UI очереди (T05);
- доработки CSV import (T03 закрыт);
- batch convert, enrichment, scraping.
