# DOA-DEC-011 — Search Provider Integration Decisions

## Metadata

- id: DOA-DEC-011
- type: DEC
- parent: DOA-ARCH-010
- status: accepted
- date: 2026-04-18

---

## Title

Search Provider Integration Decisions

---

*Примечание DocOps: идентификатор **DOA-DEC-010** зарезервирован решением **Environment Configuration Contract** (`parent: DOA-ARCH-009`). Решения по интеграции Brave Search оформлены как **DOA-DEC-011**.*

---

## Decision 1 — Provider Selection Control

**Решение:**

Выбор между **live provider** и **mock** осуществляется на уровне **orchestration** (до или при вызове Search Adapter), а не внутри adapter как скрытая эвристика.

**Обоснование:**

- сохраняется простота **Search Adapter** (делегирование одному выбранному backend)  
- исключается **смешение ответственности** между «политикой режима» и «вызовом API»  
- повышается **прозрачность** управления поведением системы для оператора и тестов  

---

## Decision 2 — Provider Contract

**Решение:**

Provider обязан возвращать данные **сразу** в формате **`SearchHit`** (или эквивалентном списке, совместимом с текущим контрактом модели), без промежуточного типа, требующего отдельной нормализации на границе pipeline.

**Обоснование:**

- упрощается **pipeline** и orchestration  
- исключается **дополнительная нормализация** на стыке search → classification  
- сохраняется **единый контракт downstream** (как при mock baseline)  

---

## Decision 3 — Fallback Strategy

**Решение:**

Используется **graceful fallback**:

- при **отсутствии** API key (или явном «degraded» сигнале из config) → **mock**  
- при **ошибках** live provider (сеть, HTTP-ошибки, невалидный ответ — детали на IMP) → **mock**  

**Обоснование:**

- соответствует **MVP** и уже принятому **env contract** (optional keys)  
- обеспечивает **стабильность** pipeline без hard fail CLI  
- согласуется с **ARCH-010** (fallback на mock того же контракта)  

---

## Decision 4 — Degradation Control

**Решение:**

Вводится политика **контролируемой деградации**: использование **timeout** и отказ от **неограниченно блокирующих** операций на пути live provider (конкретные числа секунд и политика retry **не** фиксируются на уровне DEC — перенос на OP/IMP).

**Обоснование:**

- предотвращает **зависание** pipeline при сбоях внешнего API  
- обеспечивает **предсказуемое** поведение деградации в сторону mock  

---

## Constraints

- **не** изменять контракт и семантику **downstream** стадий (classification / normalization / ingestion) в рамках этого решения  
- **не** расширять scope за пределы **поиска** и интеграции provider  
- **не** добавлять **продуктовые** функции под видом поиска (UI, CRM, коммуникации)  
