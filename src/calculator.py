"""Calcolo della quota esente e della quota imponibile di una richiesta."""

from types import SimpleNamespace

from src import rules


def _get_rules(data_str):
    """Seleziona i parametri normativi in base all'anno della data di sostenimento."""
    if int(data_str[:4]) >= 2026:
        return SimpleNamespace(
            massimali_giornalieri=rules.MASSIMALI_GIORNALIERI_2026,
            massimale_km=rules.MASSIMALE_KM_2026,
            massimale_notte=rules.MASSIMALE_NOTTE_2026,
            plafond_mensile=rules.PLAFOND_MENSILE_2026,
        )
    return SimpleNamespace(
        massimali_giornalieri=rules.MASSIMALI_GIORNALIERI_2025,
        massimale_km=rules.MASSIMALE_KM_2025,
        massimale_notte=rules.MASSIMALE_NOTTE_2025,
        plafond_mensile=rules.PLAFOND_MENSILE_2025,
    )


def massimale_teorico(richiesta):
    """Massimale di esenzione applicabile alla richiesta, in base alla categoria."""
    r = _get_rules(richiesta["data"])
    categoria = richiesta["categoria"]
    if categoria in rules.CATEGORIE_A_GIORNATE:
        return round(r.massimali_giornalieri[categoria] * richiesta["giorni"], 2)
    if categoria == "chilometrico":
        return round(r.massimale_km * richiesta["km"], 2)
    if categoria == "alloggio":
        return round(r.massimale_notte * richiesta["notti"], 2)
    raise ValueError(f"categoria non gestita: {categoria}")


def calcola(richiesta, esente_gia_riconosciuta):
    """Restituisce (quota_esente, quota_imponibile, dettaglio).

    `esente_gia_riconosciuta` è la quota esente già riconosciuta al dipendente
    nel mese della richiesta, ai fini del plafond mensile.
    """
    r = _get_rules(richiesta["data"])
    importo = richiesta["importo"]
    teorico = massimale_teorico(richiesta)
    esente_teorica = min(importo, teorico)
    capienza = max(r.plafond_mensile - esente_gia_riconosciuta, 0.0)
    esente = round(min(esente_teorica, capienza), 2)
    imponibile = round(importo - esente, 2)
    dettaglio = {
        "massimale_teorico": teorico,
        "esente_teorica": round(esente_teorica, 2),
        "capienza_plafond": round(capienza, 2),
    }
    return esente, imponibile, dettaglio
