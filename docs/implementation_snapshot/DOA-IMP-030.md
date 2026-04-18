# DOA-IMP-030 — CLI Execution Entry Point

## Metadata

- id: DOA-IMP-030
- type: IMP
- parent: DOA-OP-007-A
- status: implemented
- date: 2026-04-18

---

## Title

CLI Execution Entry Point

---

## Summary

Реализован CLI entrypoint для запуска discovery pipeline.

Добавлен orchestration слой:

Search → Classification → Normalization → Ingestion

---

## Files

- app/discovery/run.py

---

## Behavior

- поддержка CLI параметров
- поддержка dry-run
- поддержка LLM flag (без изменения classification-модулей: при отсутствии `--llm` на время прогона снимается `OPENAI_API_KEY`, чтобы принудительно использовать stub; с `--llm` используется текущее окружение)
- вывод статистики выполнения
- параметр `--source` выводится в лог (контракт нормализации по-прежнему фиксирует `vk` в слое IMP-028)

---

## Verification

Команда:

python -m app.discovery.run --query "астролог" --limit 5

Результат:

- pipeline выполняется
- кандидаты обрабатываются
- ingestion вызывается (если не dry-run)

Дополнительно проверено:

- `python -m app.discovery.run --query "астролог" --limit 5 --dry-run` — ingestion не вызывается, в логе `saved=0 (dry-run)`
- прогон с pain-like запросом без `--dry-run` создаёт строки в Candidate Queue (`saved` > 0 при наличии pain-hits)
