# DOA-VAL-011 — Discovery Observability Debug View Validation

## Metadata

- id: DOA-VAL-011
- type: VAL
- parent: DOA-IMP-038
- status: validated
- date: 2026-04-18

---

## Title

Discovery Observability Debug View Validation

---

## Validation Scope

Проверка **CLI debug view** поверх observability данных (**DOA-IMP-038**) в локальном окружении **Windows / PowerShell**, каталог репозитория в корне проекта:

- **stage view**
- **diff view**
- правила **безопасной активации** (debug только вместе с observability)
- разделение **stdout / stderr** при объединённом перенаправлении
- **не заявляется** проверка ветки **fallback identity** без отдельного сценария с пустым `source_link`
- **не заявляется** отдельный повторный аудит git-diff hooks/collector вне описания IMP

---

## Test Cases

### TC1 — Stage view requires observability

**Условия:** запуск `--discovery-debug-stage` без `--discovery-observability`.

**Ожидаемо:** отказ с понятной ошибкой; exit code **2**; pipeline не выполняется.

---

### TC2 — Stage view rendering

**Условия:** `--discovery-observability --discovery-debug-stage search`.

**Ожидаемо:** вывод stage в **stderr**; имя стадии; **total** / **truncated**; записи кандидатов; **stdout** с отчётом pipeline отдельно.

---

### TC3 — Diff view rendering

**Условия:** `--discovery-observability --discovery-debug-diff search,normalization`.

**Ожидаемо:** diff в **stderr**; блок **A \\ B**; симметричный блок отдельно при наличии; **stdout** с отчётом pipeline отдельно.

---

### TC4 — Identity strategy

**Проверка:** primary **`source_link`**; fallback **text-hash**; соответствие **DOA-DEC-015**.

---

### TC5 — No pipeline interference

**Проверка:** семантика pipeline не меняется; без debug-флагов — baseline как **IMP-037**; контракт hooks/collector не менялся.

---

### TC6 — Stream separation

**Проверка:** отчёт pipeline в **stdout**; observability/debug в **stderr**; при **`2>&1`** порядок приемлем для оператора (**flush** на stderr-debug).

---

## Executed Checks

Все команды из каталога репозитория: `D:\Work\Lead discovery CRM MVP\Project` (PowerShell).

### TC1 — выполнено

```powershell
python -m app.discovery.run --query "t" --dry-run --discovery-debug-stage search 2>&1
```

**Результат:** в **stderr** строка `discovery_debug: error: --discovery-debug-stage / --discovery-debug-diff require --discovery-observability`; код выхода **2**; строк отчёта pipeline в **stdout** нет (pipeline не запускался).

---

### TC2 — выполнено

```powershell
python -m app.discovery.run --query "t" --dry-run --discovery-observability --discovery-debug-stage search 2>&1
```

**Результат:** в **stderr** присутствуют строки с префиксом `discovery_debug:`: `stage=search`, `total=10` (значение зависит от окружения), `truncated=False`, блоки `[n] id=link:https://vk.com/wall-mock-...`; в **stdout** после блока **stderr** — стандартные строки отчёта (`llm_enabled=...`, `found(raw)=10`, и т.д.).

---

### TC3 — выполнено

```powershell
python -m app.discovery.run --query "t" --dry-run --discovery-observability --discovery-debug-diff search,normalization 2>&1 | Select-Object -First 20
```

**Результат:** в **stderr** строки `discovery_debug: diff search -> normalization`, заголовок с `only_in_search_not_in_normalization count=10`, список `id=link:...`, затем симметричный заголовок `only_in_normalization_not_in_search count=0`; далее в потоке идут строки **stdout** отчёта pipeline (порядок: сначала завершён блок **stderr** для данной выборки строк).

---

### TC4 — частично выполнено

- **Primary `source_link`:** в выводе TC2 и TC3 идентификаторы имели вид `id=link:https://...` — согласуется с правилом primary из **DOA-DEC-015**.
- **Fallback `text:` + hash:** отдельный прогон с искусственно пустым `source_link` в снимках **не выполнялся** в рамках этой валидации → ветка fallback **не подтверждена** экспериментом здесь.

---

### TC5 — частично выполнено

```powershell
python -m app.discovery.run --query "t" --dry-run 2>&1
```

**Результат:** только **stdout** (без `discovery_observability` / `discovery_debug`); отчёт в ожидаемом формате — соответствует **отсутствию** debug-режима.

**Контракт hooks/collector:** отдельный повторный прогон тестов / `git diff` по файлам observability в этой валидации **не выполнялся**; утверждение опирается на зафиксированный состав изменений **DOA-IMP-038** (новый `debug_cli.py`, правки `run.py`).

---

### TC6 — выполнено

Проверка выполнена в рамках команд TC2–TC3 и выборки **`Select-Object -First 20`** для TC3: отчёт pipeline идёт отдельным блоком **stdout** после блока **stderr**; префиксы `discovery_debug:` не смешиваются со строками метрик **stdout** внутри одной и той же строки.

---

## Results

| TC | Статус | Комментарий |
|----|--------|-------------|
| TC1 | **passed** | exit **2**, сообщение об ошибке, pipeline не стартовал |
| TC2 | **passed** | stage в **stderr**, метрики в **stdout** |
| TC3 | **passed** | diff «только в A» + симметричный блок; **stdout** отдельно |
| TC4 | **partial** | подтверждён только primary `link:`; fallback **not run** |
| TC5 | **partial** | baseline без debug — **passed**; hooks/collector — **not run** (опора на IMP) |
| TC6 | **passed** | разделение потоков подтверждено на фактических выводах |

---

## Conclusion

По **выполненным** проверкам: **stage** и **diff** режимы в CLI **работают** при включённом **`--discovery-observability`**; активация debug **без** observability **безопасно отклоняется** (exit **2**); **stdout** отчёта pipeline и **stderr** observability/debug **разделены** на проверенных командах.

**Остаточные риски / пробелы:** не проверена экспериментально ветка **identity fallback**; не выполнялся отдельный регрессионный набор на всех стадиях **`--discovery-debug-stage`** и всех парах **`--discovery-debug-diff`**; устойчивость порядка вывода при других оболочках / буферизации не исследовалась за пределами указанных запусков.
