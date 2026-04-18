## Metadata

id: DOA-OP-013  
type: OP  
status: planned  
parent: DOA-DEC-013  
date: 2026-04-18

---

## Title

Dotenv Initialization Implementation Plan

---

## Objective

Реализовать централизованную загрузку `.env` в локальном runtime через Environment Initialization Layer без нарушения config discipline и pipeline.

Критично соблюсти порядок запуска: обращение к Config Layer до завершения Environment Initialization недопустимо. Риски включают ранние импорты с побочным чтением настроек, альтернативные точки входа и subprocess, стартующие без того же entrypoint. Верификация порядка и цепочки импортов входит в работы T04–T05.

---

## Scope

В рамках:

- реализация Environment Initialization
- внедрение единой точки вызова
- соблюдение override policy
- соблюдение idempotency
- интеграция с текущим Config Layer

Вне scope:

- изменение env contract
- изменение pipeline
- секрет-менеджмент
- выбор альтернативных конфигурационных систем

---

## Work Items

### T01 — Initialization Module

Создать модуль Environment Initialization.

---

### T02 — Dotenv Loading Logic

Реализовать загрузку `.env` с учётом override policy.

---

### T03 — Idempotency Guard

Добавить защиту от повторной инициализации.

---

### T04 — Entry Point Integration

Вставить вызов initialization:

- до первого использования Config Layer
- в основном entrypoint приложения
- проверить цепочку импортов и пути запуска, чтобы Config Layer не читался до init (в т.ч. побочные эффекты при import)

---

### T05 — Subprocess Compatibility

Проверить поведение в CLI и subprocess (агент/скрипты).

---

### T06 — Fallback Behavior

Проверить корректную работу без `.env`.

---

## Done Definition

- `.env` загружается автоматически в локальном runtime
- system env не перетирается
- повторные вызовы безопасны
- Config Layer работает без изменений
- pipeline не изменён

---

## Next

DOA-IMP-036
