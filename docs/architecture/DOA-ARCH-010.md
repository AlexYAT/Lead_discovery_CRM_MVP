# DOA-ARCH-010 — Search Provider Integration Architecture

## Metadata

- id: DOA-ARCH-010
- type: ARCH
- parent: DOA-IDEA-010
- status: proposed
- date: 2026-04-18

---

## Title

Search Provider Integration Architecture

---

## Overview

**DOA-IDEA-010** фиксирует необходимость заменить **mock** search на **реальный** источник данных (**Brave Search**), не ломая текущий контур **Search → Classification → Normalization → Ingestion**.

Сейчас recall синтетический: downstream получает структурно корректные `SearchHit`, но **не** отражает реальный веб-поиск. Цель архитектуры — ввести реальный provider **точечно** в слое поиска, сохранив контракт входа/выхода для остальных стадий и уже принятый **Config Layer** с **API keys** и **env contract**.

---

## Architectural Approach

Вводится отдельный слой:

### Search Adapter Layer

**Назначение:**

- **изолировать** внешний provider от остального pipeline (оркестрация и downstream не зависят от деталей HTTP/SDK Brave)  
- **единый контракт** поиска: один вход (query, limit, контекст из config) и список **`SearchHit`** на выходе, как сегодня  
- **совместимость с mock**: mock остаётся валидной реализацией того же контракта (dev, тесты, деградация)  

Adapter выбирает или делегирует конкретному **provider implementation**; pipeline выше вызывает только adapter-абстракцию.

---

## Components

### Search Adapter

- **Единая точка входа** для recall в discovery (замена прямого вызова конкретного класса provider из orchestration).  
- **Не** зависит от конкретного vendor API: знает только интерфейс «поиск по строке с лимитом».  
- Получает уже **нормализованные из config** параметры, необходимые для выбора режима (в т.ч. наличие ключа / флаги), без чтения секретов из **`os.environ`** внутри adapter как основного пути (**strict config-only** baseline).  

### Provider Implementation

- **Brave Search** — первая реализация за интерфейсом provider.  
- **Расширяемость:** та же граница adapter/provider позволяет в будущем добавить другой backend без смены сигнатуры pipeline (вне scope текущего MVP).  

### Existing Pipeline

- **Classification → Normalization → Ingestion** остаются **без изменения контракта**: на вход по-прежнему список **`SearchHit`** (текст, ссылка и пр. поля модели).  
- Orchestration продолжает вызывать **один** поисковый entrypoint; меняется только реализация «за» adapter.  

---

## Interaction Model

Высокоуровневая цепочка:

**Pipeline (orchestration)** → **Search Adapter** → **Provider (Brave)** → **External API**

При отключённом или недоступном live-пути adapter может вернуть результат **того же контракта** через **mock provider** (см. Failure Handling), не нарушая тип выходных данных.

---

## Config Integration

- Используется **существующий** **Config Layer**: ключ и флаги уже присутствуют в **`DiscoveryConfig`** / env contract (**IMP-032**, **IMP-033**).  
- **API key** для Brave поступает в provider **через явные параметры** из orchestration (как для текущего mock-пути с `brave_api_key`), **без** прямого **`os.environ`** в search слое как основного доступа к секрету.  
- Решение «live vs mock» принимается на уровне **adapter / orchestration** на основе уже загруженного config, согласованно с graceful-поведением baseline.  

---

## Failure Handling

- При **ошибке** live provider (сеть, HTTP 4xx/5xx, пустой ответ, таймаут — детали на этапе DEC/IMP): **fallback на mock search** с тем же контрактом **`SearchHit`**, чтобы pipeline не прерывался и downstream оставался вызываемым.  
- Отсутствие ключа или явный «degraded» режим трактуются как сигнал к **mock path** без hard fail всего CLI (в духе уже принятого MVP для отсутствующих секретов).  

---

## Constraints

- **Не** менять контракт и семантику **downstream** стадий (classification / normalization / ingestion) в рамках этого архитектурного цикла.  
- **Не** добавлять новые **продуктовые** функции (UI, CRM, автоматизация коммуникаций) под видом поиска.  
- **Не** расширять scope за пределы **поиска** и интеграции provider (без multi-provider продукта, без ranking-слоя как обязательной части).  
