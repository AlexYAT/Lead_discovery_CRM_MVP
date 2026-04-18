# DOA-ARCH-008 — Architecture of API Key Support in Config Layer (Discovery)

## Metadata

- id: DOA-ARCH-008
- type: ARCH
- parent: DOA-IDEA-008
- status: proposed
- date: 2026-04-18

---

## Title

Architecture of API Key Support in Config Layer (Discovery)

---

## Context

См. **DOA-IDEA-008**: Config Layer для discovery уже есть (**ARCH-007** / **IMP-031**), но ключи внешних API не входят в явный контракт: **`OPENAI_API_KEY`** читается implicit по месту использования, **`BRAVE_API_KEY`** не зафиксирован в модели, нет единого **`.env` contract** — растут скрытые зависимости.

Этот ARCH-цикл готовит:

- интеграцию **Brave Search** с предсказуемым источником ключа  
- **предсказуемую** конфигурацию LLM без разрозненного доступа к env в downstream  

---

## Goals

Расширение config должен:

- **централизовать** API keys в `DiscoveryConfig`  
- **убрать implicit `os.environ`** из search/classification как основного способа получить ключи  
- **задокументировать** `.env` contract (ожидаемые переменные и роль)  
- остаться в **локальном discovery scope** (без app-wide secrets framework)  
- повысить **воспроизводимость** конфигурации интеграций при фиксированном env + CLI для не-секретных полей  

---

## Architectural Decision

1. **Поля в `DiscoveryConfig`:** `brave_api_key`, `openai_api_key` (наряду с уже существующими `llm_enabled`, `source`, `default_limit`).  
2. **Источник значений ключей:** только **переменные окружения**, читаемые в **config module** (`BRAVE_API_KEY`, `OPENAI_API_KEY` → поля модели).  
3. **Access model (strict config-only):** downstream **не** читает env для ключей; orchestration строит config и передаёт объект / явные параметры в search и classification.  
4. **Missing key:** на уровне config допустимо `None`; фактическое поведение (stub vs live) задаёт **orchestration / контракт шага pipeline**, без неявного «второго» чтения env как fallback для того же секрета.  
5. **Scope:** только discovery config layer; без общесистемного secrets framework.  

---

## Config Model Extension

`DiscoveryConfig` (расширение):

- `llm_enabled: bool`  
- `source: str`  
- `default_limit: int`  
- `openai_api_key: str | None`  
- `brave_api_key: str | None`  

Загрузка: **`load_config_from_env()`** (и существующий merge CLI для не-секретных полей по правилам предыдущего цикла).

Правило нормализации: **пустая строка из env → `None`**; в объекте хранятся уже нормализованные значения.

---

## Access Rules

**Strict config-only** для ключей:

- **Запрещено** использовать `os.getenv` / `os.environ.get` в search/classification **как основной** способ получить `OPENAI_API_KEY` / `BRAVE_API_KEY` после внедрения цикла.  
- Ключи приходят через **config** и явную передачу из **orchestration**.  
- Решения external provider (вызов API vs stub) должны опираться на **видимые** поля/параметры, согласованные с config contract.  

*Исключение по объёму цикла:* чтение env остаётся **только** в `config.py` при сборке `DiscoveryConfig`.

---

## Integration Points

| Зона | Роль |
|------|------|
| `app/discovery/config.py` | Чтение env для ключей, нормализация, сборка `DiscoveryConfig` |
| `app/discovery/run.py` | Итоговый config после merge; передача дальше по pipeline |
| Search provider path | Явный вход `brave_api_key` (или эквивалент), без прямого env |
| Classification path | Явный вход `openai_api_key` / производные флаги поведения от orchestration |

Не входит в объём: детальная реализация Brave, смена **source** semantics, новые поля вне ключей и уже принятого config baseline.

---

## .env Contract

Ожидаемые переменные (baseline для локального запуска через `.env` / окружение процесса):

- `DISCOVERY_LLM_ENABLED`  
- `DISCOVERY_SOURCE`  
- `DISCOVERY_DEFAULT_LIMIT`  
- `OPENAI_API_KEY`  
- `BRAVE_API_KEY`  

**`.env`** — baseline source для dev/local. **CLI** по-прежнему override **только** для runtime-параметров предыдущего контракта (`limit`, `source`, `llm` flags и т.д. по **DEC-008**), **не** для передачи секретов в MVP.

---

## Constraints

- без новых библиотек  
- без secrets storage / encryption / vault  
- без runtime config UI  
- без глобального app-wide config framework  

---

## Non-Goals

- app-wide secrets architecture  
- key rotation  
- encrypted secret persistence  
- multiple provider profiles  
- CLI-аргументы для передачи секретов  

---

## Next

→ **DOA-DEC-009**
