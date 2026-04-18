## Metadata

id: DOA-DEC-015  
type: DEC  
status: accepted  
parent: DOA-ARCH-014  
date: 2026-04-18

---

## Title

Candidate Identity and Diff Strategy for Observability

---

## Decision 1 — Primary Identity

Кандидаты идентифицируются по:

- source_link (URL)

---

## Decision 2 — Fallback Identity

Если source_link отсутствует:

- используется hash(text)

---

## Decision 3 — Comparison Logic

Diff определяется как:

- кандидаты, присутствующие на стадии A
- и отсутствующие на стадии B

---

## Decision 4 — Stability Requirement

Identity должна быть:

- стабильной между стадиями pipeline
- независимой от внутренних преобразований

---

## Decision 5 — Scope

Эти правила применяются только для:

- observability
- debug view

И не влияют на:

- бизнес-логику pipeline
- ingestion

---

## Constraints

- не изменять pipeline
- не добавлять новые поля в доменные модели
- использовать только доступные данные
