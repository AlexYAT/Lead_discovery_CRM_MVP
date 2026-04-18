# DOA-VAL-007 — Validation of Config Layer Implementation (Discovery)

## Metadata

- id: DOA-VAL-007
- type: VAL
- parent: DOA-IMP-031
- status: passed
- date: 2026-04-18

---

## Title

Validation of Config Layer Implementation (Discovery)

---

## Scope

Проверено поведение config layer (DOA-IMP-031) для discovery CLI:

1. значения по умолчанию при отсутствии `DISCOVERY_*` в окружении
2. приоритет CLI override над env defaults
3. контракт флагов `--llm` / `--no-llm` (явная конфигурация, без env-hack с удалением `OPENAI_API_KEY`)
4. обычный прогон пайплайна и счётчики
5. безопасность импорта приложения

Перед проверками 1–4 переменные `DISCOVERY_LLM_ENABLED`, `DISCOVERY_SOURCE`, `DISCOVERY_DEFAULT_LIMIT` сброшены в текущей сессии (`$null`), чтобы зафиксировать baseline без env overrides.

---

## Executed Checks

### Check 1 — defaults from env-less run (dry-run)

Команда: `python -m app.discovery.run --query "астролог" --dry-run`

Результат: **PASS** — exit 0; первая строка лога: `llm_enabled=False source='vk' limit=10`; `found(raw)=10`; dry-run завершён без ошибок.

### Check 2 — CLI override for `limit` / `source`

Команда: `python -m app.discovery.run --query "астролог" --limit 5 --source testsrc --dry-run`

Результат: **PASS** — exit 0; первая строка: `llm_enabled=False source='testsrc' limit=5`.

### Check 3 — `--llm` / `--no-llm` contract

**3a** — команда: `python -m app.discovery.run --query "астролог" --dry-run --no-llm`

Результат: **PASS** — первая строка: `llm_enabled=False source='vk' limit=10`.

**3b** — команда: `python -m app.discovery.run --query "астролог" --dry-run --llm`

Результат: **PASS** — первая строка: `llm_enabled=True source='vk' limit=10`. Фактический вызов LLM в классификаторе дополнительно зависит от наличия `OPENAI_API_KEY`; в данной валидации зафиксирован корректный **config contract** и лог флага.

### Check 4 — normal run

Команда: `python -m app.discovery.run --query "тревожно" --limit 3`

Результат: **PASS** — exit 0; вывод: `llm_enabled=False source='vk' limit=3`, `found(raw)=3`, `passed_classification(pain)=3`, `normalized=3`, `saved=3` (итоговые счётчики присутствуют, `saved > 0` для pain-hit выборки).

### Check 5 — import safety

Команда: `python -c "import app.main; print('import_ok')"`

Результат: **PASS** — exit 0; выведено `import_ok`.

---

## Results

| Проверка | Команда (суть) | Исход |
|----------|----------------|--------|
| 1 defaults | `--query "астролог" --dry-run` без `DISCOVERY_*` | `llm_enabled=False`, `source='vk'`, `limit=10`, exit 0 |
| 2 CLI override | `--limit 5 --source testsrc --dry-run` | первая строка: `limit=5`, `source='testsrc'` |
| 3a `--no-llm` | `--dry-run --no-llm` | `llm_enabled=False` |
| 3b `--llm` | `--dry-run --llm` | `llm_enabled=True` |
| 4 normal run | `--query "тревожно" --limit 3` | пайплайн до `saved=3` |
| 5 import | `import app.main` | `import_ok`, exit 0 |

Все перечисленные проверки выполнены в среде валидации; ошибок CLI и импорта не зафиксировано.

---

## Notes

- **DOA-VAL-006** остаётся валидным описанием прежнего execution baseline (включая старый контракт с временным снятием `OPENAI_API_KEY`) и **не** покрывает новый config contract из DOA-IMP-031; настоящий снимок относится только к config layer и текущему поведению CLI.
- Параметр **`source`** остаётся execution-level параметром (виден в первой строке лога конфигурации); он **не** меняет семантику normalization/ingestion слоёв относительно зафиксированного в проекте поведения для канонического источника в данных кандидата.
- **`--llm`** задаёт `llm_enabled=True` в конфигурации и логе; фактическое выполнение LLM-пути классификации по-прежнему зависит от наличия **`OPENAI_API_KEY`** и остальной инфраструктуры модели.

---

## Conclusion

Validation passed.
