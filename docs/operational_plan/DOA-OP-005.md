## Metadata
- Project: DOA
- Doc type: operational_plan
- ID: DOA-OP-005
- Status: accepted
- Date: 2026-04-18
- Parent: [DOA-DEC-004](../decision_log/DOA-DEC-004.md)
- Lifecycle: [DOA-IDEA-004](../ideas/DOA-IDEA-004.md) → [DOA-ARCH-004](../architecture/DOA-ARCH-004.md) → [DOA-DEC-004](../decision_log/DOA-DEC-004.md) → **DOA-OP-005** → IMP / VAL / snapshot
- Tags: [lead-discovery, crm, mvp, candidate-queue, curated-inbound, op, mvp-iteration-1]

# Summary

Операционный план **первой MVP-итерации** слоя **candidate queue / curated inbound draft**: отдельная таблица и сервисы, импорт одного простого формата, минимальный SSR UI, действия **reject** и **одиночный convert → lead** с traceability и статусом **`converted`**, без изменения принятых решений [DOA-DEC-004](../decision_log/DOA-DEC-004.md) и без расширения scope за пределы DEC.

# Goal

- Добавить **слой candidates до CRM**, не смешивая его с `leads`.
- Обеспечить **импорт** кандидатов в очередь.
- Дать возможность **ручного reject** без физического удаления записи.
- Дать возможность **одиночного** convert в lead с фиксацией связи и терминальным статусом **`converted`**.
- **Не ломать** текущий CRM flow (лиды, статусы FSM, контакты, консультации, dashboard) после появления лида из convert.

# Scope

Включить только минимально необходимое:

- изменения схемы **SQLite** для таблицы `candidates` (отдельно от `leads`);
- **domain/service layer** для CRUD очереди, reject, convert (согласно DEC);
- **import** одного простого формата (например CSV с фиксированным набором колонок — уточнить в T03, не расширять без нового DEC);
- минимальный **SSR UI**: список candidates, действия reject / convert, базовая навигация к существующему `/leads/{id}` после конверсии;
- **traceability** candidate ↔ lead (`lead_id` на candidate; при необходимости ссылка на candidate с лида — в рамках T02/T04 без нарушения отдельности таблиц);
- артефакты: **implementation snapshots**, **validation report**, при необходимости **короткий audit** touchpoints и **runbook** ручной проверки импорта.

# Out of scope

- **Batch convert**, scraping, auto discovery, enrichment (явно вне DEC-004).
- **Multi-user**, роли, авторизация сверх текущего MVP.
- Переделка текущей **lead FSM** или объединение сущностей.
- Сложная аналитика / отчёты по воронке для candidates.
- Массовый импорт без явного сценария в T03 (не расширять форматы без нового цикла).

# Work breakdown (T01–T07)

## T01 — Schema & audit of integration points

- **Цель:** зафиксировать точки касания с БД, роутингом и шаблонами; спроектировать миграцию `candidates` без регрессии `leads`.
- **Артефакты:** при необходимости **DOA-AUD-xxx** или раздел в **DOA-IMP-0xx** (touchpoints, список файлов для изменения в следующих T).

## T02 — Candidate model / storage

- **Цель:** таблица `candidates` по DEC (поля: id, platform, profile_name, profile_url, notes, status lifecycle, `lead_id` nullable, timestamps по согласованию); инициализация через существующий паттерн `init_db` / schema.sql.
- **Артефакты:** **DOA-IMP-0xx** (снимок после T02).

## T03 — Import path (один простой формат)

- **Цель:** один канал импорта (например CSV: `platform,profile_name,profile_url[,notes]`); валидация строк; создание candidates со статусом `new`; отказ при невалидных обязательных полях.
- **Артефакты:** **DOA-IMP-0xx**; опционально **DOA-RUN-xxx** для ручного прогона импорта.

## T04 — Reject / convert domain logic

- **Цель:** операции reject (переход в `rejected`, без DELETE); convert одиночный: создание lead, установка `lead_id`, статус candidate → **`converted`**; запрет повторного convert; транзакции согласованы с SQLite hardening (short writes, retry где уместно).
- **Артефакты:** **DOA-IMP-0xx**.

## T05 — SSR UI for candidate queue

- **Цель:** маршруты отдельно от `/leads` (например `/candidates`): список, фильтр по статусу (минимум), форма импорта, кнопки reject / convert; после convert — редирект на существующую карточку лида.
- **Артефакты:** **DOA-IMP-0xx**.

## T06 — Validation

- **Цель:** сценарии: импорт → reject остаётся в БД → convert → проверка `converted` и `lead_id`; регрессия CRM на созданном lead.
- **Артефакты:** **DOA-VAL-xxx** (accepted при успешном прогоне).

## T07 — Final implementation snapshot

- **Цель:** закрыть цикл OP-005 одним **final IMP** с перечнем изменений, ограничений и ссылкой на VAL.
- **Артефакты:** **DOA-IMP-0xx** (final).

*(Номера IMP/VAL/AUD/RUN — назначить следующими свободными при исполнении; не создавать заглушки в этом документе.)*

# Deliverables

| Тип | Ожидание |
|-----|----------|
| **IMP** | Промежуточные снимки по T02–T05 и финальный по T07 |
| **VAL** | Один validation report по T06 |
| **AUD** | Опционально по T01, если фиксируется отдельный аудит |
| **RUN** | Опционально runbook для импорта/двухшаговой проверки |

# Definition of Done

Цикл **DOA-OP-005** считается завершённым, если:

- сущность **candidates** существует **отдельно** от `leads` (отдельная таблица);
- **import** работает для **одного** согласованного в реализации формата;
- candidate можно **отклонить** без физического удаления (статус в lifecycle);
- candidate можно **одиночно** конвертировать в lead;
- после конверсии зафиксированы **связь candidate ↔ lead** и статус candidate **`converted`**;
- текущий **CRM flow** после создания лида **не ломается**;
- создан **validation report** (VAL);
- создан **final implementation snapshot** (IMP).

# Risks

| Риск | Контроль |
|------|----------|
| Дубли по `profile_url` | Предупреждение или мягкая блокировка на convert (DEC/implementation); не скрывать дубль без явного UX. |
| Путаница candidate vs lead в UI | Отдельные пути `/candidates` vs `/leads`; явные подписи в шаблонах. |
| Частичная конверсия без связи | Одна транзакция convert или компенсирующий rollback; проверка в VAL. |
| Расползание scope | Любое отклонение от DEC — только новый DocOps-цикл. |

# Execution note

Настоящий OP **строго следует** [DOA-DEC-004](../decision_log/DOA-DEC-004.md): отдельная таблица, lifecycle для rejected, только одиночный convert, терминальный **`converted`**, внешние запреты из DEC не пересматриваются в рамках исполнения OP-005. Изменение решений — только через новый **IDEA/ARCH/DEC**, не через «уточнения» в коде без документа.

# Next steps

- Исполнение T01–T07 в границах scope/out of scope настоящего плана;
- после T07 — новый lifecycle (расширение import, batch и т.д.) только отдельной цепочкой DocOps.
