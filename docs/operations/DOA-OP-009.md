# DOA-OP-009 — Implementation Plan for API Key Support in Config Layer (Discovery)

## Metadata

- id: DOA-OP-009
- type: OP
- parent: DOA-DEC-009
- status: planned
- date: 2026-04-18

---

## Title

Implementation Plan for API Key Support in Config Layer (Discovery)

---

## Context

**DOA-DEC-009** фиксирует: ключи в **`DiscoveryConfig`**, **strict config-only**, явная передача в downstream, **graceful fallback** без hidden env и без hard fail. Текущий baseline Config Layer — **DOA-IMP-031** (`DiscoveryConfig`, merge в `run.py`, `llm_enabled` / `source` / `default_limit`).

**Цель OP-009:** внедрить API keys в config, убрать **implicit** `os.environ` из search/classification, сохранить работоспособность pipeline (stub/mock при отсутствии ключей).

---

## Scope

**Включает:**

- расширение **`DiscoveryConfig`** полями ключей  
- чтение **`OPENAI_API_KEY`** / **`BRAVE_API_KEY`** в config module, нормализация пустых строк  
- обновление **`run.py`**: сборка config и **явная** передача ключей в вызовы  
- обновление **classification** и **search** сигнатур и реализации (без env для ключей)  
- **backward-compatible** поведение: те же сценарии dry-run / без ключей остаются рабочими  

**Не включает:**

- реализацию **Brave HTTP API**  
- изменения **normalization** / **ingestion**  
- **secrets storage** / vault / encryption  

---

## Steps

### Step 1 — расширить `config.py`

- Добавить поля: `openai_api_key`, `brave_api_key` (`str | None`).  
- Обновить **`load_config_from_env()`**: читать `OPENAI_API_KEY`, `BRAVE_API_KEY`; пустая строка → **`None`**.  
- `merge_cli_overrides` **не** принимает секреты через CLI (как в **ARCH-008**).

---

### Step 2 — обновить `run.py`

- После `load_config_from_env` + merge CLI итоговый **`DiscoveryConfig`** содержит ключи.  
- Передача в downstream **явными** аргументами, например:  
  - `classify_candidates(..., llm_enabled=..., openai_api_key=...)`  
  - `search_candidates(..., brave_api_key=...)`  
  (точные имена функций — по текущему коду orchestration.)

---

### Step 3 — обновить classification

- Убрать **`os.environ.get("OPENAI_API_KEY")`** (и аналоги) как основной путь.  
- Использовать переданный **`openai_api_key`**.  
- Сохранить **`llm_enabled`** как основной флаг режима; сочетание с ключом определяет LLM vs stub согласно **DEC-009**.

---

### Step 4 — подготовить search layer

- Добавить параметр **`brave_api_key`** в контракт search entrypoint.  
- Допускается **неиспользование** до появления реального Brave client (mock/stub без изменения семантики результата MVP).

---

### Step 5 — логирование

- **Не** логировать значения ключей.  
- При необходимости — только булевы признаки: `has_openai_key`, `has_brave_key` (или эквивалент в одной строке статуса config).

---

### Step 6 — проверка (ручная / smoke)

1. Без ключей в env: pipeline завершается, **fallback** / stub пути.  
2. С `OPENAI_API_KEY` и `llm_enabled=True`: LLM path **доступен** при прочих равных.  
3. `--dry-run`: без ошибок, счётчики как ожидается.  
4. `python -c "import app.main; print('import_ok')"` — **import safety**.

---

## Constraints

- не логировать секреты  
- не добавлять новые зависимости  
- не менять **schema** БД  
- не менять публичный **API** приложения (FastAPI routes)  

---

## Output

- обновлён **`app/discovery/config.py`**  
- обновлён **`app/discovery/run.py`**  
- обновлены **classification** и **search** слои: ключи только через параметры, **без** implicit env в downstream  
- ключи доступны в **`DiscoveryConfig`** и в цепочке вызовов согласно **DEC-009**  

---

## Next

→ **DOA-IMP-032**
