# DOA-IMP-035 — Lead Qualification Layer Implementation Snapshot

## Metadata

- id: DOA-IMP-035
- type: IMP
- parent: DOA-OP-012
- status: implemented
- date: 2026-04-18

---

## Title

Lead Qualification Layer Implementation Snapshot

---

## Summary

Реализован слой **soft qualification** в discovery pipeline (**DOA-DEC-012**, **DOA-OP-012**): после **Classification** каждая строка обогащается **опциональными** метаданными квалификации; при **выключенном** слое выполняется **pass-through** (пустые словари метаданных, поведение совместимо с предыдущим прогоном).

Контур расширён до:

**Search → Classification → Qualification → Normalization → Ingestion**

Базовые типы **`SearchHit`** и **`ClassificationResult`** **не** менялись; downstream получает **те же** пары плюс **третий** элемент — `dict` метаданных квалификации, обрабатываемый **normalization** при сборке `metadata` у **`NormalizedCandidate`**.

---

## Implemented Changes

- добавлен пакет **`app/discovery/qualification/`** с **`qualify_candidates`** (soft tiers: `none` / `medium` / `high` по `is_pain` и порогу confidence)  
- **`DiscoveryConfig`** расширен: **`qualification_enabled`**, **`qualification_min_confidence`**; загрузка из **`DISCOVERY_QUALIFICATION_ENABLED`**, **`DISCOVERY_QUALIFICATION_MIN_CONFIDENCE`** в **`config.py`**  
- **`merge_cli_overrides`** сохраняет новые поля с базы (CLI для qualification **не** добавлялся в этом IMP)  
- **`run.py`**: вызов **`qualify_candidates`** между classification и normalization; лог первой строки дополнен **`qualification_enabled=`**  
- **`normalize_candidates`** / **`normalize_hit`**: поддержка строк из **2** или **3** элементов; слияние **`qualification_meta`** в **`metadata`** нормализованной записи  
- **`.env.example`** и таблица **README** (`Environment Configuration`) дополнены новыми переменными  

---

## Module Structure

- **`app/discovery/qualification/__init__.py`** — экспорт **`qualify_candidates`**  
- **`app/discovery/qualification/service.py`** — точка входа обработки батча после classification  

---

## Config Integration

- флаг **`DISCOVERY_QUALIFICATION_ENABLED`** (default **`false`**) — включает вычисление tier и запись метаданных  
- **`DISCOVERY_QUALIFICATION_MIN_CONFIDENCE`** (default **`0.45`**, clamp 0..1) — порог для tier **`high`** при `is_pain`  
- чтение env **только** в **`app/discovery/config.py`**; модуль **`qualification`** **не** обращается к **`os.environ`**  

---

## Behavior

- **`qualification_enabled=False`** → **`qualify_candidates`** возвращает те же строки с **`{}`** метаданными; нормализация не получает дополнительных полей (pass-through)  
- **`qualification_enabled=True`** → в **`metadata`** кандидата добавляются **`qualification_tier`**, **`qualification_min_confidence`**, **`qualification_layer`** для pain-positive строк  
- pipeline завершается **без ошибок** в обоих режимах (проверено dry-run)  

---

## Constraints Validation

- **hard delete** кандидатов на шаге qualification **нет**  
- **ingestion** и контракт **`NormalizedCandidate`** не ломаются: расширение только **`metadata`**  
- **ML / AI** не добавлялся  

---

## Verification

- `DISCOVERY_QUALIFICATION_ENABLED` unset / `false`: `python -m app.discovery.run --query "тревожно" --dry-run --limit 2` → `qualification_enabled=False`, exit **0**, `normalized=2`.  
- `DISCOVERY_QUALIFICATION_ENABLED=true`: та же команда → `qualification_enabled=True`, exit **0**, `normalized=2`.  
- Проверка метаданных: цепочка mock → classify → qualify (on) → normalize на запросе с pain → в **`metadata`** присутствуют **`qualification_tier`** и **`qualification_layer`**.  
- `python -c "import app.main; print('ok')"` → **ok**.  

---

## Conclusion

Слой **qualification** внедрён в соответствии с **ARCH-011** и **DEC-012**: optional config-driven soft enrichment, pass-through при выключении, downstream контракт сохранён за счёт расширения **`metadata`** и совместимого входа normalization.
