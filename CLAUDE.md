# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Cosa fa

Webapp Flask interna dell'ufficio HR per la gestione delle richieste di rimborso spese.
Per ogni richiesta calcola la **quota esente** IRPEF e la **quota imponibile** secondo i
massimali della normativa vigente (Circolare MEF n. 41/2024, anno 2025), valida i dati e
tiene traccia del **plafond mensile** di esenzione per dipendente. UI e codice sono in
italiano: mantieni questa convenzione (nomi di funzioni, variabili, messaggi, template).

## Comandi

```bash
flask --app src.app run     # avvia su http://127.0.0.1:5000
pytest                      # tutti i test
pytest tests/test_calculator.py::TestMassimaleTeorico::test_pasto   # singolo test
pytest -v                   # come la CI (.github/workflows/ci.yml)
```

`pyproject.toml` imposta `pythonpath = ["."]`, quindi gli import `from src import ...`
funzionano senza installare il pacchetto. La CI gira su Python 3.12; il codice richiede
Python 3.10+.

## Architettura

Pipeline a moduli puri orchestrati da `app.py`. Il flusso di una nuova richiesta
(`_registra` in [src/app.py](src/app.py)) è il punto centrale da capire:

1. **`validator.valida(richiesta)`** → `(ok, motivazione)`. Se fallisce, la richiesta è
   salvata con `stato="respinta"`, quote a 0 e `dettaglio=None`. Le richieste respinte
   restano archiviate, non vengono scartate.
2. **`storage.esente_riconosciuta_nel_mese(...)`** somma le quote esenti delle richieste
   **valide** dello stesso dipendente nello stesso mese (mese = primi 7 char di `data`,
   formato `AAAA-MM`).
3. **`calculator.calcola(richiesta, esente_gia_riconosciuta)`** → `(esente, imponibile,
   dettaglio)`. L'esenzione è il minimo tra importo, massimale teorico della categoria, e
   **capienza residua del plafond mensile**. Questo accoppiamento tra plafond e ordine di
   inserimento è la logica chiave: la stessa richiesta può risultare in quote diverse a
   seconda di quanto plafond è già stato consumato nel mese.

Moduli (`src/`):
- **`rules.py`** — unica fonte dei parametri normativi (massimali giornalieri, €/km,
  €/notte, `PLAFOND_MENSILE`, mappa `CATEGORIE`, `CATEGORIE_A_GIORNATE`). Cambia i
  massimali qui; nessun valore è hardcoded altrove.
- **`calculator.py`** / **`validator.py`** — funzioni pure, nessun I/O.
- **`storage.py`** — persistenza su `data/richieste.json` (nessun database). Le richieste
  sono una lista di dict; `prossimo_id` calcola l'id incrementale.
- **`app.py`** — solo routing e adattamento del form (helper `_numero`/`_intero` che
  ritornano `None` su input non valido, poi intercettato dal validator).

Le categorie si dividono in tre forme di calcolo del massimale: **a giornate**
(`trasferta_italia`, `trasferta_estero`, `pasto` → massimale × `giorni`), **chilometrico**
(€/km × `km`) e **alloggio** (€/notte × `notti`). Aggiungere una categoria richiede di
toccare `rules.CATEGORIE`, `calculator.massimale_teorico` e `validator.valida` insieme.

## Test

`tests/test_app.py` isola la persistenza con `monkeypatch.setattr(storage, "PERCORSO_DATI",
tmp_path / "richieste.json")` — usa lo stesso pattern per i test che scrivono dati, così
non tocchi `data/richieste.json` reale.
