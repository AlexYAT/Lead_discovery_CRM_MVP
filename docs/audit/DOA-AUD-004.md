# DOA-AUD-004 — Audit of Config Layer Lifecycle (Discovery)

## Metadata

- id: DOA-AUD-004
- type: AUD
- status: accepted
- date: 2026-04-18
- parent: DOA-VAL-007

---

## Title

Audit of Config Layer Lifecycle (Discovery)

---

## Audit Scope

Проверено по цепочке **DOA-IDEA-007 → DOA-ARCH-007 → DOA-DEC-008 → DOA-OP-008 → DOA-IMP-031 → DOA-VAL-007**:

1. **Полнота lifecycle** — наличие и связность артефактов от идеи до валидации.  
2. **Соответствие реализации DEC-008** — точка merge, управление LLM, семантика `source`.  
3. **Корректность config precedence** — согласованность с ARCH (CLI → env → defaults).  
4. **Отсутствие скрытых env-hack** — отказ от runtime-манипуляции `OPENAI_API_KEY` как основного переключателя режима в orchestration.  
5. **Влияние на pipeline** — классификация и оркестрация используют явный config; ingestion/normalization contract не расширен за рамки DEC.

---

## Reviewed Artifacts

- `docs/ideas/DOA-IDEA-007.md`  
- `docs/architecture/DOA-ARCH-007.md`  
- `docs/decisions/DOA-DEC-008.md`  
- `docs/operations/DOA-OP-008.md`  
- `docs/implementation_snapshot/DOA-IMP-031.md`  
- `docs/validation/DOA-VAL-007.md`  

---

## Findings

1. **Config layer централизован (env + CLI).** IDEA-007 и ARCH-007 задали единый модуль и модель `DiscoveryConfig`; IMP-031 фиксирует `app/discovery/config.py`, загрузку `DISCOVERY_*` и `merge_cli_overrides`; VAL-007 подтверждает defaults и overrides на CLI.

2. **Env-hack с временным удалением `OPENAI_API_KEY` устранён из orchestration.** DEC-008 и OP-008 требуют явного `llm_enabled`; IMP-031 описывает удаление hack из `run.py`. Точечная проверка кода `app/discovery` не показывает подмены/удаления ключа в `run.py`; чтение `OPENAI_API_KEY` остаётся **условием готовности** LLM-пути (classifier / metadata), а не скрытым переключателем через env в orchestration.

3. **Явный contract `llm_enabled` вместо implicit-only поведения.** DEC-008 п.2 закреплён: orchestration передаёт флаг downstream; VAL-007 проверяет `--llm` / `--no-llm` и соответствие первой строки лога.

4. **CLI precedence согласован с ARCH-007.** Правило CLI → env → hardcoded defaults отражено в плане OP-008 и проверено VAL-007 (check 2: `--limit` / `--source` перекрывают baseline при сброшенных `DISCOVERY_*`).

5. **`source` остаётся execution-level, pipeline не ломает ingestion schema.** DEC-008 п.3, VAL-007 Notes и IMP-031 согласованы: `source` в логе и search/orchestration без заявленного изменения normalization/ingestion semantics в этом цикле.

6. **Валидация достаточна для нового baseline.** VAL-007 (status passed) закрывает defaults, precedence, флаги LLM, нормальный прогон и import safety — в объёме, заявленном для config layer MVP.

---

## Risks

1. **`source`** по-прежнему execution-level: операторы могут ожидать end-to-end семантику канала; без отдельного ARCH/DEC цикла риск неверных интерпретаций логов vs данных в БД.

2. **Фактический LLM** зависит от внешнего **`OPENAI_API_KEY`** и инфраструктуры модели: `llm_enabled=True` не гарантирует вызов API при отсутствии ключа (stub-path), что уже зафиксировано в VAL-007.

3. **Нет строгой валидации значений env** для `DISCOVERY_*` (типизация/диапазоны): невалидные строки могут приводить к fallback или неочевидному поведению без явной ошибки конфигурации.

---

## Conclusion

Config Layer lifecycle is complete and accepted as new baseline.
