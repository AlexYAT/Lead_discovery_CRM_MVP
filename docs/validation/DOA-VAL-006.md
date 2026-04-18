# DOA-VAL-006 — Validation of CLI Execution Entry Point

## Metadata

- id: DOA-VAL-006
- type: VAL
- parent: DOA-IMP-030
- status: passed
- date: 2026-04-18

---

## Title

Validation of CLI Execution Entry Point

---

## Scope

Проверено фактическое поведение CLI orchestration для DOA-IMP-030:

1. CLI dry-run режим
2. обычный execution режим
3. import safety
4. LLM flag behavior (контракт)
5. output counters и аргумент `--source`

---

## Executed Checks

### Check 1 — dry-run

Команда: `python -m app.discovery.run --query "астролог" --limit 5 --dry-run`

Результат: **PASS** — процесс завершился с кодом 0; в выводе `saved=0 (dry-run)`; при `passed_classification(pain)=0` ingestion не требуется (цепочка до нормализации отработала без записи в БД).

### Check 2 — normal run

Команда: `python -m app.discovery.run --query "тревожно" --limit 3`

Результат: **PASS** — код 0; счётчики присутствуют (`found(raw)=3`, `passed_classification(pain)=3`, `normalized=3`, `saved=3`); ingestion вызван, `saved > 0` при pain-hit выборке.

### Check 3 — import safety

Команда: `python -c "import app.main; print('import_ok')"`

Результат: **PASS** — импорт без исключения, выведено `import_ok`.

### Check 4 — LLM flag behavior

Проверено по контракту реализации IMP-030 (без изменения кода):

- без `--llm`: на время прогона из окружения удаляется `OPENAI_API_KEY`, классификация идёт по stub-path при отсутствии ключа после удаления.
- с `--llm`: переменная окружения не снимается на время прогона; при наличии `OPENAI_API_KEY` может использоваться LLM-путь в classifier.

Результат: **PASS** (контракт задокументирован и соответствует `app/discovery/run.py`).

### Check 5 — source argument

Команда: `python -m app.discovery.run --query "x" --limit 1 --dry-run --source testsrc`

Результат: **PASS** — в первой строке вывода `source='testsrc'`; нормализационный слой (IMP-028) по-прежнему фиксирует `source="vk"` в `NormalizedCandidate`; CLI `--source` только логируется.

---

## Results

| Проверка | Команда | Исход |
|----------|---------|--------|
| dry-run | `python -m app.discovery.run --query "астролог" --limit 5 --dry-run` | exit 0; `saved=0 (dry-run)` |
| normal | `python -m app.discovery.run --query "тревожно" --limit 3` | exit 0; `saved=3` |
| import | `python -c "import app.main; print('import_ok')"` | exit 0; `import_ok` |
| `--source` | `python -m app.discovery.run --query "x" --limit 1 --dry-run --source testsrc` | exit 0; строка `source='testsrc'` |

Все перечисленные проверки выполнены в среде валидации без ошибок CLI / импорта.

---

## Notes

- Search provider в baseline остаётся **mock/stub** (IMP-026); объём и содержание raw hits детерминированы mock-логикой.
- Итоговые счётчики **зависят от pain-hit** (stub-классификатор); для запросов без pain-паттернов `normalized` и `saved` могут быть 0 — это ожидаемо.
- Аргумент **`--source`** в IMP-030 **принимается и логируется**; семантика оркестрации (нормализация → `vk` в записи) **не расширялась** в рамках IMP-030.

---

## Conclusion

Validation passed.
