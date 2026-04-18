# Lead Discovery CRM MVP

Краткое веб-приложение на **FastAPI** для ручного контура **lead discovery**: черновая очередь кандидатов (CSV), атомарный перевод в CRM-лид, учёт контактов и консультаций. Данные — **SQLite**, интерфейс — **SSR (Jinja2)** с отдельным **JSON API** под префиксом `/api`.

## Для кого (use case)

- Малые команды или один оператор, которым нужен **единый локальный MVP** без SaaS-зависимостей.
- Сценарий: импорт кандидатов → отбор → **convert** в лид → фиксация **попыток контакта** и **консультаций** на карточке лида.

## Основные возможности (MVP scope)

Соответствует текущему коду и зафиксированному baseline (см. `docs/architecture/DOA-ARCH-005.md`, snapshot `docs/implementation_snapshot/DOA-IMP-025.md`):

| Область | Возможности |
|--------|-------------|
| **Candidate Queue** | Импорт CSV, статусы `new` / `rejected` / `converted`, отказ без физического delete |
| **Convert** | Атомарное создание **lead** и обновление кандидата в одной транзакции |
| **Leads** | Список, карточка, заметки, переходы статусов по зафиксированной матрице |
| **CRM layer** | Таблицы `contact_attempts`, `consultations`; сервисы; SSR-формы; JSON API `/api/leads/...`, `/api/consultations/...` |
| **Dashboard** | Агрегированные метрики по лидам (`/dashboard`) |
| **Надёжность SQLite** | WAL, busy timeout, retry на write path |

Вне текущего MVP (не обещается в этом репозитории без нового цикла DocOps): скрейпинг, обогащение, multi-user, внешние интеграции, настраиваемый FSM из конфигов.

## High-level архитектура (модули + pipeline)

**Pipeline:** `candidate (draft)` → **atomic convert** → `lead (CRM)` → `contact_attempts` / `consultations`.

**Модули:**

- **`app/web/`** — SSR-маршруты: `/candidates`, `/leads`, `/dashboard`
- **`app/api/routes/`** — JSON API с префиксом `/api` (в т.ч. CRM)
- **`app/services/`** — бизнес-логика (очередь кандидатов, лиды, CRM `crm_service.py`)
- **`app/db/`** — SQLite: `schema.sql`, `init_db()`, политика записи с retry
- **`app/templates/`**, **`app/static/`** — представление без SPA

Инварианты (как в архитектурном baseline): **candidates ≠ leads**, CRM только после появления `lead_id`, **SSR-first**, статусы заданы в коде, а не внешним конфигом FSM.

**DocOps (DOA / LDC):** изменения ведутся docs-first, create-only; операционная рамка — **LDC-OP-002**. Архитектура и решения в репозитории выражены серией **DOA-*** (например **DOA-ARCH-005**, **DOA-DEC-005**); идентификаторы **LDC-ARCH-001** / **LDC-DEC-*** в операционных документах должны ссылаться на эти артефакты там, где каталог LDC сопоставлен с файлами в `docs/`.

## Quick start

Требования: **Python 3.12** (рекомендуется), см. также `RUN.md`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Точки входа для ручной проверки:

- Главная: http://127.0.0.1:8000/
- Кандидаты: http://127.0.0.1:8000/candidates
- Лиды: http://127.0.0.1:8000/leads
- Дашборд: http://127.0.0.1:8000/dashboard
- Health API: http://127.0.0.1:8000/api/health

База по умолчанию создаётся при старте приложения (каталог `data/`).

## Структура проекта

```
app/
  main.py              # FastAPI app, роутеры, startup → init_db
  api/routes/          # JSON API (/api/...)
  web/routes/          # SSR pages
  services/            # Доменная логика
  db/                  # SQLite schema + connection helpers
  templates/           # Jinja2
  static/
data/                  # SQLite DB file (gitignored — не коммитить прод-данные)
docs/                  # DocOps: ideas, architecture, decisions, operations, IMP/VAL/AUD
requirements.txt
RUN.md
```

## Roadmap

| Версия | Фокус (ориентир, не контракт) |
|--------|-------------------------------|
| **v0.1** | Текущий MVP: candidate queue → lead → contacts → consultations; SSR + `/api` CRM; SQLite hardened writes |
| **v0.2** | Качество и сопровождение: тесты API/SSR, ужесточение валидации, выравнивание DocOps-путей в `docs/`, при необходимости — расширенный аудит JSON CRM |
| **v0.3** | Возможное развитие продукта **только после discussion-first** (новый IDEA): обогащение, отчёты, интеграции — вне текущего LDC-OP-002 без отдельного цикла |

---

*Подготовка репозитория к публикации выполнена в рамках **LDC-OP-002**; существующие файлы в `docs/` не изменялись.*
