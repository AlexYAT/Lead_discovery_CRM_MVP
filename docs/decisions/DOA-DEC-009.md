# DOA-DEC-009 — Decision on API Key Handling in Config Layer (Discovery)

## Metadata

- id: DOA-DEC-009
- type: DEC
- parent: DOA-ARCH-008
- status: accepted
- date: 2026-04-18

---

## Title

Decision on API Key Handling in Config Layer (Discovery)

---

## Context

**DOA-IDEA-008** фиксирует необходимость явного контракта для внешних интеграций. **DOA-ARCH-008** задаёт **strict config-only**: ключи в `DiscoveryConfig`, чтение env только в config module, downstream без implicit `os.environ` для секретов.

Проблема до внедрения цикла:

- API keys **не** входят в явный config contract  
- используется **implicit** доступ к env в search/classification  
- нужна единая модель для **Brave** и **LLM** поверх уже принятого merge CLI/env (**DEC-008**)  

Пользователь подтвердил решения ниже.

---

## Decision

### 1. Storage model

API keys хранятся **напрямую** в `DiscoveryConfig`:

- `openai_api_key: str | None`  
- `brave_api_key: str | None`  

Значения загружаются из env в config module и **нормализуются** (пустая строка → `None`).

---

### 2. Access model

- Ключи передаются **явно** в вызовы downstream:  
  - **search layer** получает `brave_api_key` (и прочие execution-параметры по существующим правилам)  
  - **classification layer** получает `openai_api_key` и **`llm_enabled`** (и связанные явные параметры поведения)  
- **Запрещён** implicit доступ к env в downstream для этих секретов (повторное «дочитывание» как основной путь).  
- **Не** используется глобальный доступ к config из глубины стека вместо явных аргументов: контракт вызова остаётся читаемым на границе orchestration → provider/service.

---

### 3. Missing key behavior

- Отсутствие ключа (`None`) **допустимо** на уровне config.  
- Поведение задаёт **orchestration** и контракт шага:  
  - **LLM** → graceful **stub / fallback** path при отсутствии ключа или при `llm_enabled=False`  
  - **search** → провайдер недоступен или **fallback** (mock / degraded), **без hard fail** в MVP  
- **Запрещён** скрытый fallback через повторное чтение env для того же секрета.  

---

## Rationale

- Убирает **hidden dependencies** и дублирование источника истины.  
- Конфигурация интеграций становится **полностью явной** в объекте + сигнатурах вызовов.  
- Упрощает **тестирование** (передача `None` / фиктивных значений без подмены процесса) и **validation** снимков.  
- Согласуется со **strict config-only** из **ARCH-008**.

---

## Alternatives Considered

### A — хранить только derived flags

**Отклонено:** недостаточно для реальных HTTP-вызовов к Brave/OpenAI без дублирования env в другом месте.

### B — передавать весь `DiscoveryConfig` в каждый downstream

**Отклонено:** снижает явность контрактов функций и усиливает связность слоёв.

### C — implicit env access в providers

**Отклонено:** противоречит **IDEA-008** и **ARCH-008**.

### D — hard fail при отсутствии ключа

**Отклонено:** ломает MVP/stub и локальный dry-run без полного набора секретов.

---

## Consequences

- Сигнатуры search/classification (и смежных сервисов) будут **расширены** явными параметрами ключей / поведения.  
- **Orchestration** (`run.py` и аналоги) остаётся **единственной точкой** сборки интеграционного контекста из config.  
- Появляется **единый config contract** для внешних сервисов discovery.  
- Система **готова** к поэтапной интеграции **Brave API** без смены архитектурного принципа.

Следующий шаг: **→ DOA-OP-009**
