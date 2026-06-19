"""Regole di validazione delle richieste di rimborso."""

from datetime import date, timedelta

from src import rules

_CATEGORIE_TRASFERTA = {"trasferta_italia", "trasferta_estero"}


def _intervallo_date(richiesta):
    """Set di date coperte dalla richiesta (per trasferte e telelavoro)."""
    inizio = date.fromisoformat(richiesta["data"])
    return {inizio + timedelta(days=i) for i in range(richiesta["giorni"])}


def valida(richiesta):
    """Restituisce (True, "") se la richiesta è valida, altrimenti (False, motivazione)."""
    if not richiesta.get("dipendente"):
        return False, "dipendente mancante"

    categoria = richiesta.get("categoria")
    if categoria not in rules.CATEGORIE:
        return False, "categoria non riconosciuta"

    importo = richiesta.get("importo")
    if importo is None or importo <= 0:
        return False, "importo non positivo"

    try:
        date.fromisoformat(richiesta.get("data") or "")
    except ValueError:
        return False, "data mancante o non valida"

    if categoria in rules.CATEGORIE_A_GIORNATE:
        giorni = richiesta.get("giorni")
        if not giorni or giorni <= 0:
            return False, "numero di giornate non valido"

    if categoria == "chilometrico":
        km = richiesta.get("km")
        if not km or km <= 0:
            return False, "numero di chilometri non valido"

    if categoria == "alloggio":
        notti = richiesta.get("notti")
        if not notti or notti <= 0:
            return False, "numero di notti non valido"

    if categoria == "telelavoro":
        if (richiesta.get("data") or "") < "2026-01-01":
            return False, "categoria non riconosciuta"
        giorni = richiesta.get("giorni")
        if not giorni or giorni <= 0:
            return False, "numero di giornate non valido"

    return True, ""


def valida_compatibilita(richiesta, richieste_valide):
    """Verifica l'incompatibilità telelavoro/trasferta (§5 Circ. MEF 18/2026).

    Solo per richieste con data dal 01/01/2026.
    Restituisce (True, "") se compatibile, (False, motivazione) altrimenti.
    """
    if (richiesta.get("data") or "") < "2026-01-01":
        return True, ""

    categoria = richiesta.get("categoria")
    if categoria not in _CATEGORIE_TRASFERTA and categoria != "telelavoro":
        return True, ""

    giorni_nuova = richiesta.get("giorni")
    if not giorni_nuova or giorni_nuova <= 0:
        return True, ""

    date_nuova = _intervallo_date(richiesta)
    dipendente = richiesta["dipendente"]

    categorie_conflitto = (
        _CATEGORIE_TRASFERTA if categoria == "telelavoro" else {"telelavoro"}
    )

    for r in richieste_valide:
        if r.get("stato") != "valida":
            continue
        if r["dipendente"] != dipendente:
            continue
        if r.get("categoria") not in categorie_conflitto:
            continue
        if not r.get("giorni"):
            continue
        if (r.get("data") or "") < "2026-01-01":
            continue
        if date_nuova & _intervallo_date(r):
            return False, "incompatibilità telelavoro/trasferta"

    return True, ""
