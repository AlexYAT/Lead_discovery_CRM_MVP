# DOA-IDEA-008 — Config Layer Extension for API Keys (.env contract)

## Metadata

- id: DOA-IDEA-008
- type: IDEA
- parent: DOA-AUD-004
- status: proposed
- date: 2026-04-18

---

## Title

Config Layer Extension for API Keys (.env contract)

---

## Problem

После завершённого цикла Config Layer (**DOA-IDEA-007** … **DOA-AUD-004**) в `DiscoveryConfig` централизованы `llm_enabled`, `source` и `default_limit`, но **API-ключи** для внешних сервисов по-прежнему не являются частью явного контракта конфигурации.

Проблемы:

- **`OPENAI_API_KEY`** читается по месту использования (implicit env), а не через единый config object  
- **`BRAVE_API_KEY`** отсутствует в модели конфигурации и не задокументирован как обязательная часть MVP-контракта  
- нет **явного `.env` contract** (какие переменные ожидаются, для чего, в каком слое они читаются)

Это блокирует:

- предсказуемую **интеграцию Brave** (поиск)  
- **предсказуемость** конфигурации между окружениями  
- **reproducibility** (один и тот же набор параметров и секретов описан в одном месте)

---

## Idea

Расширить Config Layer поддержкой API-ключей через переменные окружения:

- **`BRAVE_API_KEY`**
- **`OPENAI_API_KEY`**

Включить их в **`DiscoveryConfig`** и обеспечить **централизованный доступ** (загрузка при старте orchestration, передача в слои search / classification без разрозненного `os.environ.get` как основного паттерна).

---

## Scope (MVP)

- чтение API-ключей из env в рамках discovery config module  
- доступ к значениям (включая «отсутствует» / пусто) **через config object**  
- постепенный отказ от **implicit** чтения env в downstream-коде в пользу явных полей config (цель цикла ARCH/DEC/IMP)

---

## Non-Goals

- отдельное **secrets storage**  
- **encryption** ключей на диске  
- **vault** и иные enterprise secret managers  

---

## Expected Outcome

- **единый config contract** для всех внешних интеграций discovery (лимиты, флаги, ключи)  
- **готовность к Brave API** за счёт явного места для ключа в конфигурации  
- **прозрачное управление зависимостями**: документированный `.env` contract и предсказуемое поведение при отсутствии ключей

---

## Next

→ **DOA-ARCH-008**
