# DOA-IMP-037 — Discovery Pipeline Observability Layer Snapshot

## Metadata

- id: DOA-IMP-037
- type: IMP
- status: implemented
- parent: DOA-OP-014
- date: 2026-04-18

---

## Title

Discovery Pipeline Observability Layer Implementation Snapshot

---

## Summary

Добавлен **non-invasive** слой наблюдаемости для discovery pipeline (**DOA-IDEA-013**, **DOA-ARCH-013**, **DOA-DEC-014**, **DOA-OP-014**): снимки стадий **только in-memory** в рамках **одного** запуска CLI, без БД, без синглтона коллектора, без изменения **сигнатур** сервисов pipeline и без изменения **бизнес-логики** стадий. Включение — только флаг **`--discovery-observability`**; при выключенном флаге хуки **не вызываются**, коллектор **не создаётся**. Контекст выполнения — **`contextvars`** (не глобальное хранилище результатов между запусками). **Qualification** покрыт отдельным хуком после **`qualify_candidates`**.

---

## Implemented Changes

- пакет **`app/discovery/observability/`**:
  - **`collector.py`** — класс **`PipelineObservabilityCollector`**: **`add_stage(stage_name, data)`**, экспорт стадий **`export_stages()`**, лимит размера снимков через **`MAX_OBSERVABILITY_ITEMS`** (50) в **`snapshots.py`**
  - **`context.py`** — **`attach_pipeline_observability`**, **`detach_pipeline_observability`**, **`current_pipeline_observability`** на базе **`ContextVar`**
  - **`snapshots.py`** — преобразование **`SearchHit`**, строк classification/qualification, **`NormalizedCandidate`** в ограниченные **read-only** dict-структуры
  - **`hooks.py`** — **`observe_after_search`**, **`observe_after_classification`**, **`observe_after_qualification`**, **`observe_after_normalization`** (внутри — no-op, если контекст пуст)
  - **`access.py`** — **`get_observability_stages_for_current_execution()`** для будущего debug/UI (чтение только при активном контексте)
  - **`__init__.py`** — публичный экспорт API
- **`app/discovery/run.py`**: опциональный флаг **`--discovery-observability`**; при включении — создание коллектора, **`attach`** до шага search, **`detach`** в **`finally`**; вызовы observe **только если** коллектор создан; одна строка в **stderr** с числом зафиксированных стадий (не влияет на основной stdout-отчёт pipeline)

---

## Observability Structure

- **Collector:** список записей `{"stage": str, "data": dict}` — только данные снимков, без ссылок на живые объекты домена в экспорте (dict копии полей).
- **Ограничение объёма:** в каждом снимке списков — не более **`MAX_OBSERVABILITY_ITEMS`** элементов + поля **`total`** / **`truncated`**.
- **Стадии (имена):** `search` → `classification` → `qualification` → `normalization`.

---

## Hook Integration

| После шага в `run.py` | Hook | Покрытие |
|------------------------|------|----------|
| `search_candidates` | `observe_after_search` | raw hits |
| `classify_candidates` | `observe_after_classification` | пары hit + classification (до qualification) |
| `qualify_candidates` | `observe_after_qualification` | строки 2- или 3-кортежа + meta qualification |
| `normalize_candidates` | `observe_after_normalization` | нормализованные кандидаты (pain-only, как и pipeline) |

**Ingestion** в этом IMP **не** инструментируется (вне перечня OP/DEC для MVP). Сигнатуры **`search_candidates`**, **`classify_candidates`**, **`qualify_candidates`**, **`normalize_candidates`**, **`ingest_candidates`** **не** менялись; коллектор **не** передаётся в эти функции.

---

## Activation Mode

- **Вкл.:** CLI **`--discovery-observability`** → создаётся **`PipelineObservabilityCollector`**, **`ContextVar`** устанавливается на время **`try`** блока основного прогона.
- **Выкл. (по умолчанию):** коллектор не создаётся, **`attach`** не вызывается, вызовы **`observe_*`** отсутствуют — практически нулевой вклад в hot path.

---

## Constraints Validation

| Требование | Статус |
|------------|--------|
| Pipeline бизнес-логика не изменена | сервисы pipeline не правились |
| Сигнатуры pipeline функций не изменены | только **`run.py`** оркестрация |
| Нет глобального синглтона коллектора | новый экземпляр на запуск при debug |
| In-memory, один execution context | **`ContextVar`** + **`detach`** в **`finally`** |
| Нет персистентности в БД | только списки в процессе |
| Observability не влияет на результат | те же вызовы и данные, что до IMP; снимки — побочные копии |
| Qualification покрыт | отдельный hook после **`qualify_candidates`** |

---

## Verification

- **`python -m app.discovery.run --query "test" --dry-run`**: stdout совпадает с ожидаемым отчётом pipeline (без флага observability); stderr без строки observability.
- **`python -m app.discovery.run --query "test" --dry-run --discovery-observability`**: stdout тот же по структуре; stderr: **`discovery_observability: stages=4`**.
- Ручная проверка: при включённом режиме в **`collector.export_stages()`** присутствуют стадии **`search`**, **`classification`**, **`qualification`**, **`normalization`** (до **`detach`**).

---

## Conclusion

Реализован минимальный **execution-scoped** observability-слой с четырьмя хуками по фактическому контуру **Search → Classification → Qualification → Normalization**, без изменения результатов pipeline и с заделом под UI через **`get_observability_stages_for_current_execution()`** и структуру **`export_stages()`**.
