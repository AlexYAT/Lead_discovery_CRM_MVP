## Metadata
- Project: DOA
- Doc type: operational_plan
- ID: DOA-OP-002
- Status: accepted
- Date: 2026-04-17
- Parent: DOA-DEC-002
- Tags: [lead-discovery, crm, mvp, validation-cycle, op, human-validation]

# Summary
Документ задаёт операционный план validation-cycle до начала реальной UX-проверки человеком.

# Goal
- подготовить воспроизводимое окружение;
- зафиксировать установку зависимостей;
- обеспечить явный способ запуска человеком;
- подготовить checklist validation-сценариев;
- подготовить session-based фиксацию проблем;
- не вносить улучшения в систему до фиксации проблем.

# Scope of Execution
## Включено в выполнение
- проверка текущего состояния проекта для human-run readiness;
- фиксация/создание инструкций по окружению;
- фиксация/создание инструкций по установке зависимостей;
- фиксация/создание инструкций запуска приложения человеком;
- validation checklist по пользовательским сценариям;
- подготовка структуры session-based validation reports;
- проведение первой validation-сессии;
- фиксация результатов validation-сессии в новом документе.

## Не включено в выполнение
- улучшения UX;
- изменения функциональности;
- архитектурные изменения;
- новые фичи;
- исправления по итогам validation.

# Execution Strategy
План выполняется в последовательных минимальных шагах T01-T07. Каждый этап завершается явным артефактом,
подтверждающим воспроизводимость validation-cycle без внедрения продуктовых изменений.

## T01 - Human-run readiness audit
- проверить, хватает ли текущих файлов для локального запуска человеком;
- проверить наличие зависимостей/инструкций/точки входа;
- зафиксировать gaps без их решения в рамках validation findings;
- определить минимальный набор runtime prerequisites.

Deliverable:
- подтверждённый список того, что нужно для воспроизводимого запуска человеком.

## T02 - Environment and dependencies setup instructions
- создать/зафиксировать воспроизводимые инструкции по подготовке окружения;
- зафиксировать способ установки зависимостей;
- зафиксировать версию Python / способ запуска venv;
- если в проекте отсутствует файл зависимостей, создать минимально необходимый runtime dependency file;
- если нужны служебные инструкции запуска, создать их как project files.

Ограничение:
- только то, что нужно для запуска человеком; без продуктовых изменений.

Deliverable:
- воспроизводимый setup path для человека.

## T03 - Human-run launch path
- зафиксировать явный способ запуска приложения человеком;
- зафиксировать URL/entrypoint'ы для проверки сценариев;
- если нужен README/операционный runbook для validation, создать новый документ или runtime guide file;
- проверить, что приложение запускается по этим инструкциям.

Deliverable:
- человек может поднять систему и открыть нужные страницы.

## T04 - Validation checklist
- создать обязательный checklist сценариев validation:
  - создание лида;
  - список лидов;
  - карточка лида;
  - изменение статуса;
  - заметки;
  - contact log;
  - consultation;
  - dashboard;
- для каждого сценария зафиксировать:
  - цель проверки;
  - шаги;
  - expected observable outcome;
- не добавлять решений и улучшений.

Deliverable:
- воспроизводимый checklist для human validation.

## T05 - Session-based validation reporting structure
- создать канонический путь `docs/validation_reports/`, если его нет;
- определить формат validation report документа:
  - одна validation-сессия = один документ;
  - свободный текст;
  - severity: low / medium / high;
  - ссылка на конкретный сценарий/checklist item;
- не превращать это в DEC; просто зафиксировать operational format исполнения.

Deliverable:
- готовая структура для фиксации результатов validation.

## T06 - First validation session execution
- провести первую human validation session по checklist;
- зафиксировать только проблемы/наблюдения;
- без решений;
- без исправлений;
- создать новый validation report документ как отдельный артефакт с session-based ID/именованием по принятому
  формату;
- зафиксировать severity и привязку к сценарию.

Deliverable:
- первый validation report с зафиксированными проблемами.

## T07 - Validation completion snapshot
- создать implementation snapshot по итогам выполнения OP validation-cycle;
- зафиксировать, что цикл выполнил задачу подготовки запуска и первой validation-сессии;
- перечислить созданные operational artifacts;
- не включать решения проблем.

Deliverable:
- итоговый IMP validation-cycle.

# Deliverables
- T01: подтвержденный audit readiness и список runtime prerequisites.
- T02: воспроизводимые инструкции окружения и зависимостей + runtime dependency file при необходимости.
- T03: проверенный launch path с явными URL/entrypoint'ами и run guide при необходимости.
- T04: обязательный checklist validation-сценариев с шагами и ожидаемыми наблюдаемыми результатами.
- T05: каноническая структура `docs/validation_reports/` и session-based формат фиксации.
- T06: первый validation report по итогам human validation session.
- T07: implementation snapshot закрытия validation OP.

# Definition of Done for execution
OP считается выполненным, если:
- человек может воспроизводимо поднять систему;
- зависимости и способ запуска зафиксированы;
- checklist validation создан;
- структура validation reports создана;
- проведена первая validation-сессия;
- создан отдельный validation report;
- создан implementation snapshot завершения validation OP;
- не предложены и не реализованы улучшения.

# Risks and Controls
- Риск: скрытая нехватка зависимостей для запуска.  
  Контроль: формализованный T01 audit + обязательная проверка запуска после T02/T03.
- Риск: неполный checklist.  
  Контроль: обязательное покрытие всех сценариев из `DOA-IDEA-002` и `DOA-ARCH-002`.
- Риск: случайный переход к улучшениям до фиксации проблем.  
  Контроль: жёсткий запрет изменений системы в execution prompts validation-cycle.
- Риск: смешивание observation и solution.  
  Контроль: в validation reports разрешены только наблюдения/проблемы без предложений решений.
- Риск: неполная трассируемость validation reports.  
  Контроль: session-based структура, severity и привязка к checklist item в каждом отчёте.

# Next Steps
- выполнение задач только в рамках данного OP;
- после завершения перейти к следующему lifecycle-циклу с анализом найденных проблем.
