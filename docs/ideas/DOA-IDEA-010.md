# DOA-IDEA-010 — Brave Search Integration

## Metadata

- id: DOA-IDEA-010
- type: IDEA
- parent: DOA-AUD-005
- status: proposed
- date: 2026-04-18

---

## Title

Brave Search Integration

---

## Problem

Текущий search layer реализован как **mock** и не использует реальные источники данных.

Это ограничивает:

- **качество** поиска потенциальных клиентов  
- **релевантность** кандидатов  
- **практическую применимость** системы в реальном контуре  

Pipeline не выполняет свою ключевую бизнес-функцию: **поиск реальных лидов** (recall остаётся синтетическим).

---

## Idea

Интегрировать **реальный** search provider (**Brave Search**) в discovery pipeline.

Цель:

- заменить mock search на **реальный** источник данных  
- обеспечить получение **реальных** кандидатов на входе пайплайна  
- **сохранить** текущую архитектуру этапов **Search → Classification → Normalization → Ingestion** без перепроектирования downstream  

Опора на уже принятый baseline: **Config Layer**, поддержка **API keys** и **environment contract** (без расширения scope за пределы discovery на уровне IDEA).

---

## Scope

**В рамках IDEA (граница намерения, без детализации реализации):**

- интеграция **внешнего** search provider (Brave) в слой поиска discovery  
- использование существующего **config layer** и пользовательского **env contract** для секретов и параметров  
- включение поиска в **тот же** pipeline без изменения смысла стадий **Classification → Normalization → Ingestion** на этом этапе замысла  

**Вне scope (MVP, без переусложнения):**

- тонкая **оптимизация качества** поиска и query tuning  
- **ranking / scoring** как отдельный продуктовый слой  
- **multi-provider** стратегия и failover между поисковыми API  
- изменения **UI** приложения  
- **автоматизация коммуникации** с лидами  
