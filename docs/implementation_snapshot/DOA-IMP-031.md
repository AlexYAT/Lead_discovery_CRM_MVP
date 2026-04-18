# DOA-IMP-031 — Config Layer Implementation (Discovery)

## Metadata

- id: DOA-IMP-031
- type: IMP
- parent: DOA-OP-008
- status: implemented
- date: 2026-04-18

---

## Title

Config Layer Implementation (Discovery)

---

## Summary

Внедрён Config Layer для discovery pipeline.

- добавлен **DiscoveryConfig** и загрузка из env (`DISCOVERY_*`)
- CLI override интегрирован через **merge_cli_overrides**
- удалён **env-hack** с временным удалением `OPENAI_API_KEY` в `run.py`
- классификация переключается по явному **`llm_enabled`**
- метаданные `classification_mode` в нормализации могут задаваться вызывающим слоем (без смены контракта `NormalizedCandidate`)

---

## Files

- `app/discovery/config.py` (новый)
- `app/discovery/run.py` (обновлён)
- `app/discovery/classification/classifier.py` (параметр `llm_enabled`)
- `app/discovery/classification/service.py` (проброс `llm_enabled`)
- `app/discovery/normalization/normalizer.py` / `service.py` (опциональный `classification_mode` для metadata)

---

## Behavior

- **`llm_enabled`**: из `DISCOVERY_LLM_ENABLED` + override `--llm` / `--no-llm`
- **`source`**: из `DISCOVERY_SOURCE` + override `--source` (execution-level, логируется в первой строке вывода)
- **`default_limit`**: из `DISCOVERY_DEFAULT_LIMIT` + override `--limit`
- LLM path только при `llm_enabled` **и** наличии `OPENAI_API_KEY`; иначе stub

---

## Verification

Команда:

`python -m app.discovery.run --query "астролог" --limit 5 --dry-run`

Результат (фактический вывод):

```
llm_enabled=False source='vk' limit=5
found(raw)=5
passed_classification(pain)=0
normalized=0
saved=0 (dry-run)
```

Команда:

`python -m app.discovery.run --query "тревожно" --limit 3`

Результат:

```
llm_enabled=False source='vk' limit=3
found(raw)=3
passed_classification(pain)=3
normalized=3
saved=3
```

Импорт:

`python -c "import app.main; print('ok')"` → `ok`
