# DOA-OP-007-A — Execution Entry Point (CLI) — Extension

## Metadata

- id: DOA-OP-007-A
- type: OP
- parent: DOA-OP-007
- status: planned
- date: 2026-04-18

---

## Title

Execution Entry Point (CLI) — Extension

---

## Context

DOA-DEC-007 зафиксировал стратегию:

→ CLI entrypoint для запуска discovery pipeline

Текущий pipeline уже реализован (IMP-026 → IMP-029), но не имеет execution слоя.

---

## Scope

Добавить execution entrypoint:

- единая точка запуска pipeline
- CLI интерфейс
- управление параметрами
- поддержка .env

---

## Steps

### Step 1 — Create CLI module

Создать файл:

app/discovery/run.py

Функции:

- main()
- parse_args()

---

### Step 2 — Pipeline orchestration

Внутри main():

- вызвать search
- передать в classification
- затем normalization
- затем ingestion

---

### Step 3 — CLI arguments

Поддержать:

- --query (string, required)
- --limit (int, optional)
- --source (string, default vk)
- --llm (flag)
- --dry-run (flag)

---

### Step 4 — Logging

Вывод:

- количество найденных кандидатов
- количество прошедших фильтр
- количество сохранённых

---

### Step 5 — .env support

- использовать существующий config слой (если есть)
- НЕ вводить новый config framework

---

## Constraints

- НЕ менять существующие слои (search/classification/normalization/ingestion)
- НЕ менять schema
- orchestration только через вызовы

---

## Output

- CLI команда работает:

python -m app.discovery.run --query "..." --limit 10

---

## Next

→ DOA-IMP-030
