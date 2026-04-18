# DOA-DEC-007 — Execution Entry Point Strategy

## Metadata

- id: DOA-DEC-007
- type: DEC
- parent: DOA-ARCH-006
- status: accepted
- date: 2026-04-18

---

## Title

Execution Entry Point Strategy

---

## Context

После реализации pipeline (IMP-026 → IMP-029) система способна:

- находить кандидатов
- классифицировать
- нормализовать
- сохранять в Candidate Queue

Однако отсутствует механизм запуска pipeline.

Это блокирует:

- воспроизводимое выполнение
- тестирование
- дальнейшую автоматизацию

---

## Decision

Принято решение использовать CLI entrypoint как базовый механизм исполнения pipeline.

Формат запуска:

python -m app.discovery.run

CLI принимает параметры (или использует .env):

- query
- limit
- source
- flags (debug / dry-run / llm)

---

## Rationale

CLI выбран как первый шаг, так как:

- обеспечивает детерминированное выполнение
- максимально прост в реализации
- полностью соответствует принципу IMP = факт
- удобен для локальной отладки
- легко расширяется до cron / automation

---

## Alternatives Considered

### API endpoint

Отклонён на текущем этапе:

- добавляет сложность (async, state)
- ухудшает дебаг
- преждевременен для MVP

### Hybrid (CLI + API)

Отложен:

- будет реализован в будущем
- CLI остаётся базовым execution layer

---

## Consequences

- следующий шаг: DOA-OP-008 (реализация CLI entrypoint)
- далее: DOA-IMP-030
- возможное расширение: API trigger layer
