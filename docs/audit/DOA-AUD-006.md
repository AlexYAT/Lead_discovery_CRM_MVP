# DOA-AUD-006 — Brave Search Integration Audit

## Metadata

- id: DOA-AUD-006
- type: AUD
- status: accepted
- date: 2026-04-18
- parent: DOA-VAL-009

---

## Title

Brave Search Integration Audit

---

## Audit Scope

Аудит интеграции **Brave Search** в discovery pipeline по фактическим артефактам цикла:

- **соответствие lifecycle** (traceability DOA-идентификаторов)  
- **соответствие архитектуре** (**DOA-ARCH-010**: adapter / provider, изоляция внешнего API)  
- **соответствие решениям** (**DOA-DEC-011**: выбор режима, контракт `SearchHit`, fallback, деградация)  
- **влияние на pipeline** (стадии downstream)  
- **config discipline** для ключа Brave (как зафиксировано в **DOA-VAL-009**)  

---

## Reviewed Artifacts

- `docs/ideas/DOA-IDEA-010.md`  
- `docs/architecture/DOA-ARCH-010.md`  
- `docs/decisions/DOA-DEC-011.md`  
- `docs/operations/DOA-OP-011.md`  
- `docs/implementation_snapshot/DOA-IMP-034.md`  
- `docs/validation/DOA-VAL-009.md`  

---

## Findings

1. **Lifecycle соблюдён:** цепочка **IDEA-010 → ARCH-010 → DEC-011 → OP-011 → IMP-034 → VAL-009** замкнута; **AUD-006** ссылается на **VAL-009** как на последний проверенный артефакт.  

2. **Соответствие ARCH-010:** в **IMP-034** зафиксированы **Search Adapter** (`adapter.py` / `discovery_search`) и отдельная **live** реализация (**`BraveLiveSearchProvider`**), mock вынесен в **`MockSearchProvider`**.  

3. **Соответствие DEC-011:** контракт выхода **`SearchHit`**, **graceful fallback** на mock при отсутствии ключа и при ошибке live, **timeout** на live-запросе (константа в реализации, без фиксации в DEC — согласовано **DEC-011 Decision 4**).  

4. **Pipeline не расширен и не переламывался:** **IMP-034** явно оставляет контур **Search → Classification → Normalization → Ingestion** и контракт списка **`SearchHit`** для downstream.  

5. **Config discipline для Brave:** по результатам **VAL-009 (TC5)** в **`app/discovery/search/`** нет чтения **`os.getenv` / `os.environ`**; **`BRAVE_API_KEY`** по-прежнему загружается в **`app/discovery/config.py`** и передаётся параметром (**IMP-032** baseline сохранён). *(В других модулях discovery, не относящихся к Brave search, env может использоваться иначе — вне предмета данного аудита.)*  

---

## Risks

1. **TC3 (live mode)** в **VAL-009** **не выполнялся** в автоматической сессии валидации — остаётся зона ручного подтверждения оператором с валидным ключом.  

2. **Зависимость от внешнего API** Brave (доступность, квоты, изменения контракта API).  

3. **Параметры деградации** (timeout и отсутствие расширенного retry) заданы в **коде** live provider, **без** выноса в **config / env** — при изменении эксплуатационных требований возможен рассинхрон ожиданий оператора и фактического поведения.  

---

## Conclusion

Интеграция Brave Search:

- **корректно реализована** в объёме **IMP-034** и проверок **VAL-009**  
- **соответствует** заявленной **архитектуре** и **DEC-011**  
- **не нарушает** зафиксированные **инварианты** pipeline и контракта **`SearchHit`** для данного цикла  

Lifecycle **Brave Search integration** по DocOps-артефактам **завершён** (при оговорке по **TC3** в **Risks**).
