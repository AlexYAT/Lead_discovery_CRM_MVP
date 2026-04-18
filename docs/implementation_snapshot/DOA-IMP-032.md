# DOA-IMP-032 — API Key Support in Config Layer (Discovery)

## Metadata

- id: DOA-IMP-032
- type: IMP
- parent: DOA-OP-009
- status: implemented
- date: 2026-04-18

---

## Title

API Key Support in Config Layer (Discovery)

---

## Summary

Реализована поддержка API keys в Config Layer discovery pipeline.

- **`DiscoveryConfig`** расширен полями **`openai_api_key`** / **`brave_api_key`**
- ключи читаются из env только в **`config.py`** (`OPENAI_API_KEY`, `BRAVE_API_KEY`), пустая строка → **`None`**
- orchestration в **`run.py`** передаёт ключи явно в **search** / **classification**
- убран implicit доступ к **`OPENAI_API_KEY`** в classification и в normalization fallback для mode
- **`merge_cli_overrides`** по-прежнему только runtime-поля (секреты через CLI не принимаются)
- при ошибках OpenAI (в т.ч. невалидный ключ) — **graceful fallback** на keyword stub без hard fail
- Brave HTTP client **не** реализован; **`brave_api_key`** принят в контракте **`BraveSearchProvider`** / **`search_candidates`**

---

## Files

- `app/discovery/config.py`
- `app/discovery/run.py`
- `app/discovery/classification/classifier.py`
- `app/discovery/classification/service.py`
- `app/discovery/search/service.py`
- `app/discovery/search/brave_provider.py`
- `app/discovery/normalization/normalizer.py`

---

## Behavior

- **`openai_api_key` / `brave_api_key`** в `DiscoveryConfig`; значения **не** логируются, только **`has_openai_key`** / **`has_brave_key`**
- **classification:** LLM path при `llm_enabled` **и** непустом `openai_api_key`; иначе stub; при сбое API — stub
- **search:** параметр **`brave_api_key`** проброшен; mock-поведение без изменений
- **normalization:** при отсутствии переданного `classification_mode` fallback метаданных — **`stub`** (без чтения env для ключа)

---

## Verification

Окружение: для сценариев без ключей в сессии обнулены `OPENAI_API_KEY` и `BRAVE_API_KEY`.

**1.** `python -m app.discovery.run --query "астролог" --dry-run`

```
llm_enabled=False source='vk' limit=10 has_openai_key=False has_brave_key=False
found(raw)=10
passed_classification(pain)=0
normalized=0
saved=0 (dry-run)
```

(exit 0)

**2.** `python -m app.discovery.run --query "тревожно" --limit 3`

```
llm_enabled=False source='vk' limit=3 has_openai_key=False has_brave_key=False
found(raw)=3
passed_classification(pain)=3
normalized=3
saved=3
```

(exit 0)

**3.** `python -c "import app.main; print('import_ok')"` → `import_ok` (exit 0)

**4.** Контракт `--llm` + ключ из env (без реального успешного вызова модели обязателен):

- `OPENAI_API_KEY=$null`, `python -m app.discovery.run --query "астролог" --dry-run --llm --limit 2` → первая строка содержит `llm_enabled=True`, `has_openai_key=False`, stub path, exit 0
- `OPENAI_API_KEY=sk-invalid-test-key-for-smoke`, та же команда → `has_openai_key=True`, после 401 OpenAI — fallback на stub, pipeline завершился с exit 0
