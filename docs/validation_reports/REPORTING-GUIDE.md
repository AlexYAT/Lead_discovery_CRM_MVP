# Validation Reporting Guide

Назначение: единые правила фиксации результатов validation-сессий.

## Session-based формат
- одна validation-сессия = один документ;
- файл создаётся в `docs/validation_reports/`;
- рекомендуемое именование: `DOA-VAL-XXX.md`.

## Что обязательно фиксировать в отчёте
- идентификатор validation-сессии;
- дата/время сессии;
- кто выполнял сценарии и кто фиксировал наблюдения;
- список пройденных checklist item (`VAL-01 ... VAL-08`);
- observations/problems по каждому зафиксированному случаю.

## Формат записи observations/problems
Для каждой проблемы фиксировать:
- checklist item / сценарий (например, `VAL-03`);
- где возникает (экран / действие);
- описание проблемы (свободный текст);
- наблюдаемое поведение;
- ожидаемое поведение (без решения);
- severity: `low` / `medium` / `high`.

## Ограничения отчётов
- только observations/problems;
- без решений;
- без предложений улучшений;
- без функциональных изменений в рамках validation-session.

## Минимальный шаблон session report
```markdown
# Validation Session: DOA-VAL-XXX

## Session Metadata
- Date:
- Executor:
- Observer:
- Scope: checklist items

## Findings
### Finding 1
- Scenario: VAL-XX
- Where:
- Description:
- Observed behavior:
- Expected behavior (without solution):
- Severity: low|medium|high

## Notes
- Дополнительные наблюдения без решений.
```
