# DOA-ARCH-011 — Lead Qualification Layer Architecture

## Metadata

- id: DOA-ARCH-011
- type: ARCH
- parent: DOA-IDEA-011
- status: proposed
- date: 2026-04-18

---

## Title

Lead Qualification Layer Architecture

---

## Overview

**DOA-IDEA-011** вводит необходимость повысить **качество** кандидатов после появления **реального** recall (Brave и др.), не размывая ответственность downstream и не усложняя MVP.

Архитектурно фиксируется **Lead Qualification Layer** — тонкий слой **оценки и мягкой фильтрации** поверх уже классифицированных пар **(SearchHit, ClassificationResult)**, без удаления записей из pipeline на уровне MVP и **без** обязательного ML.

---

## Architectural Approach

Добавляется новый слой:

### Lead Qualification Layer

**Расположение в контуре discovery:**

**Search → Classification → Qualification → Normalization → Ingestion**

То есть квалификация выполняется **после** классификации (используются текст, сигнал pain/stub/LLM и краткие поля результата), **до** нормализации в `NormalizedCandidate`, чтобы downstream по-прежнему получал согласованный вход.

---

## Components

### Qualification Module

- **Вход:** результат classification — список пар **`(SearchHit, ClassificationResult)`** (или эквивалентный контракт orchestration).  
- **Поведение:** **soft qualification** — не удаляет кандидатов физически; добавляет **признаки / флаги / score-подобные поля** (минимальная модель — на этапе DEC/IMP) для последующего отбора оператором или для нормализации в metadata.  
- **Выход:** тот же список по размеру и порядку, обогащённый полями квалификации (обёртка, расширенная структура или параллельный словарь — деталь реализации вне ARCH).  

---

## Qualification Strategy

- **Soft qualification:** никакого hard delete кандидатов на этом шаге в MVP.  
- **Эвристики:** простые правила (ключевые паттерны, порог confidence, комбинация с источником recall) — перечень и пороги фиксируются в DEC/OP, не в ARCH.  
- **Без ML** как обязательного компонента; расширение до ML — отдельный lifecycle.  

---

## Data Flow

**Search** (recall) → **Classification** (pain signal) → **Qualification** (флаги качества / приоритет) → **Normalization** (как сегодня, с учётом дополнительных metadata при необходимости) → **Ingestion**.

Orchestration (`run.py` или преемник) вызывает модуль квалификации **один раз** на батч после classification.

---

## Constraints

- **Не** удалять кандидатов на уровне MVP (только маркировка / приоритизация).  
- **Не** менять **публичный контракт** downstream без отдельного DEC (нормализация по-прежнему опирается на существующую модель `NormalizedCandidate` и правила отбора pain-positive где применимо).  
- **Не** добавлять **ML** / обучаемые модели в рамках этого ARCH-цикла.  
