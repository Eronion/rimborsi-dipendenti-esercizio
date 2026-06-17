"""Entry point per il deploy su Vercel (serverless).

Questo file serve SOLO al deploy dimostrativo su Vercel e non cambia il
funzionamento locale: la persistenza su file `data/richieste.json` definita
in `src/storage.py` resta quella usata da chi clona il repo ed esegue l'app
in locale.

Su Vercel il filesystem e' in sola lettura tranne `/tmp`, che e' temporaneo
e per-istanza. Qui reindirizziamo la persistenza su `/tmp`, seminandolo a
ogni avvio a freddo dai dati di esempio inclusi nel repo. Effetto per chi
prova l'app online: e' pienamente navigabile e si possono inserire richieste,
ma i dati sono un sandbox temporaneo che si reimposta periodicamente e non
e' condiviso tra utenti.

L'override agisce solo qui: `src/storage.py` non viene modificato.
"""

import shutil
from pathlib import Path

from src import storage

_TMP_DATI = Path("/tmp/richieste.json")
_SEED = Path(__file__).resolve().parent.parent / "data" / "richieste.json"

# Avvio a freddo: parti dai dati di esempio se il file temporaneo non esiste.
if not _TMP_DATI.exists() and _SEED.exists():
    shutil.copy(_SEED, _TMP_DATI)

# carica()/salva() leggono questo modulo-globale a ogni richiesta.
storage.PERCORSO_DATI = _TMP_DATI

# L'app WSGI esposta come `app` viene servita dal runtime Python di Vercel.
from src.app import app  # noqa: E402

__all__ = ["app"]
