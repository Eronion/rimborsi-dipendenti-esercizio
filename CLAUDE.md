# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the app
flask --app src.app run

# Run all tests
pytest

# Run a single test file
pytest tests/test_calculator.py

# Run a single test
pytest tests/test_calculator.py::test_name -v
```

## Architecture

This is a Flask web app for managing employee expense reimbursements (rimborsi spese), applying Italian tax law (Circolare MEF n. 41/2024) to determine the IRPEF-exempt and taxable portions of each request.

**Data flow for a new request:**

1. `app.py` receives the form POST → calls `validator.valida()` to check required fields
2. If valid: `storage.esente_riconosciuta_nel_mese()` fetches the employee's already-recognized exempt quota for that month (for plafond tracking), then `calculator.calcola()` computes `quota_esente` and `quota_imponibile`
3. `storage.salva()` appends the result to `data/richieste.json`

**Key business rules (all constants in `rules.py`):**

- Each expense category (`trasferta_italia`, `trasferta_estero`, `pasto`, `chilometrico`, `alloggio`) has a per-unit ceiling
- Categories `trasferta_italia`, `trasferta_estero`, `pasto` multiply by `giorni`; `chilometrico` by `km`; `alloggio` by `notti`
- A monthly per-employee plafond (`PLAFOND_MENSILE = 1200.00 €`) caps total exempt amount; `calculator.calcola()` receives the already-consumed amount and caps accordingly
- Exempt = `min(importo, massimale_teorico, plafond_residuo)`; taxable = `importo - esente`

**Module responsibilities:**

| File | Role |
|------|------|
| `rules.py` | Single source of truth for all regulatory constants |
| `calculator.py` | Pure functions; no I/O; takes a request dict + already-recognized exempt amount |
| `validator.py` | Pure functions; validates shape/presence of required fields per category |
| `storage.py` | JSON file I/O (`data/richieste.json`); plafond query helper |
| `app.py` | Flask routes; orchestrates the above; no business logic |

**No database**: all data lives in `data/richieste.json`. The `data/` directory is created on first save. 

**Boundaries**: Do not touch the stored requests in data/.


