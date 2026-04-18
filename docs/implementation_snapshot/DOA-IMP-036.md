# DOA-IMP-036 — Dotenv Environment Initialization Layer Snapshot

## Metadata

- id: DOA-IMP-036
- type: IMP
- parent: DOA-OP-013
- status: implemented
- date: 2026-04-18

---

## Title

Dotenv Environment Initialization Layer Implementation Snapshot

---

## Summary

Реализован **Environment Initialization Layer** (**DOA-ARCH-012**, **DOA-DEC-013**, **DOA-OP-013**): корневой **`.env`** подмешивается в **`os.environ`** до использования **Config Layer**, без правок **`app/discovery/config.py`** и без изменений **pipeline**. Политика: **системное окружение не перетирается**; **повторный вызов init безопасен**; отсутствие **`.env`** не считается ошибкой. Реализация **stdlib-only** (без `python-dotenv`).

---

## Implemented Changes

- добавлен пакет **`app/core/`** с модулем **`env_init.py`** и функцией **`initialize_environment()`**  
- парсинг **`.env`** (UTF-8, комментарии `#`, опциональный префикс `export `, кавычки у значений) только в **`env_init`**  
- флаг и ранний return для **idempotency** после первого прохода  
- **`app/discovery/run.py`**: вызов **`initialize_environment()`** до импорта **`app.discovery.config`**  
- **`app/main.py`**: вызов **`initialize_environment()`** до остальных импортов **`app.*`**  
- **`.env.example`**: пояснение про приоритет системного окружения  
- **README**: автозагрузка **`.env`**, ссылка на **`app/core/env_init.py`**, дерево **`app/core/`**  

---

## Files Touched

| Path | Role |
|------|------|
| `app/core/__init__.py` | пакет `core` |
| `app/core/env_init.py` | единственное место чтения **`.env`** |
| `app/discovery/run.py` | ранний init → затем импорт config |
| `app/main.py` | ранний init для uvicorn / локального web runtime |
| `.env.example` | комментарий (контракт переменных без изменений) |
| `README.md` | краткое описание поведения |
| `docs/implementation_snapshot/DOA-IMP-036.md` | этот snapshot |

**Не менялись:** `app/discovery/config.py`, шаги pipeline.

---

## Where Initialization Runs

1. **`python -m app.discovery.run`** — при загрузке модуля, **до** `from app.discovery.config import ...`.  
2. **`uvicorn app.main:app`** — при импорте **`app.main`**, до подключения роутеров и **`init_db`**.  

---

## Verification

- **`python -m app.discovery.run --query "test anxiety" --dry-run`** (с **`.env`** в корне): exit **0**, в первой строке вывода **`has_brave_key=True`** при заданном в **`.env`** **`BRAVE_API_KEY`**.  
- Временное отсутствие **`.env`** (переименование файла): та же команда → exit **0**, при отсутствии ключа в окружении процесса **`has_brave_key=False`**.  
- Приоритет системы: **`$env:BRAVE_API_KEY='from_system'`** (PowerShell) перед запуском → `python -c "from app.core.env_init import initialize_environment; initialize_environment(); from app.discovery.config import load_config_from_env; print(load_config_from_env().brave_api_key)"` → вывод **`from_system`** (значение из **`.env`** не подменило переменную).  
- **Idempotency:** два вызова **`initialize_environment()`** подряд → без исключений.  
- Импорт веб-приложения: **`python -c "import app.main; print('main_import_ok')"`** → **`main_import_ok`**.  

---

## Constraints Validation

- **`.env`** не читается вне **`app/core/env_init.py`**.  
- **`app/discovery/config.py`** не изменялся; чтение значений discovery по-прежнему только там.  
- **Pipeline** (search → classify → …) не менялся.  
- **Env contract** (имена и смысл переменных из **`.env.example`**) сохранён.  

---

## References

- **DOA-IDEA-012**, **DOA-ARCH-012**, **DOA-DEC-013**, **DOA-OP-013**
