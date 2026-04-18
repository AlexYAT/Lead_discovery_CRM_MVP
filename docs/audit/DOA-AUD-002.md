# DOA-AUD-002 — Audit of Discovery CLI Execution Cycle

## Metadata

- id: DOA-AUD-002
- type: AUD
- parent: DOA-VAL-006
- status: accepted
- date: 2026-04-18

---

## Title

Audit of Discovery CLI Execution Cycle

---

## Audit Scope

1. **Traceability:** DOA-DEC-007 → DOA-OP-007-A → DOA-IMP-030 → DOA-VAL-006  
2. **Architectural consistency:** решение DEC отражено в IMP (CLI entrypoint)  
3. **Validation consistency:** VAL-006 описывает поведение, согласованное с кодом и IMP-030  
4. **Baseline limitations:** mock search, stub/LLM контракт классификации, `--source` только лог, отсутствие automation/trigger слоя  

---

## Reviewed Artifacts

- **DOA-DEC-007** (`docs/decisions/DOA-DEC-007.md`) — принят CLI как базовый execution entrypoint (`python -m app.discovery.run`).  
- **DOA-OP-007-A** (`docs/operations/DOA-OP-007-A.md`) — расширение OP-007: шаги CLI, argparse, orchestration, dry-run, логирование.  
- **DOA-IMP-030** (`docs/implementation_snapshot/DOA-IMP-030.md`) — фиксация реализации `app/discovery/run.py` и поведения флагов.  
- **DOA-VAL-006** (`docs/validation/DOA-VAL-006.md`) — прогон команд dry-run / normal / import / контракт `--llm` / `--source`.  

---

## Findings

### Finding 1 — Traceability is preserved

Цепочка DEC → OP extension → IMP snapshot → VAL закрыта без разрыва идентификаторов: parent у OP-007-A указывает на OP-007, IMP-030 — на OP-007-A, VAL-006 — на IMP-030, настоящий AUD — на VAL-006.

### Finding 2 — IMP matches actual code state

В репозитории присутствует `app/discovery/run.py` с `argparse`, цепочкой search → classification → normalization → ingestion (с `--dry-run`), поведением `--llm` через окружение — как описано в IMP-030.

### Finding 3 — Validation is sufficient for current baseline

VAL-006 фиксирует выполненные команды, счётчики и контракт флагов; для текущего MVP (mock search, опциональный LLM) этого достаточно, полный E2E с реальным Brave не входил в объём цикла.

### Finding 4 — Execution layer is operational but still baseline-limited

CLI запускает pipeline детерминированно, но качество и объём данных по-прежнему ограничены mock search и эвристикой/LLM-контрактом; production-grade discovery не заявлен.

---

## Risks

- **`--source`** не меняет семантику пайплайна (только лог); при расширении каналов легко забыть синхронизировать с нормализацией.  
- **Search** остаётся mock/stub — риск ложного чувства полноты интеграции.  
- **`--llm`** завязан на временное изменение `OPENAI_API_KEY` в процессе CLI — нет отдельного выделенного config contract; при параллельных процессах возможны коллизии окружения.  
- **Automation/trigger** (cron, API) отсутствует — ручной запуск CLI единственный зафиксированный entrypoint.

---

## Conclusion

Execution cycle по CLI согласован с DocOps-цепочкой и валидирован; baseline ограничений принят осознанно. Следующий логичный шаг — **discussion-first** перед новым циклом (реальный search provider, config contract для LLM/source, automation), без автоматического запуска нового IDEA.
