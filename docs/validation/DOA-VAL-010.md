# DOA-VAL-010 — Lead Qualification Layer Validation

## Metadata

- id: DOA-VAL-010
- type: VAL
- parent: DOA-IMP-035
- status: validated
- date: 2026-04-18

---

## Title

Lead Qualification Layer Validation

---

## Validation Scope

Проверка внедрения **Lead Qualification Layer** по фактическому контракту **DOA-IMP-035**:

- **qualification off / on** (`DISCOVERY_QUALIFICATION_ENABLED`)  
- **pass-through** при `qualification_enabled=false`  
- **metadata enrichment** (`qualification_*` в `NormalizedCandidate.metadata`) при включённом слое  
- **совместимость normalization** с входом из **2** или **3** элементов  
- отсутствие **breaking** изменений в типах **`SearchHit`** / **`ClassificationResult`**  
- **config discipline** для настроек qualification  

---

## Test Cases

### TC1 — Qualification disabled (pass-through)

**Условия:** `DISCOVERY_QUALIFICATION_ENABLED` отсутствует или **`false`**.

**Ожидаемо:** pipeline выполняется; exit **0**; метаданные qualification **не** добавляются в нормализованную запись; normalization / dry-run не ломаются.

---

### TC2 — Qualification enabled

**Условия:** `DISCOVERY_QUALIFICATION_ENABLED=true`.

**Ожидаемо:** слой активен; pipeline выполняется; exit **0**; метаданные qualification **формируются** на пути к normalization.

---

### TC3 — Qualification metadata propagation

**Проверка:** ключи **`qualification_tier`**, **`qualification_min_confidence`**, **`qualification_layer`** присутствуют в **`NormalizedCandidate.metadata`** при включённом слое.

---

### TC4 — Normalization compatibility

**Проверка:** **`normalize_candidates`** принимает как **2-элементные**, так и **3-элементные** строки входа без исключения.

---

### TC5 — Config discipline

**Проверка:** переменные **`DISCOVERY_QUALIFICATION_*`** читаются в **`app/discovery/config.py`**; в **`app/discovery/qualification/`** нет **`os.getenv` / `os.environ`**.

---

### TC6 — Application smoke

**Проверка:** **`import app.main`** успешен; discovery CLI не падает на smoke-командах выше.

---

## Executed Checks

### TC1 — выполнено

1. `$env:DISCOVERY_QUALIFICATION_ENABLED=$null; python -m app.discovery.run --query "тревожно" --dry-run --limit 1`  
   - Результат: exit **0**; в логе `qualification_enabled=False`; `normalized=1`.  

2. `$env:DISCOVERY_QUALIFICATION_ENABLED="false";` та же команда  
   - Результат: exit **0**; `qualification_enabled=False`.  

3. Проверка метаданных (pass-through): цепочка mock → classify → **`qualify_candidates(..., enabled=False)`** → normalize на pain-hit  
   - Результат: ключ **`qualification_tier`** в **`metadata` отсутствует** (`False`, значение `None`).  

---

### TC2 — выполнено

`$env:DISCOVERY_QUALIFICATION_ENABLED="true"; python -m app.discovery.run --query "тревожно" --dry-run --limit 1`

- Результат: exit **0**; в логе `qualification_enabled=True`; `normalized=1`.

Дополнительно (ingestion path, не dry-run):

`$env:DISCOVERY_QUALIFICATION_ENABLED="true"; python -m app.discovery.run --query "тревожно" --limit 1`

- Результат: exit **0**; `saved=1`.

---

### TC3 — выполнено

`$env:DISCOVERY_QUALIFICATION_ENABLED="true";` (и `DISCOVERY_QUALIFICATION_MIN_CONFIDENCE=0.45` в той же сессии) + inline Python: mock → classify → **`qualify_candidates(..., enabled=True, min_confidence=0.45)`** → normalize.

- Результат: в **`metadata`** присутствуют  
  - `qualification_tier` = **`high`**  
  - `qualification_min_confidence` = **`0.45`**  
  - `qualification_layer` = **`v1`**  

---

### TC4 — выполнено

Inline Python: **только** `classify_candidates` (список **2-кортежей**) → **`normalize_candidates`** без шага qualification.

- Результат: нормализация успешна; ключ **`qualification_tier`** в **`metadata` отсутствует**; присутствуют базовые ключи (`classification_mode`, `classifier_reason`).

---

### TC5 — выполнено

- `rg` по **`app/discovery/qualification/*.py`**: совпадений **`os.getenv` / `os.environ`** **нет**.  
- `rg` **`DISCOVERY_QUALIFICATION`** по **`app/discovery/*.py`**: вхождения **только** в **`app/discovery/config.py`**.  

---

### TC6 — выполнено

`python -c "import app.main; print('import_ok')"` → выведено **`import_ok`**, exit **0**.

---

## Results

| TC | Исход |
|----|--------|
| TC1 | **passed** |
| TC2 | **passed** |
| TC3 | **passed** |
| TC4 | **passed** |
| TC5 | **passed** |
| TC6 | **passed** |

---

## Conclusion

По **реально выполненным** проверкам (TC1–TC6):

- слой **qualification** ведёт себя в рамках **MVP**: **optional**, **pass-through** при выключении подтверждён (**TC1**).  
- **metadata enrichment** при включённом слое подтверждён (**TC3**).  
- **normalization** совместима с **2-** и **3-**элементным входом (**TC4**).  
- **config discipline** для **`DISCOVERY_QUALIFICATION_*`** и отсутствие env-чтения в модуле qualification подтверждены (**TC5**).  
- общий **smoke** приложения и CLI (включая не-dry-run с **`saved=1`**) подтверждён (**TC2**, **TC6**).  

**Residual / ограничения среды:** не выполнялся отдельный матричный прогон всех комбинаций порогов **`DISCOVERY_QUALIFICATION_MIN_CONFIDENCE`** и длинных батчей; не проверялась ручная валидация содержимого БД после ingest beyond счётчика **`saved`**.
