# DOA-IDEA-007 — Config Layer for Discovery Pipeline

## Metadata

- id: DOA-IDEA-007
- type: IDEA
- parent: DOA-AUD-002
- status: proposed
- date: 2026-04-18

---

## Title

Config Layer for Discovery Pipeline

---

## Problem

Текущий execution слой не имеет централизованного управления конфигурацией.

Проблемы:

- логика управления LLM завязана на изменение env во время выполнения
- нет единой точки конфигурации
- параметры CLI частично дублируют будущий config
- `--source` не влияет на downstream поведение

Это создаёт:

- риск неконсистентного поведения
- сложность расширения (новые источники, providers)
- отсутствие reproducible config состояния

---

## Idea

Ввести Config Layer как отдельный слой управления параметрами pipeline.

Config должен:

- централизовать параметры execution
- управлять поведением pipeline (LLM, source, limits)
- быть совместимым с CLI
- использовать .env как источник (на MVP этапе)

---

## Scope (MVP)

- единый config объект
- загрузка из .env
- интеграция с CLI (CLI override)
- управление:
  - llm_enabled
  - source
  - default_limit

---

## Non-Goals

- сложные config системы (yaml/json)
- runtime config UI
- remote config

---

## Expected Outcome

- единая точка управления pipeline
- отказ от env-hacks
- подготовка к:
  - real search provider
  - automation layer

---

## Next

→ DOA-ARCH-007
