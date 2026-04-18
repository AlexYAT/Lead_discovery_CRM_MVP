# DOA-IDEA-009 — Environment Configuration Contract for Discovery Pipeline

## Metadata

- id: DOA-IDEA-009
- type: IDEA
- parent: DOA-AUD-004
- status: proposed
- date: 2026-04-18

---

## Title

Environment Configuration Contract for Discovery Pipeline

---

## Problem

После **DOA-IMP-032** API keys попали в **Config Layer** и читаются в **`app/discovery/config.py`**, но для оператора и разработчика по-прежнему нет **единого, явного** контракта окружения:

- нет **`.env.example`** в репозитории  
- нет сводного списка **всех** поддерживаемых переменных discovery с пояснением  
- неочевидно, что **обязательно**, что **опционально**, какие **значения по умолчанию** и как они влияют на pipeline  

Это ведёт к:

- слабому **DX** (onboarding, handover)  
- ошибкам и лишнему времени на отладку «почему не LLM / почему stub»  
- **неявным** ожиданиям относительно поведения без `.env`  

---

## Idea

Ввести явный **environment contract** для discovery:

- файл **`.env.example`** в корне проекта (шаблон без секретов)  
- перечень поддерживаемых переменных с кратким описанием  
- задокументированное поведение значений (в т.ч. defaults и optional/required)  

**Config Layer** остаётся **единственной точкой чтения** env для discovery; контракт лишь фиксирует ожидания и согласуется с уже принятой моделью (**ARCH-008**, **IMP-032**).

---

## Scope (MVP)

- добавить **`.env.example`** (плейсхолдеры, без реальных ключей)  
- описать переменные:  
  - `OPENAI_API_KEY`  
  - `BRAVE_API_KEY`  
  - `DISCOVERY_LLM_ENABLED`  
  - `DISCOVERY_SOURCE`  
  - `DISCOVERY_DEFAULT_LIMIT`  
- в том же цикле документации (ARCH/OP или README-фрагмент по решению следующего шага) зафиксировать:  
  - **default** значения (в духе текущего кода)  
  - статус **optional / required**  
  - **влияние на pipeline** (LLM vs stub, mock search, лимиты, метки source)  

---

## Non-Goals

- новая зависимость **`python-dotenv`** (загрузка `.env` остаётся вне этого IDEA, как сегодня)  
- **secrets storage**, vault, шифрование  
- **runtime reload** конфигурации без перезапуска процесса  

---

## Expected Outcome

- быстрый и **понятный onboarding** для запуска discovery  
- **воспроизводимость** локального запуска при согласованном наборе переменных  
- меньше **implicit assumptions** за счёт явного шаблона и описания контракта  

---

## Next

→ **DOA-ARCH-009**
