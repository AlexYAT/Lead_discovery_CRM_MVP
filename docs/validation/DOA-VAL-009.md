# DOA-VAL-009 — Brave Search Integration Validation

## Metadata

- id: DOA-VAL-009
- type: VAL
- parent: DOA-IMP-034
- status: validated
- date: 2026-04-18

---

## Title

Brave Search Integration Validation

---

## Validation Scope

Проверка корректности интеграции **Brave Search** в рамках **MVP** (**DOA-IMP-034**, **DOA-DEC-011**):

- выбор режима **live / mock**  
- **fallback** при ошибке live  
- сохранение **pipeline** Search → Classification → Normalization → Ingestion  
- **config discipline** для ключа Brave (без чтения `BRAVE_API_KEY` в search-слое)  

---

## Test Cases

### TC1 — Mock mode (no API key)

**Условия:** `BRAVE_API_KEY` отсутствует (unset в сессии проверки).

**Ожидаемо:** mock recall; pipeline завершается; exit code **0**.

---

### TC2 — Invalid API key

**Условия:** задан заведомо **невалидный** ключ.

**Ожидаемо:** ошибка live provider; **fallback** на mock; exit code **0**.

---

### TC3 — Live mode (valid API key)

**Условия:** валидный `BRAVE_API_KEY`.

**Ожидаемо:** используется live provider; возвращаются реальные **`SearchHit`** (текст/URL из ответа API).

---

### TC4 — Contract integrity

**Проверка:** downstream получает результат поиска как **`list[SearchHit]`**, совместимый с существующим classification entrypoint (dry-run проходит стадию classification).

---

### TC5 — Config discipline

**Проверка:** в каталоге **`app/discovery/search/`** отсутствует прямое чтение **`os.getenv` / `os.environ`** для ключей; `BRAVE_API_KEY` по-прежнему читается только в **`app/discovery/config.py`** (baseline strict config-only).

---

## Executed Checks

### TC1 — выполнено

Команда: `$env:BRAVE_API_KEY=$null; python -m app.discovery.run --query "астролог" --dry-run --limit 2`

Результат: exit **0**; первая строка: `has_brave_key=False`; `found(raw)=2`.

Дополнительно: `python -c "from app.discovery.search.adapter import discovery_search; ..."` — первый hit начинается с **`[mock brave]`** (mock path).

---

### TC2 — выполнено

Команда: `$env:BRAVE_API_KEY='invalid-key-val-009'; python -m app.discovery.run --query "x" --dry-run --limit 1`

Результат: exit **0**; `has_brave_key=True`; `found(raw)=1` (fallback после ошибки live).

---

### TC3 — не выполнялось в автоматической сессии

В среде валидации **нет** гарантированно валидного `BRAVE_API_KEY` без раскрытия секрета; **live** HTTP к Brave с валидным ключом не вызывался.

Рекомендация для полного закрытия TC3: ручной smoke оператором с реальным ключом (ожидаются `SearchHit` без префикса `[mock brave]`).

---

### TC4 — выполнено

TC1/TC2: после search отработали счётчики `passed_classification` / `normalized` без исключений → контракт **`SearchHit`** на границе search → classification сохранён.

---

### TC5 — выполнено

Поиск по **`app/discovery/search/*.py`**: вхождений **`os.getenv` / `os.environ`** **нет**. Чтение **`BRAVE_API_KEY`** в discovery ограничено **`app/discovery/config.py`** (`rg` по `app/discovery`).

---

## Results

| TC | Исход |
|----|--------|
| TC1 | **passed** |
| TC2 | **passed** |
| TC3 | **not run** в данной сессии (требуется валидный ключ у оператора); контракт live path описан в **DOA-IMP-034** |
| TC4 | **passed** |
| TC5 | **passed** |

---

## Conclusion

Интеграция Brave Search валидирована в рамках MVP (в объёме выполненных test cases).

Система:

- работает **стабильно** (TC1, TC2, TC4)  
- **корректно деградирует** в mock при отсутствии ключа и при ошибке live (TC1, TC2)  
- соблюдает **архитектурные инварианты**: контракт **`SearchHit`**, неизменный pipeline (TC4), config discipline для Brave (TC5)  

Полный **live** сценарий (**TC3**) остаётся для подтверждения оператором при наличии валидного `BRAVE_API_KEY`.
