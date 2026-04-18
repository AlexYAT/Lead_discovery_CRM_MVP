## Metadata

id: DOA-DEC-013  
type: DEC  
status: accepted  
parent: DOA-ARCH-012  
date: 2026-04-18

---

## Title

Dotenv Loading Policy and Behavior

---

## Decision 1 — Override Policy

Значения, уже заданные в системных переменных окружения, имеют приоритет над значениями из `.env`.

`.env` используется только для заполнения отсутствующих переменных.

---

## Decision 2 — Idempotent Initialization

Environment Initialization выполняется один раз за lifecycle процесса.

Повторные вызовы не должны изменять уже установленное окружение.

---

## Decision 3 — Optional Loading

Если файл `.env` отсутствует:

- система продолжает работу
- используется только текущее окружение процесса
- отсутствие `.env` не является ошибкой

---

## Decision 4 — Scope of Application

Инициализация применяется только для локального runtime:

- CLI запуск
- локальная разработка
- агентские subprocess (если они используют тот же entrypoint)

---

## Decision 5 — Single Entry Point

Загрузка `.env` должна происходить:

- в одной точке
- до первого обращения к Config Layer

---

## Constraints

- не менять env contract
- не менять pipeline
- не читать `.env` вне init слоя
- не читать os.environ вне config layer
