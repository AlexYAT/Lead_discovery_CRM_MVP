## Metadata
- Project: DOA
- Doc type: operational_plan
- ID: DOA-OP-001
- Status: accepted
- Date: 2026-04-17
- Parent: DOA-DEC-001
- Tags: [lead-discovery, crm, mvp, op, execution-plan]

# Summary
Документ задает операционный план реализации MVP после фиксации архитектурных решений и определяет
минимальные исполнимые шаги до перехода к implementation snapshot.

# Goal
- довести MVP до состояния, соответствующего Definition of Done;
- сохранить минимальную сложность решения;
- реализовать ручной lead workflow без выхода за границы MVP.

# Scope of Execution
## Включено в выполнение
- backend skeleton;
- storage schema;
- lead management;
- contact log;
- consultation management;
- dashboard metrics;
- persistence check.

## Не включено в выполнение
- auto messaging;
- AI layer;
- complex integrations;
- source connectors.

# Execution Strategy
Реализация выполняется последовательными минимальными блоками T01-T07. Каждый блок завершается
проверяемым deliverable и служит основанием для следующего.

## T01 - Project skeleton
- базовая структура приложения;
- FastAPI app;
- SSR UI skeleton;
- базовые каталоги.

Deliverable:
- репозиторная структура MVP и рабочий каркас backend/UI, пригодный для последующего наполнения.

## T02 - Storage and domain schema
- SQLite schema;
- таблицы Lead / Contact Attempt / Consultation;
- базовые связи и миграционный/инициализационный подход MVP.

Deliverable:
- инициализированное хранилище SQLite с доменной схемой и воспроизводимым способом первичного развёртывания.

## T03 - Lead CRM
- создание лида;
- список лидов;
- карточка лида;
- обновление статуса;
- заметки.

Deliverable:
- модуль Lead CRM, покрывающий полный базовый цикл работы с лидом в рамках ручного сценария.

## T04 - Contact Log
- добавление попытки контакта;
- история взаимодействий;
- outcome / next_action.

Deliverable:
- журнал коммуникаций, связанный с лидом и поддерживающий фиксацию результата и следующего шага.

## T05 - Consultation Management
- создание консультации;
- обновление статуса консультации;
- отображение в карточке лида.

Deliverable:
- отдельный контур управления консультациями, связанный с лидом и отражаемый в интерфейсе.

## T06 - Dashboard
- counts;
- статусные агрегаты;
- базовые conversion metrics.

Deliverable:
- dashboard с ключевыми количественными показателями воронки и базовой конверсионной аналитикой.

## T07 - Persistence and MVP verification
- проверка сохранности после перезапуска;
- ручная верификация DoD;
- подготовка к IMP.

Deliverable:
- подтверждение устойчивости данных и комплект результатов ручной проверки готовности MVP к snapshot.

# Deliverables
- T01: каркас приложения и базовая структура каталогов.
- T02: SQLite-схема и воспроизводимая инициализация.
- T03: рабочий модуль Lead CRM.
- T04: рабочий модуль Contact Log.
- T05: рабочий модуль Consultation Management.
- T06: рабочий модуль Dashboard.
- T07: подтвержденная persistence-проверка и итоговая верификация DoD.

# Definition of Done for execution
OP считается выполненным, если:
- все этапы T01-T07 завершены;
- MVP соответствует исходному Definition of Done;
- подтверждена готовность к формированию implementation snapshot.

# Risks and Controls
- Риск: переусложнение MVP.  
  Контроль: жёстко ограничивать реализацию рамками T01-T07 и out-of-scope ограничениями.
- Риск: нарушение create-only в документации.  
  Контроль: фиксировать новые артефакты только через создание новых документов без правки истории.
- Риск: расползание scope.  
  Контроль: отклонять задачи вне зафиксированного Scope of Execution.
- Риск: неполное покрытие status flow.  
  Контроль: проверять соответствие реализации утвержденной FSM-модели и сценариям верификации.

# Next Steps
- выполнение задач только в рамках данного OP;
- по завершении T01-T07 перейти к этапу IMP и зафиксировать implementation snapshot.
