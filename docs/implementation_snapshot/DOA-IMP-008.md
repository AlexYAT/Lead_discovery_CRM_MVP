## Metadata
- Project: DOA
- Doc type: implementation_snapshot
- ID: DOA-IMP-008
- Status: accepted
- Date: 2026-04-17
- Parent: DOA-OP-002
- Tags: [lead-discovery, crm, mvp, imp, validation-cycle, human-run-readiness]

# Summary
Документ фиксирует выполнение T01/T02/T03 из `DOA-OP-002`: подготовлен воспроизводимый human-run readiness
путь для запуска MVP человеком перед validation-сценариями.

# Что выполнено в рамках T01/T02/T03
- проведён readiness audit состояния проекта для запуска человеком;
- зафиксирован минимальный runtime dependency file (`requirements.txt`);
- создан runtime guide (`RUN.md`) с полным setup/run path;
- подтверждён фактический запуск приложения по новым инструкциям;
- подтверждена доступность ключевых validation URL (`/`, `/leads`, `/dashboard`).

# Какие gaps readiness были найдены
- отсутствовал файл зависимостей для воспроизводимой установки;
- отсутствовала явная инструкция запуска для человека;
- отсутствовал зафиксированный набор prerequisites и пошаговый launch path.

# Какие файлы созданы/изменены
Созданы:
- `requirements.txt`
- `RUN.md`

Изменён:
- `.gitignore` (добавлен `.venv/` для исключения локального окружения из VCS)

# Какие зависимости зафиксированы
В `requirements.txt` зафиксированы минимальные runtime-зависимости:
- `fastapi`
- `uvicorn`
- `jinja2`
- `python-multipart`

# Как человек теперь поднимает систему
1. Создаёт виртуальное окружение: `python -m venv .venv`
2. Активирует окружение: `.\.venv\Scripts\Activate.ps1`
3. Устанавливает зависимости:
   - `python -m pip install --upgrade pip`
   - `pip install -r requirements.txt`
4. Запускает приложение:
   - `uvicorn app.main:app --host 127.0.0.1 --port 8000`

# Какие URL используются для validation
- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/leads`
- `http://127.0.0.1:8000/dashboard`

# Что сознательно НЕ делалось
- не вносились продуктовые улучшения;
- не менялись UX/flow и бизнес-логика;
- не добавлялись новые функции;
- не выполнялись исправления validation findings.

# Какая проверка выполнена
- синтаксическая проверка Python-файлов (`py_compile`);
- проверен установочный путь зависимостей через `pip install -r requirements.txt`;
- выполнен фактический запуск приложения через `uvicorn`;
- проверена доступность страниц `/`, `/leads`, `/dashboard` (HTTP 200).

# Как это соотносится с `DOA-OP-002`
Результат закрывает блок T01/T02/T03:
- readiness audit выполнен;
- setup/dependencies/run path формализованы;
- человек может воспроизводимо поднять систему для следующего шага validation-cycle.

# Next Steps
- переход к T04 (`validation checklist`).
