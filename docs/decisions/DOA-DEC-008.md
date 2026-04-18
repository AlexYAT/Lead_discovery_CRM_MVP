# DOA-DEC-008 — Decision on Config Merge and Execution Semantics for Discovery Pipeline

## Metadata

- id: DOA-DEC-008
- type: DEC
- parent: DOA-ARCH-007
- status: accepted
- date: 2026-04-18

---

## Title

Decision on Config Merge and Execution Semantics for Discovery Pipeline

---

## Context

Execution layer уже реализован через CLI (IMP-030, VAL-006). **DOA-IDEA-007** вводит Config Layer для устранения env-hack и централизации параметров. **DOA-ARCH-007** задаёт локальный discovery config module, модель `DiscoveryConfig` и precedence **CLI → env → defaults**. Перед DEC выполнен analyze; пользователь подтвердил три решения ниже.

---

## Decision

### 1. Config merge point

Итоговый merge конфигурации выполняется в **`app/discovery/run.py`**.

`run.py`:

- читает env-базу через config module;
- применяет CLI overrides;
- строит итоговый **`DiscoveryConfig`**;
- передаёт downstream уже нормализованные значения.

### 2. LLM control

Переключение LLM выполняется через явное поле **`llm_enabled: bool`** в config.

Оркестрация использует этот флаг как входной параметр и **не** должна полагаться на **runtime-manipulation `OPENAI_API_KEY`** как на основной механизм управления режимом.

### 3. Source semantics

Поле **`source: str`** на этапе DEC-008 фиксируется как **execution-level** parameter.

Это означает:

- может использоваться CLI / config / search orchestration;
- **не** меняет downstream semantics normalization/ingestion в рамках этого цикла;
- end-to-end source semantics требует **отдельного** ARCH/DEC цикла.

---

## Rationale

- Merge в **`run.py`** — одна точка истины и предсказуемый порядок override.  
- **`llm_enabled`** делает режим явным, тестируемым и независимым от скрытой подмены env.  
- Ограничение **`source`** сохраняет scope MVP и не смешивает Config Layer с перепроектированием контракта нормализации/ingestion.

---

## Alternatives Considered

### Alternative A — split merge between config.py and run.py

**Отклонено:** логика размазывается, выше риск рассинхрона и дублирования precedence.

### Alternative B — classifier keeps reading env directly

**Отклонено:** сохраняет env-hack, противоречит целям Config Layer (IDEA-007 / ARCH-007).

### Alternative C — make source end-to-end semantic now

**Отложено:** выходит за scope текущего цикла; требует отдельного решения по normalization/ingestion contract.

---

## Consequences

- Следующий шаг: **DOA-OP-008** (операционный план внедрения config + рефактор orchestration).  
- Реализация вводит **локальный config module** в discovery scope.  
- **`run.py`** перестаёт использовать env-hack для переключения LLM.  
- **`source`** пока остаётся ограниченным execution parameter.  
- Downstream **API** и **schema** не меняются в рамках этого решения.
