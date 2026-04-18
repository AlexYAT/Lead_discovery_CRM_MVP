## Metadata

id: DOA-DEC-014  
type: DEC  
status: accepted  
parent: DOA-ARCH-013  
date: 2026-04-18

---

## Title

Pipeline Observability Data and Behavior Decisions

---

## Decision 1 — Data Granularity

Сохраняются данные кандидатов на каждой стадии pipeline:

- вход стадии
- ключевые признаки (classification, qualification)
- выход стадии

---

## Decision 2 — Storage Model

Observability данные хранятся в памяти (in-memory) в рамках одного запуска pipeline.

Персистентное хранение не используется на уровне MVP.

---

## Decision 3 — Activation Mode

Observability слой включается только в debug режиме.

По умолчанию выключен.

---

## Decision 4 — Data Volume Control

Ограничение:

- фиксированное количество кандидатов
- отсутствие хранения полного history

---

## Decision 5 — Non-interference

Observability не влияет на:

- порядок pipeline
- результат обработки
- принятие решений

---

## Constraints

- не сохранять данные в БД
- не изменять pipeline
- не использовать observability для логики
- минимальный overhead
