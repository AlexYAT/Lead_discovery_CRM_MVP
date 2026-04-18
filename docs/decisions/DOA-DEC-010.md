# DOA-DEC-010 — Environment Configuration Contract for Discovery Pipeline

## Metadata

- id: DOA-DEC-010
- type: DEC
- parent: DOA-ARCH-009
- status: accepted
- date: 2026-04-18

---

## Title

Environment Configuration Contract for Discovery Pipeline

---

## Context

После **DOA-IMP-032** discovery pipeline читает env **только** через **Config Layer** (`app/discovery/config.py`), но в репозитории по-прежнему **нет** **`.env.example`** и нет **user-facing** описания поддерживаемых переменных. **DOA-IDEA-009** и **DOA-ARCH-009** вводят явный контракт: шаблон env + документация, без смены runtime-модели и без новых зависимостей.

---

## Decision

1. В корень репозитория добавляется **`.env.example`** как **единственный** шаблон переменных окружения для discovery baseline (реализация в **OP-010** / **IMP**).  
2. **Documentation fragment** размещается в **README** отдельной **секцией** (то же содержание по смыслу, что и таблица/список в `.env.example`).  
3. **`.env.example`** и **README** содержат **одинаковый набор** переменных:  
   - `OPENAI_API_KEY`  
   - `BRAVE_API_KEY`  
   - `DISCOVERY_LLM_ENABLED`  
   - `DISCOVERY_SOURCE`  
   - `DISCOVERY_DEFAULT_LIMIT`  
4. На baseline **все** перечисленные переменные считаются **optional** (отсутствие — валидное состояние).  
5. Отсутствие переменных **не ломает** pipeline: допускаются **stub** / **fallback** пути (согласовано с текущим поведением после **IMP-032** / **DEC-009**).  
6. **Runtime** по-прежнему читает env **только** через **config layer**; DEC не вводит альтернативных путей чтения.  
7. **Секреты:** не передаются через **CLI**, не **логируются**, в **`.env.example`** только **плейсхолдеры**, без реальных значений в VCS.  

---

## Rationale

- Улучшение **DX** и **onboarding** без смены архитектуры strict config-only.  
- Снижение **implicit assumptions** за счёт явного списка и defaults в README + шаблоне.  
- Сохранение **fallback-safe** baseline (mock search, stub LLM при отсутствии ключей).  
- Согласованность с уже принятой моделью ключей и orchestration (**ARCH-008**, **DEC-009**, **IMP-032**).  

---

## Alternatives Considered

### A — только `.env.example` без расширения README

**Отклонено:** слабая discoverability для нового участника; ARCH-009 предполагает и файл, и краткую пользовательскую документацию.

### B — отдельный doc в `docs/` вместо README

**Отклонено:** хуже видимость при первом открытии репозитория; README остаётся каноническим входом.

### C — сделать API keys **required**

**Отклонено:** ломает stub/mock baseline и локальный запуск без секретов.

---

## Consequences

**Положительные:**

- прозрачный запуск и воспроизводимость среды при согласованном `.env`  
- единый **контракт** списка переменных для оператора и кода  

**Негативные / риски:**

- необходимость **синхронизации** README и **`.env.example`** при изменениях  
- риск **рассинхрона** с `app/discovery/config.py`, если список переменных расширят без обновления артефактов контракта  

---

## Next

→ **DOA-OP-010**
