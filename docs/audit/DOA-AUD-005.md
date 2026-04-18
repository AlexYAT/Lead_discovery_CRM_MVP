# DOA-AUD-005 — Audit of Environment Configuration Contract Lifecycle (Discovery)

## Metadata

- id: DOA-AUD-005
- type: AUD
- status: accepted
- date: 2026-04-18
- parent: DOA-VAL-008

---

## Title

Audit of Environment Configuration Contract Lifecycle (Discovery)

---

## Audit Scope

Проверена цепочка **DOA-IDEA-009 → DOA-ARCH-009 → DOA-DEC-010 → DOA-OP-010 → DOA-IMP-033 → DOA-VAL-008** на предмет:

1. **Полноты lifecycle** от IDEA до VAL и связности `parent` по идентификаторам.  
2. **Соответствия реализации** принятым решениям **DOA-DEC-010** (шаблон `.env.example`, секция **README**, пять переменных, optional baseline, без смены runtime).  
3. **Согласованности** **`.env.example`**, **README** и фактического чтения в **`app/discovery/config.py`** (`load_config_from_env`).  
4. **Отсутствия** изменений runtime-кода в коммите **IMP-033** (подтверждено в **DOA-VAL-008** через `git show` коммита артефактов).  
5. **Сохранения** модели **strict config-only** (единственная точка чтения env для discovery — `config.py`; артефакты не вводят параллельных путей).  

---

## Reviewed Artifacts

- `docs/ideas/DOA-IDEA-009.md`  
- `docs/architecture/DOA-ARCH-009.md`  
- `docs/decisions/DOA-DEC-010.md`  
- `docs/operations/DOA-OP-010.md`  
- `docs/implementation_snapshot/DOA-IMP-033.md`  
- `docs/validation/DOA-VAL-008.md`  

Дополнительно для сверки выводов аудита использованы существующие файлы репозитория: **`.env.example`**, фрагмент **`README.md`** (секция **Environment Configuration**), **`app/discovery/config.py`** (без изменений в рамках данного цикла).  

---

## Findings

1. **Lifecycle полный и прослеживаемый:** IDEA → ARCH → DEC → OP → IMP → VAL закрыт; **VAL-008** со статусом **passed** ссылается на **IMP-033**, настоящий AUD — на **VAL-008**.  

2. **`.env.example`** и **README** реализуют контракт **DEC-010:** корневой шаблон, секция документации, ровно **пять** переменных (`OPENAI_API_KEY`, `BRAVE_API_KEY`, `DISCOVERY_LLM_ENABLED`, `DISCOVERY_SOURCE`, `DISCOVERY_DEFAULT_LIMIT`), optional baseline, запрет секретов в шаблоне и в VCS-описании.  

3. **Синхронность с `config.py`:** имена и defaults, зафиксированные в **IMP-033** / **VAL-008**, согласованы с **`load_config_from_env()`** (в т.ч. `false` / `vk` / `10`, пустые ключи → `None` через `_normalize_secret`).  

4. **DX без смены runtime:** пользователь получил явный шаблон и README-описание; поведение процесса при отсутствии `.env` не менялось за счёт кода в этом цикле (**IMP-033** менял только `.env.example`, `README.md` и snapshot).  

5. **Strict config-only сохранён:** README явно указывает единственную точку чтения — **`app/discovery/config.py`**; не добавлялись **python-dotenv** и автозагрузка `.env` (**VAL-008 Notes**).  

---

## Risks

- **Рассинхрон:** при расширении `load_config_from_env` забыть обновить **`.env.example`** и **README** — оператор увидит устаревший контракт.  
- **Ожидание автозагрузки `.env`:** контракт user-facing, но приложение по-прежнему не подгружает файл автоматически; оператор должен задавать env вручную или через среду запуска.  
- **`BRAVE_API_KEY`:** в README и шаблоне переменная есть, live Brave integration в этом цикле **не** входила; риск неверной интерпретации «ключ уже включает поиск».  

---

## Conclusion

Environment configuration contract lifecycle is complete and accepted as baseline.
