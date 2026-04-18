## Metadata

id: DOA-IDEA-013  
type: IDEA  
status: proposed  
parent: DOA-AUD-007  
date: 2026-04-18

---

## Title

Discovery Pipeline Observability Layer

---

## Problem

Текущий discovery pipeline выполняет поиск и обработку кандидатов, но не предоставляет оператору прозрачности стадий обработки.

Отсутствует возможность:

- видеть raw результаты поиска
- понимать, какие кандидаты проходят classification
- видеть признаки (pain, confidence)
- понимать влияние qualification layer
- анализировать причины фильтрации

В результате:

- сложно улучшать качество pipeline
- отсутствует feedback loop
- невозможно валидировать эвристики

---

## Idea

Добавить слой наблюдаемости (observability) для discovery pipeline.

Цель:

- визуализировать стадии pipeline
- показать трансформацию кандидатов
- дать оператору понимание причин фильтрации
- обеспечить основу для улучшения качества

---

## Scope

В рамках IDEA:

- отображение кандидатов на разных стадиях pipeline
- отображение признаков (classification, qualification)
- минимальный UI/debug view

Вне scope:

- сложный UI
- редактирование кандидатов
- автоматические решения
- ML/AI анализ
- изменение pipeline
