# DOA-OP-012 — Lead Qualification Layer Implementation Plan

## Metadata

- id: DOA-OP-012
- type: OP
- parent: DOA-DEC-012
- status: planned
- date: 2026-04-18

---

## Title

Lead Qualification Layer Implementation Plan

---

## Objective

Реализовать слой **qualification** в discovery pipeline (**DOA-IDEA-011**, **DOA-ARCH-011**, **DOA-DEC-012**) **без** изменения семантики существующих стадий и **без** breaking change контракта downstream.

---

## Scope

**В рамках OP-012:**

- добавление слоя **qualification** **после** **Classification** и **до** **Normalization**  
- **базовая** эвристическая оценка кандидатов (**soft qualification**, расширение данных флагами/полями)  
- **интеграция** включения/выключения и параметров через **Config Layer** (**DEC-012 Decision 3–4**)  
- сохранение **совместимости** pipeline при выключенном слое (pass-through)  

**Вне scope:**

- изменение логики **downstream** стадий (нормализация / ingestion) сверх необходимого проброса metadata  
- **ML / AI scoring**  
- изменения **UI** и CRM-продуктовые расширения  

---

## Work Items

### T01 — Qualification Module Structure

Создать пакет/модуль **`app/discovery/qualification/`** (или эквивалентное имя по конвенции репозитория) с публичной функцией уровня **`qualify_candidates(...)`**, принимающей выход classification и возвращающей обогащённый контракт (**IMP** уточнит типы).

---

### T02 — Qualification Logic

Реализовать **минимальные эвристики** (например: порог confidence, простые текстовые паттерны, комбинация с полями classification) — список и значения по умолчанию согласовать с **config**; **без** ML.

---

### T03 — Config Integration

Добавить в **`DiscoveryConfig`** / env флаг **включения** qualification и параметры правил (имена переменных согласовать с **`.env.example`** / **README** в том же IMP или отдельным мини-doc циклом); чтение env **только** в **`config.py`**.

---

### T04 — Pipeline Integration

Вставить вызов qualification в **`run.py`** (или актуальный orchestration entrypoint) строго в порядке:

**Search → Classification → Qualification → Normalization → Ingestion**

---

### T05 — Pass-through Mode

При **выключенном** qualification в config: **прозрачный** pass-through (те же структуры и порядок, что до внедрения слоя), **без** побочных эффектов на счётчики и dry-run.

---

### T06 — Compatibility Check

Прогон smoke: **dry-run** и короткий normal path с qualification **on** и **off**; подтвердить, что **normalization** и **ingestion** **не** требуют изменений файлов, кроме опционального чтения новых metadata-полей, если они уже поддержаны моделью.

---

## Done Definition

- слой **qualification** присутствует в pipeline на согласованном месте  
- pipeline **работает** с qualification **включённым** и **выключенным**  
- **downstream** не ломается (контракт **DEC-012**)  
- **config** управляет включением и параметрами  

---

## Next

→ **DOA-IMP-035**
