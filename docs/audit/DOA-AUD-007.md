# DOA-AUD-007 — Lead Qualification Layer Audit

## Metadata

- id: DOA-AUD-007
- type: AUD
- status: accepted
- date: 2026-04-18
- parent: DOA-VAL-010

---

## Title

Lead Qualification Layer Audit

---

## Audit Scope

Аудит внедрения **Lead Qualification Layer** по фактическим артефактам цикла и результатам **DOA-VAL-010**:

- **соответствие lifecycle** (traceability DOA-идентификаторов)  
- **соответствие архитектуре** (**DOA-ARCH-011**: место слоя, soft qualification)  
- **соответствие решениям** (**DOA-DEC-012**)  
- **влияние на pipeline** (расширение без заявленного breaking change)  
- **config discipline** для настроек qualification  

---

## Reviewed Artifacts

- `docs/ideas/DOA-IDEA-011.md`  
- `docs/architecture/DOA-ARCH-011.md`  
- `docs/decisions/DOA-DEC-012.md`  
- `docs/operations/DOA-OP-012.md`  
- `docs/implementation_snapshot/DOA-IMP-035.md`  
- `docs/validation/DOA-VAL-010.md`  

---

## Findings

1. **Lifecycle соблюдён:** цепочка **IDEA-011 → ARCH-011 → DEC-012 → OP-012 → IMP-035 → VAL-010** замкнута; **AUD-007** ссылается на **VAL-010** как на последний проверенный артефакт.  

2. **Место слоя в pipeline** согласовано с **IMP-035** и **ARCH-011:** **Search → Classification → Qualification → Normalization → Ingestion** (orchestration в **`run.py`** вызывает qualification между classification и normalization).  

3. **Решения DEC-012 отражены в IMP/VAL:** **soft qualification** без удаления кандидатов; расширение через **метаданные** и **третий** элемент строки без изменения типов **`SearchHit`** / **`ClassificationResult`**; управление через **`DiscoveryConfig`** / **`DISCOVERY_QUALIFICATION_*`**; **optional** режим с **pass-through** при выключении — подтверждено **VAL-010** (TC1–TC5).  

4. **Downstream контракт:** **VAL-010 TC4** подтверждает приём **2-** и **3-**элементных входов в **`normalize_candidates`**; обогащение **`NormalizedCandidate.metadata`** при включённом слое — **VAL-010 TC3**.  

5. **Config discipline (qualification):** **VAL-010 TC5** фиксирует чтение **`DISCOVERY_QUALIFICATION_*`** только в **`app/discovery/config.py`** и отсутствие **`os.getenv` / `os.environ`** в **`app/discovery/qualification/`**.  

---

## Risks

1. **VAL-010** явно ограничивает покрытие: не выполнялся полный прогон комбинаций **`DISCOVERY_QUALIFICATION_MIN_CONFIDENCE`** и длинных батчей.  

2. **Ingestion / БД:** глубокая проверка содержимого записей после ingest **не** входила в VAL — опирались на счётчик **`saved`** и успешный exit (**VAL-010**, residual).  

3. **Эвристики** (`none` / `medium` / `high`) остаются **MVP**-уровня; для «шумных» реальных выборок может понадобиться следующий цикл улучшений (вне текущего scope).  

---

## Conclusion

**Lead Qualification Layer** по результатам артефактов и **VAL-010**:

- **реализован** в объёме **IMP-035**  
- **соответствует** заявленной **архитектуре** и **DEC-012** в проверенных аспектах  
- **не нарушает** зафиксированные в VAL инварианты совместимости normalization и config discipline  

Lifecycle по DocOps-артефактам **завершён** с оговорками из раздела **Risks** (наследуемыми из **VAL-010**).
