# DOA-IMP-034 — Brave Search Integration Implementation Snapshot

## Metadata

- id: DOA-IMP-034
- type: IMP
- parent: DOA-OP-011
- status: implemented
- date: 2026-04-18

---

## Title

Brave Search Integration Implementation Snapshot

---

## Summary

Реализована интеграция **реального** search provider (**Brave Web Search API**) в discovery pipeline с **graceful fallback** на mock (**DOA-DEC-011**, **DOA-OP-011**).

- при **наличии** `brave_api_key` в config — попытка **live** запроса (stdlib `urllib`, timeout)  
- при **отсутствии** ключа или **ошибке** live (HTTP, сеть, JSON) — **mock** recall того же контракта **`SearchHit`**  

Контур пайплайна **не менялся**: **Search → Classification → Normalization → Ingestion**. Downstream по-прежнему получает `list[SearchHit]`.

---

## Implemented Changes

- введён **Search Adapter** — модуль `app/discovery/search/adapter.py`, единая функция **`discovery_search`** (выбор live vs mock / fallback)  
- добавлена **live** реализация **`BraveLiveSearchProvider`** в `app/discovery/search/brave_live_provider.py` (GET `api.search.brave.com`, заголовок `X-Subscription-Token`)  
- mock вынесен в **`MockSearchProvider`** (`app/discovery/search/mock_provider.py`) для повторного использования при fallback  
- **`BraveSearchProvider`** переписан как тонкая обёртка над adapter (совместимость с существующим `search_candidates` / протоколом)  
- **`search_candidates`** по-прежнему принимает `brave_api_key` и опциональный `provider`; дефолтный путь идёт через adapter  
- **`run.py`** не менялся по сигнатуре вызова: ключ по-прежнему передаётся из `cfg.brave_api_key` (orchestration → search layer)  
- **config layer / env contract** без изменений: ключ уже загружался в **IMP-032**; прямого `os.environ` в новых search-модулях для ключей **нет**  

---

## Config Integration

- Используется существующий **Config Layer**: `brave_api_key` из `DiscoveryConfig` → `search_candidates(..., brave_api_key=...)` → adapter  
- Секрет по-прежнему из **env contract** (`BRAVE_API_KEY`), читается только в **`app/discovery/config.py`**  

---

## Behavior

- есть **валидный** `BRAVE_API_KEY` и успешный ответ API → **`SearchHit`** из результатов Brave (`title`/`description`/`url`)  
- ключа **нет** или live **падает** → те же по форме **`SearchHit`**, что и раньше у mock (`[mock brave] …`)  
- pipeline остаётся **вызываемым** в любом режиме  

---

## Constraints Validation

- **Classification / Normalization / Ingestion** — без изменений файлов в этом IMP  
- scope ограничен **search** + минимальные новые модули; **без** UI, CRM, ranking  
- **без** новых зависимостей (только stdlib)  

---

## Verification

- `python -m app.discovery.run --query "астролог" --dry-run --limit 2` при `BRAVE_API_KEY` unset → `has_brave_key=False`, `found(raw)=2`, mock-тексты в выдаче (проверено вручную).  
- при `BRAVE_API_KEY=invalid-key-test`, `--limit 1` → после ошибки API **fallback**, `found(raw)=1`, exit 0.  
- `python -c "import app.main; print('ok')"` → import успешен (регрессия приложения).  

---

## Conclusion

Интеграция Brave Search в рамках **MVP** выполнена и соответствует **DOA-ARCH-010** и **DOA-DEC-011**: adapter + live provider + mock fallback, контракт **`SearchHit`** сохранён.
