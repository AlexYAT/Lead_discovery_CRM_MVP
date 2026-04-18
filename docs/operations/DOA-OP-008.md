# DOA-OP-008 — Implementation Plan for Config Layer (Discovery)

## Metadata

- id: DOA-OP-008
- type: OP
- parent: DOA-DEC-008
- status: planned
- date: 2026-04-18

---

## Title

Implementation Plan for Config Layer (Discovery)

---

## Context

CLI execution layer уже реализован (**IMP-030**, **VAL-006**). **DOA-DEC-008** фиксирует: merge config в **`app/discovery/run.py`**, управление LLM через **`llm_enabled: bool`**, поле **`source`** — execution-level без изменения normalization/ingestion semantics. Требуется убрать env-hack и централизовать конфигурацию без расширения scope за пределы discovery.

---

## Scope

В рамках OP-008:

- добавить **config module** в discovery;
- реализовать **`DiscoveryConfig`** и загрузку из **env** (stdlib);
- внедрить **CLI override** согласно precedence DEC/ARCH;
- обновить **orchestration** в `run.py`;
- убрать временную манипуляцию **`OPENAI_API_KEY`** как основной переключатель режима;
- обновить **логирование** итогового config.

---

## Steps

### Step 1 — Create config module

Создать **`app/discovery/config.py`** с контрактом:

- **`DiscoveryConfig`**
- **`load_config_from_env()`** → базовый объект из переменных окружения и defaults

---

### Step 2 — Implement config model

Поля минимум:

- **`llm_enabled: bool`**
- **`source: str`**
- **`default_limit: int`**

Допустим helper **`merge_cli_overrides(...)`** (или эквивалент внутри `run.py`), не нарушая single merge point в DEC-008.

---

### Step 3 — CLI integration

В **`app/discovery/run.py`**:

- построить config из env через config module;
- применить CLI overrides;
- сформировать итоговый **`DiscoveryConfig`** перед запуском pipeline.

---

### Step 4 — Remove env-hack

- удалить логику временного удаления / восстановления **`OPENAI_API_KEY`** в `run.py`;
- передавать режим LLM через **`llm_enabled`** (и далее в classification path согласно Step 5).

---

### Step 5 — Pass config downstream

- **classification** получает **`llm_enabled`** (или эквивалентный явный параметр), без самостоятельного чтения env для переключения режима;
- **search / orchestration** получают **`default_limit`**, **`source`** там, где это уже применимо на execution-level, без изменения контракта normalization/ingestion.

---

### Step 6 — Logging update

- логировать **итоговый** `DiscoveryConfig` (или его ключевые поля): `llm_enabled`, `source`, `default_limit`;
- сохранить существующие счётчики pipeline.

---

## Constraints

- **не** менять **schema** БД;
- **не** менять публичный **API** приложения;
- **не** добавлять зависимости (stdlib + существующий код);
- **не** вводить global app-wide config layer на этом шаге.

---

## Output

- CLI работает через **единый config object**;
- **env-hack** для LLM-switching **удалён**;
- поведение **детерминировано** при фиксированных env + CLI.

---

## Next

→ **DOA-IMP-031**
