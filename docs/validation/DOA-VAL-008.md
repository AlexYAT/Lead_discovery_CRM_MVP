# DOA-VAL-008 — Validation of Environment Configuration Contract Artifacts

## Metadata

- id: DOA-VAL-008
- type: VAL
- parent: DOA-IMP-033
- status: passed
- date: 2026-04-18

---

## Title

Validation of Environment Configuration Contract Artifacts

---

## Scope

Проверено соответствие **DOA-IMP-033** (артефакты env contract без изменения runtime):

1. наличие и состав **`.env.example`**  
2. наличие и полнота секции **README** `Environment Configuration`  
3. совпадение **набора** переменных с baseline  
4. совпадение **defaults / semantics** с **`app/discovery/config.py`** (`load_config_from_env`)  
5. **отсутствие** изменений runtime-кода в рамках IMP-033  

---

## Executed Checks

### Check 1 — `.env.example`

- Файл **`.env.example`** присутствует в **корне** репозитория.  
- После комментариев в шапке зафиксированы **ровно пять** строк присваиваний: `OPENAI_API_KEY=`, `BRAVE_API_KEY=`, `DISCOVERY_LLM_ENABLED=false`, `DISCOVERY_SOURCE=vk`, `DISCOVERY_DEFAULT_LIMIT=10`.  
- Значения ключей **пустые**; нет строк вида `sk-…`, длинных токенов или иных признаков реальных секретов.  

**Результат:** PASS  

---

### Check 2 — README section

- Найден заголовок **`## Environment Configuration`**.  
- В таблице перечислены **все пять** переменных с пояснением назначения.  
- Явно указано: переменные **optional** на baseline; **defaults** в тексте/таблице; **stub / mock / graceful fallback** без ключей; копирование **`.env.example` → `.env`**; **`.env`** с секретами **не коммитить**; чтение env для discovery **только** через **`app/discovery/config.py`**; секреты **не** через CLI и **не** в логи.  

**Результат:** PASS  

---

### Check 3 — sync with `config.py`

Сверка с **`load_config_from_env()`** (`app/discovery/config.py`, строки чтения env):

- Имена: `OPENAI_API_KEY`, `BRAVE_API_KEY`, `DISCOVERY_LLM_ENABLED`, `DISCOVERY_SOURCE`, `DISCOVERY_DEFAULT_LIMIT` — совпадают с `os.getenv(...)` в коде.  
- Defaults в коде: `_parse_bool_env(..., False)` → baseline **false** для LLM; `source` — **`vk`** при отсутствии/пустоте; `_parse_int_env(..., 10)` → **10**; `_normalize_secret` для ключей при отсутствии/пустой строке → **`None`**. README и `.env.example` согласованы с этой семантикой.  

**Результат:** PASS  

---

### Check 4 — runtime code unchanged (IMP-033)

Команда: `git show d8e65e1 --name-only` (коммит **IMP-033** `docs(env): add environment config contract artifacts (IMP-033)`).

Изменённые файлы:

- `.env.example`  
- `README.md`  
- `docs/implementation_snapshot/DOA-IMP-033.md`  

Файлов под **`app/`** в коммите **нет**.  

**Результат:** PASS  

---

### Check 5 — contract consistency

- **`.env.example`** и **README** описывают **один и тот же** набор из пяти переменных и согласованные defaults.  
- Контракт согласован с **strict config-only**: единственная точка чтения env для discovery — **`app/discovery/config.py`** (зафиксировано в README; код IMP-033 не менял).  

**Результат:** PASS  

---

## Results

| Проверка | Исход |
|----------|--------|
| Check 1 `.env.example` | PASS — 5 переменных, секретов нет |
| Check 2 README | PASS — секция и требования по ТЗ |
| Check 3 sync `config.py` | PASS — имена и defaults |
| Check 4 runtime | PASS — в IMP-033 не менялся `app/` |
| Check 5 consistency | PASS — единый baseline, strict config-only |

---

## Notes

- **`.env.example`** сам по себе **не подгружается** приложением: оператор копирует в **`.env`** или задаёт переменные в окружении процесса; автозагрузки **`.env`** из кода **нет**.  
- **`python-dotenv`** в рамках **IMP-033** **не** добавлялся (как в **DEC-010** / **OP-010**).  
- Контракт **user-facing** (шаблон + README); **source of truth** для фактического чтения переменных остаётся **`app/discovery/config.py`**.  

---

## Conclusion

Validation passed.
