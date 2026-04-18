# DOA-ARCH-007 — Architecture of Config Layer for Discovery Pipeline

## Metadata

- id: DOA-ARCH-007
- type: ARCH
- parent: DOA-IDEA-007
- status: proposed
- date: 2026-04-18

---

## Title

Architecture of Config Layer for Discovery Pipeline

---

## Context

См. **DOA-IDEA-007**: execution layer (CLI) уже есть, но конфигурация разрознена: `--llm` опирается на временную манипуляцию `OPENAI_API_KEY`, `--source` логируется и не задаёт downstream semantics, нет единого контракта чтения настроек.

---

## Goals

Config Layer должен:

- дать **единую точку чтения** конфигурации discovery pipeline
- **убрать env-hack** из orchestration (`run.py` и аналоги)
- **сохранить CLI** как execution entrypoint с явными overrides
- обеспечить **воспроизводимость** baseline config (env + defaults + CLI)

---

## Architectural Decision

1. **Scope:** слой реализуется локально в discovery: `app/discovery/config.py` (или эквивалентный один модуль в `app/discovery/`, без app-wide config framework).  
2. **Чтение env:** только **stdlib** (`os.getenv` / аналог), **без новых зависимостей**.  
3. **Базовая модель:** объект **`DiscoveryConfig`** с полями минимум: `llm_enabled: bool`, `source: str`, `default_limit: int`.  
4. **Precedence:** значения из **CLI** перекрывают **env**, env перекрывает **hardcoded defaults**.  
5. **Orchestration:** `run.py` и связанные вызовы используют **готовый config object**, а не прямую подмену переменных окружения внутри pipeline.

Контрактные helpers (архитектурно): `load_config_from_env()`, `merge_cli_overrides(...)` — без детализации реализации в этом документе.

---

## Config Model

Минимальная структура:

- **`DiscoveryConfig`**
  - `llm_enabled: bool`
  - `source: str`
  - `default_limit: int`

Расширение полей — только через следующий ARCH/DEC цикл при необходимости.

---

## Precedence Rules

Порядок применения значений:

1. **CLI arguments** (явно переданные флаги/опции)
2. **environment variables** (через `.env` / окружение процесса)
3. **hardcoded defaults** (безопасный baseline в коде)

Правила:

- отсутствие CLI-аргумента **не ломает** env-driven запуск;
- итоговый config **детерминирован**: после merge все поля явно заданы.

---

## Integration Points

Config используется как вход orchestration:

- **`app/discovery/run.py`** — построение config, merge CLI, передача дальше
- **classification path** — получает `llm_enabled` (или эквивалент) из config, без самостоятельного чтения env для переключения режима
- **search path** — лимиты/источник согласованы с `default_limit` / `source` где применимо
- **defaults execution** — единая точка для лимитов и логических флагов

Downstream-модули **по возможности** принимают уже нормализованные параметры, а не читают env напрямую.

---

## Constraints

- без изменения публичного **API** приложения (FastAPI routes)
- **без новых библиотек** для config
- без **runtime UI** и remote config
- **без** общесистемного config layer на этом этапе (только discovery scope)

---

## Non-Goals

- Pydantic Settings / pydantic-base config
- YAML/JSON файлы конфигурации
- multi-profile / per-user config
- distributed / централизованный сервер конфигурации

---

## Next

→ DOA-DEC-008
