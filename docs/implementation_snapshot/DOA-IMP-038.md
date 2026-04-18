# DOA-IMP-038 — Discovery Observability Debug View (CLI) Snapshot

## Metadata

- id: DOA-IMP-038
- type: IMP
- status: implemented
- parent: DOA-OP-015
- date: 2026-04-18

---

## Title

Discovery Observability Debug View (CLI) Implementation Snapshot

---

## Summary

Реализован **CLI debug view** поверх существующих observability-снимков (**DOA-IDEA-014**, **DOA-ARCH-014**, **DOA-DEC-015**, **DOA-OP-015**): режимы **stage** и **diff**, **read-only** доступ к данным через **`read_debug_stages()`** (сначала **`get_observability_stages_for_current_execution()`**, иначе **`collector.export_stages()`** после detach). Идентичность кандидатов для diff — **DOA-DEC-015** (`source_link`, иначе **SHA-256** текста, 16 hex). **Pipeline**, **hooks** и **контракт collector** не менялись.

---

## Implemented Changes

| Файл | Изменение |
|------|-----------|
| **`app/discovery/observability/debug_cli.py`** | **новый**: парсинг **`--discovery-debug-diff`**, **`read_debug_stages`**, **`candidate_identity`**, **`render_stage_view_lines`**, **`render_diff_view_lines`** (симметричный хвост diff) |
| **`app/discovery/run.py`** | mutually exclusive **`--discovery-debug-stage`** / **`--discovery-debug-diff`**; проверка «только вместе с **`--discovery-observability`**» (**`sys.exit(2)`**); после прогона вывод observability и debug в **stderr** с **`flush=True`**; основной отчёт pipeline — по-прежнему **stdout** |

**Не менялись:** `collector.py`, `hooks.py`, `context.py`, `access.py`, `snapshots.py`, сервисы pipeline.

---

## CLI Debug Modes

| Режим | Флаг | Условие |
|--------|------|---------|
| **Stage view** | `--discovery-debug-stage` + одна из стадий: `search`, `classification`, `qualification`, `normalization` | обязателен **`--discovery-observability`** |
| **Diff view** | `--discovery-debug-diff A,B` (две стадии через запятую) | то же |

Без **`--discovery-observability`**: debug-флаги → сообщение **`discovery_debug: error: ...`** в stderr и код выхода **2** (pipeline не выполняется).

---

## Identity and Diff Logic

- **Primary:** непустой **`source_link`** из снимка (для search / normalization — верхний уровень; для classification / qualification — внутри **`hit`**).
- **Fallback:** **`text:{sha256(text)[:16]}`** по нормализованной строке текста (стабильно между стадиями при неизменном тексте).
- **Diff:** множество идентичностей стадии **A** минус стадия **B** как основной сценарий «отфильтровано относительно B»; дополнительно блок **symmetric** «только в B, не в A».

---

## Output Behavior

- **stdout:** только прежние строки метрик pipeline (без префикса `discovery_debug:`).
- **stderr:** `discovery_observability: stages=…`, затем блок **stage** или **diff** (все строки с префиксом **`discovery_debug:`**), **`flush=True`** чтобы при объединении потоков (**`2>&1`**) не перемешивались с stdout.

---

## Constraints Validation

| Требование | Статус |
|------------|--------|
| Pipeline не изменён | логика шагов в сервисах не трогалась |
| Observability hooks / collector contract | без изменений |
| Только read-only поверх снимков | нет записи в collector после export |
| **DEC-015** identity | реализовано в **`candidate_identity`** |
| Debug без observability | явный отказ, exit **2** |

---

## Verification

- **`python -m app.discovery.run --query t --dry-run --discovery-debug-stage search`** → stderr: ошибка про **`--discovery-observability`**, код **2**, pipeline не запускается.
- **`python -m app.discovery.run --query t --dry-run --discovery-observability --discovery-debug-stage search`** → stderr: заголовок stage, **total/truncated**, строки **`[n] id=link:…`**; stdout — прежние строки отчёта.
- **`python -m app.discovery.run --query t --dry-run --discovery-observability --discovery-debug-diff search,normalization`** → stderr: diff **search → normalization**, **count=10** для mock без pain; stdout без изменений по смыслу отчёта.
- Без debug-флагов поведение как в **DOA-IMP-037** (одна строка **`discovery_observability`** при включённом observability).

---

## Conclusion

CLI **stage** / **diff** поверх **`export_stages()`** / попытки **`get_observability_stages_for_current_execution()`** закрывает **DOA-OP-015** для локального анализа без UI и без смены семантики observability; следующий цикл — отдельный веб/UI при необходимости.
