# DOA-IMP-033 — Environment Configuration Contract Artifacts

## Metadata

- id: DOA-IMP-033
- type: IMP
- parent: DOA-OP-010
- status: implemented
- date: 2026-04-18

---

## Title

Environment Configuration Contract Artifacts

---

## Summary

Реализованы user-facing артефакты **environment contract** для discovery pipeline (**DOA-DEC-010**, **DOA-OP-010**).

- добавлен **`.env.example`** в корне репозитория  
- в **README** добавлена секция **Environment Configuration**  
- содержимое сверено с **`app/discovery/config.py`** (`load_config_from_env`)  

**Runtime-код приложения не изменялся.**

---

## Files

- `.env.example` (новый)
- `README.md` (обновлён)

---

## Behavior

- **`.env.example`** содержит ровно **пять** переменных baseline: `OPENAI_API_KEY`, `BRAVE_API_KEY`, `DISCOVERY_LLM_ENABLED`, `DISCOVERY_SOURCE`, `DISCOVERY_DEFAULT_LIMIT`  
- значения по умолчанию в файле совпадают с семантикой кода: `false`, `vk`, `10`, пустые ключи  
- **README** описывает optional/default semantics, влияние на pipeline, копирование в `.env`, запрет коммита секретов, единственную точку чтения env — `app/discovery/config.py`  
- в репозиторий **не** добавлены реальные API keys  

---

## Verification

1. **Наличие `.env.example`** — файл в корне, пять переменных, без заполненных секретов.  
2. **Наличие секции README** — заголовок `## Environment Configuration`, таблица переменных и поясняющий текст.  
3. **Сверка с `load_config_from_env()`** (`app/discovery/config.py`):  
   - имена: `OPENAI_API_KEY`, `BRAVE_API_KEY`, `DISCOVERY_LLM_ENABLED`, `DISCOVERY_SOURCE`, `DISCOVERY_DEFAULT_LIMIT` — совпадают с вызовами `os.getenv` в функции  
   - defaults: `_parse_bool_env(..., False)` → `DISCOVERY_LLM_ENABLED=false`; `source` из `(raw or "vk").strip() or "vk"` → `vk`; `_parse_int_env(..., 10)` → `DISCOVERY_DEFAULT_LIMIT=10`  
4. **Runtime-код** — `git diff` / список изменённых файлов не включает `app/discovery/config.py` и прочие модули `app/` (только `.env.example`, `README.md`, настоящий IMP snapshot).
