# DOA-OP-010 — Implementation Plan for Environment Configuration Contract (Discovery)

## Metadata

- id: DOA-OP-010
- type: OP
- parent: DOA-DEC-010
- status: planned
- date: 2026-04-18

---

## Title

Implementation Plan for Environment Configuration Contract (Discovery)

---

## Context

**DOA-DEC-010** (accepted) фиксирует user-facing **environment contract**: **`.env.example`** в корне репозитория, секция **README** как documentation fragment, **пять** переменных, **optional** baseline, **strict config-only** (чтение env только через `app/discovery/config.py`). Сейчас **`.env.example`** и секция **README** отсутствуют; требуется внедрить артефакты контракта **без изменения** runtime-поведения и **без** правок кода приложения.

---

## Scope

В рамках OP-010:

- создать **`.env.example`** в корне проекта  
- добавить в **README** секцию **Environment Configuration**  
- зафиксировать переменные, defaults, optional semantics и влияние на pipeline  
- **не** менять код (`config.py` / discovery runtime) — только сверка на шаге 3  

---

## Steps

### Step 1 — создать `.env.example` (корень репозитория)

Минимальное содержимое (плейсхолдеры, без реальных секретов):

```env
OPENAI_API_KEY=
BRAVE_API_KEY=
DISCOVERY_LLM_ENABLED=false
DISCOVERY_SOURCE=vk
DISCOVERY_DEFAULT_LIMIT=10
```

Допустимы **краткие комментарии** (если выбранный формат комментариев согласован при внедрении; для `.env` обычно `#` строки над группой переменных).

---

### Step 2 — обновить README

Добавить секцию:

## Environment Configuration

Включить:

- **список** тех же пяти переменных  
- указание: на baseline все **optional**  
- **default** значения (согласованные с `load_config_from_env` / `merge_cli_overrides` и текущими hardcoded fallback в коде)  
- **влияние на pipeline**: LLM vs stub (ключ + `DISCOVERY_LLM_ENABLED` / CLI `--llm`), mock search до Brave (`BRAVE_API_KEY` зарезервирован), `DISCOVERY_DEFAULT_LIMIT` и CLI `--limit`, execution-level `DISCOVERY_SOURCE`  
- напоминание: скопировать `.env.example` → `.env` вручную; **не** коммитить `.env` с секретами  

---

### Step 3 — синхронизация с `config.py`

Проверить вручную (чеклист перед merge IMP):

- имена переменных в **`.env.example`** и **README** совпадают с **`load_config_from_env()`** (`OPENAI_API_KEY`, `BRAVE_API_KEY`, `DISCOVERY_*`)  
- **defaults** в тексте README / примерах совпадают с кодом: `DISCOVERY_LLM_ENABLED` → false, `DISCOVERY_SOURCE` → `vk`, `DISCOVERY_DEFAULT_LIMIT` → **10**, пустые ключи → отсутствие live API  

---

### Step 4 — проверка запуска (smoke)

- запуск **без** локального `.env` (только env процесса по умолчанию) — pipeline должен оставаться рабочим (stub/fallback)  
- запуск с **частичным** набором переменных в `.env` / окружении  
- при наличии ключей — контрактно зафиксировать ожидаемое поведение (без обязательного реального вызова модели в отчёте IMP)  

---

### Step 5 — проверка безопасности

- **`.env.example`**: нет реальных API keys, только пустые значения / плейсхолдеры  
- **README**: нет вставленных секретов, только описания и примеры имён переменных  

---

## Constraints

- **не** менять код приложения в рамках OP-010 (реализация артефактов DocOps)  
- **не** добавлять зависимости (**python-dotenv** и др.)  
- **не** вводить **новые** env-переменные сверх перечня **DEC-010**  

---

## Output

- файл **`.env.example`** в корне репозитория  
- обновлённый **README** с секцией **Environment Configuration**  
- зафиксированная **синхронизация** с `app/discovery/config.py` (чеклист Step 3) в **DOA-IMP-033**  

---

## Next

→ **DOA-IMP-033**
