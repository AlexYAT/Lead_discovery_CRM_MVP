## Metadata

id: DOA-OP-015  
type: OP  
status: planned  
parent: DOA-DEC-015  
date: 2026-04-18

---

## Title

Discovery Observability Debug View Implementation Plan

---

## Objective

Реализовать CLI debug view для observability данных discovery pipeline без изменения pipeline и без изменения существующего observability слоя.

---

## Scope

В рамках:

- stage view для одной стадии
- diff view для сравнения двух стадий
- identity resolution по DOA-DEC-015
- базовый CLI renderer
- read-only доступ к export_stages()

Вне scope:

- web UI
- persistent storage
- auto analytics
- изменение pipeline
- изменение collector semantics

---

## Work Items

### T01 — Debug CLI Interface

Определить CLI-флаги / режимы для:

- stage view
- diff view

---

### T02 — Stage Renderer

Спланировать renderer для отображения одной стадии:

- stage name
- total items
- truncated / count info
- candidate entries в читаемом виде

---

### T03 — Diff Renderer

Спланировать renderer для сравнения двух стадий:

- items only in A
- items only in B (если нужно для симметричного режима)
- filtered out candidates как основной use case

---

### T04 — Identity Resolver

Спланировать сравнение кандидатов по:

- source_link как primary identity
- hash(text) как fallback

---

### T05 — Integration with Existing Observability

Спланировать read-only интеграцию поверх:

- collector.export_stages()
- get_observability_stages_for_current_execution()

Без изменения pipeline hooks и collector contract.

---

### T06 — Activation and Output Safety

Спланировать безопасный режим запуска:

- debug view работает только вместе с observability mode
- отсутствие observability данных обрабатывается явно
- вывод не влияет на основной pipeline result

---

## Done Definition

- определены CLI режимы stage/diff
- определён renderer для stage view
- определён renderer для diff view
- identity comparison следует DEC-015
- интеграция только read-only
- pipeline и observability semantics не изменены

---

## Next

DOA-IMP-038
