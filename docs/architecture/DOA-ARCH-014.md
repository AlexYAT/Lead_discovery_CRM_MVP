## Metadata

id: DOA-ARCH-014  
type: ARCH  
status: proposed  
parent: DOA-IDEA-014  
date: 2026-04-18

---

## Title

Discovery Observability Debug View Architecture

---

## Overview

Определить способ отображения observability данных через CLI без изменения pipeline.

---

## Architectural Approach

Debug View является отдельным слоем поверх Observability:

Pipeline → Observability → Debug View

Debug View не влияет на pipeline и не изменяет данные.

---

## Components

### 1. Observability Data Source

- collector.export_stages()

---

### 2. CLI Debug Renderer

Отвечает за форматирование и вывод данных

---

### 3. Debug Commands Interface

Поддерживает режимы:

- stage view
- diff view

---

## Interaction Modes

### Mode 1 — Stage View

Показ одной стадии:

- search
- classification
- qualification
- normalization

---

### Mode 2 — Diff View

Сравнение двух стадий:

- какие кандидаты отфильтрованы
- какие остались

---

## Data Flow

collector → export_stages() → renderer → CLI output

---

## Constraints

- не менять pipeline
- не менять observability слой
- только read-only доступ
- не хранить данные
- минимальный overhead

---

## Extensibility

В будущем:

- переход к UI
- фильтры
- сортировка
