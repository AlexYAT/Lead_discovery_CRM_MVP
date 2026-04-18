# DOA-OP-011 — Brave Search Integration Implementation Plan

## Metadata

- id: DOA-OP-011
- type: OP
- parent: DOA-DEC-011
- status: planned
- date: 2026-04-18

---

## Title

Brave Search Integration Implementation Plan

---

## Objective

Зафиксировать **минимальный воспроизводимый** план внедрения **реального** search provider (**Brave Search**) в существующий discovery pipeline (**DOA-IDEA-010**, **DOA-ARCH-010**, **DOA-DEC-011**) **без** изменения контракта и семантики **downstream** стадий (classification → normalization → ingestion).

---

## Scope

**В рамках плана (MVP, только search integration):**

- подключение **live** search path через принятый **adapter / provider** подход (**ARCH-010**, **DEC-011**)  
- использование существующего **Config Layer** и **API key** / **env contract** (без новых переменных сверх baseline, если не решено иначе в отдельном DEC)  
- сохранение **fallback на mock** при отсутствии ключа и при ошибках live path (**DEC-011 Decision 3**)  
- сохранение текущего **контракта выхода** search — список **`SearchHit`** для downstream (**DEC-011 Decision 2**)  

**Вне scope:**

- ranking / scoring improvements  
- query tuning как отдельный продуктовый цикл  
- multi-provider support  
- UI changes  
- CRM / product feature expansion  

---

## Work Items

### T01 — Search adapter integration path

Определить единый operational шаг: **orchestration** вызывает **Search Adapter** (или эквивалентную единую точку), а не конкретный Brave-класс напрямую; **выбор live vs mock** остаётся на уровне orchestration (**DEC-011 Decision 1**).

### T02 — Brave provider implementation path

Определить operational шаг: первая **live** реализация за интерфейсом provider выполняет HTTP/SDK вызовы к **Brave** и маппит ответ в **`SearchHit`**; mock остаётся отдельной реализацией того же контракта.

### T03 — Config-driven mode selection

Определить operational шаг: режим и ключ берутся из уже загруженного **`DiscoveryConfig`** / явных аргументов orchestration; **не** вводить чтение секретов через **`os.environ`** в provider вне **config layer** (**strict config-only** baseline).

### T04 — Graceful fallback behavior

Определить operational шаг: при отсутствии ключа или при ошибке live path — **возврат к mock** с тем же типом результата, без прерывания всего CLI (**DEC-011 Decision 3**).

### T05 — Controlled degradation

Определить operational шаг: для live path задать **timeout** и избегать неограниченно блокирующих вызовов; детали чисел и минимальный retry (если есть) — на уровне IMP, **без** enterprise policy (**DEC-011 Decision 4**).

### T06 — Verification-ready implementation snapshot target

Зафиксировать: итоговая реализация оформляется **IMP snapshot** + последующий **VAL** (по необходимости **AUD**) **в том же продуктовом scope** — без расширения функциональности за пределы поиска.

---

## Done Definition

План считается выполненным как **operational artifact**, если:

- перечислены все шаги реализации (**T01–T06**)  
- план явно привязан к **DOA-DEC-011** (и вышестоящим **IDEA-010** / **ARCH-010**)  
- **scope** ограничен **только** search integration  
- downstream контракт заявлен **неизменным** (`SearchHit` → существующий pipeline)  
- предусмотрен **fallback на mock** при деградации  

---

## Next

→ **DOA-IMP-034**
