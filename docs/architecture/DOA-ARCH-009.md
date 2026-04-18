# DOA-ARCH-009 — Architecture of Environment Configuration Contract for Discovery Pipeline

## Metadata

- id: DOA-ARCH-009
- type: ARCH
- parent: DOA-IDEA-009
- status: proposed
- date: 2026-04-18

---

## Title

Architecture of Environment Configuration Contract for Discovery Pipeline

---

## Context

**DOA-IDEA-009** фиксирует пробел: после **DOA-IMP-032** discovery уже читает согласованный набор переменных в **Config Layer** (`app/discovery/config.py`), но в репозитории **нет** **`.env.example`**, нет **явного пользовательского контракта** — оператор не видит шаблон и краткое описание supported variables, defaults и влияния на pipeline.

---

## Goals

Environment / config contract должен:

- дать **шаблон** **`.env.example`** (без реальных секретов)  
- **явно перечислить** поддерживаемые env-переменные discovery baseline  
- описать **defaults**, **optional / required** и **эффект на pipeline**  
- **не менять** текущий runtime model (чтение env только через существующий config layer)  
- **не вводить** новые зависимости (в т.ч. **python-dotenv**)  

---

## Architectural Decision

1. В **корне репозитория** добавляется **`.env.example`** — шаблон конфигурации без секретов, синхронизируемый с фактическим чтением в config module.  
2. Помимо файла, контракт **кратко** дублируется в **пользовательской** проектной документации (**README** секция или уже принятый user-facing doc — конкретный путь фиксируется в **OP/DEC** цикла внедрения).  
3. **`.env.example`** и документация покрывают **только** текущий discovery baseline:  
   - `OPENAI_API_KEY`  
   - `BRAVE_API_KEY`  
   - `DISCOVERY_LLM_ENABLED`  
   - `DISCOVERY_SOURCE`  
   - `DISCOVERY_DEFAULT_LIMIT`  
4. **Источник runtime-чтения** env остаётся **`app/discovery/config.py`**; артефакты контракта **не** меняют поведение кода сами по себе.  
5. Секреты **не** передаются через CLI и **не** коммитятся как реальные значения (плейсхолдеры в `.env.example` только).  

---

## Contract Artifacts

### 1. `.env.example` (корень репозитория)

- перечень **имён** переменных, поддерживаемых discovery  
- **placeholder** / безопасные примеры значений (не боевые ключи)  
- **комментарии** в файле — допустимы, если согласованы с принятым стилем репозитория при внедрении  

### 2. Documentation fragment

- краткое **назначение** каждой переменной  
- **optional / required** и **default** semantics  
- **effect on pipeline** (LLM vs stub, mock search до Brave, лимиты, execution-level `source`)  
- напоминание: локальный **`.env`** не коммитится; оператор собирает окружение вручную по шаблону  

---

## Variable Model

| Переменная | Статус | Default / семантика | Pipeline |
|------------|--------|---------------------|----------|
| `OPENAI_API_KEY` | optional | нет → `None` | при наличии + `llm_enabled` допустим live LLM path; иначе stub / graceful fallback |
| `BRAVE_API_KEY` | optional | нет → `None` | на текущем baseline mock search; зарезервировано под будущий Brave HTTP |
| `DISCOVERY_LLM_ENABLED` | optional | **false** | базовый флаг LLM до CLI override |
| `DISCOVERY_SOURCE` | optional | **`vk`** | execution-level метка |
| `DISCOVERY_DEFAULT_LIMIT` | optional | **10** | верхняя граница recall до CLI `--limit` и cap в orchestration |

**Общее:** отсутствие ключей и части переменных **не ломает** pipeline — допустимы **stub / fallback** пути согласно **DEC-009** / текущей реализации.

---

## Usage Rules

- **`.env.example`** не содержит реальных секретов.  
- Оператор **копирует** `.env.example` → `.env` **вручную** (или задаёт те же переменные в окружении процесса).  
- Runtime: переменные читаются **только** через **Config Layer** (`load_config_from_env` + merge CLI для не-секретных полей).  
- **CLI override** — только для уже принятых runtime-полей (**не** для API keys).  
- Документация и **`.env.example`** должны **остаться согласованными** с `app/discovery/config.py` при любых будущих изменениях списка переменных.  

---

## Constraints

- без новых библиотек  
- без автозагрузки **`.env`** из кода на этом архитектурном baseline  
- без secret manager / vault  
- без глобального **app-wide** env contract в рамках этого цикла  

---

## Non-Goals

- **python-dotenv** и аналоги как обязательная часть стека  
- encrypted secrets, rotation  
- runtime reload конфигурации  
- multi-environment profiles (dev/staging/prod files в репозитории)  

---

## Next

→ **DOA-DEC-010**
