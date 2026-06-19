"""Test per la regola di incompatibilità telelavoro/trasferta (§5 MEF 18/2026)."""

import pytest

from src import storage, validator
from src.app import app


# ---------------------------------------------------------------------------
# Test unitari su validator.valida_compatibilita
# ---------------------------------------------------------------------------

def _richiesta_valida(categoria, data_inizio, giorni, dipendente="Mario Bianchi"):
    return {
        "dipendente": dipendente,
        "data": data_inizio,
        "categoria": categoria,
        "giorni": giorni,
        "importo": 50.0,
        "stato": "valida",
        "quota_esente": 50.0,
    }


def test_telelavoro_rifiutato_se_trasferta_sovrapposta():
    trasferta = _richiesta_valida("trasferta_italia", "2026-03-03", giorni=5)
    telelavoro = {**_richiesta_valida("telelavoro", "2026-03-06", giorni=3), "stato": None}
    ok, motivazione = validator.valida_compatibilita(telelavoro, [trasferta])
    assert not ok
    assert motivazione == "incompatibilità telelavoro/trasferta"


def test_trasferta_rifiutata_se_telelavoro_sovrapposto():
    telelavoro = _richiesta_valida("telelavoro", "2026-03-06", giorni=3)
    trasferta_nuova = {**_richiesta_valida("trasferta_italia", "2026-03-03", giorni=5), "stato": None}
    ok, motivazione = validator.valida_compatibilita(trasferta_nuova, [telelavoro])
    assert not ok
    assert motivazione == "incompatibilità telelavoro/trasferta"


def test_incompatibilita_su_un_solo_giorno():
    # Trasferta 02/03–06/03, telelavoro 06/03–08/03: solo il 06 si sovrappone → rifiuto totale
    trasferta = _richiesta_valida("trasferta_italia", "2026-03-02", giorni=5)
    telelavoro = {**_richiesta_valida("telelavoro", "2026-03-06", giorni=3), "stato": None}
    ok, _ = validator.valida_compatibilita(telelavoro, [trasferta])
    assert not ok


def test_nessuna_sovrapposizione_entrambi_validi():
    # Trasferta 02/03–04/03, telelavoro 05/03–07/03: range adiacenti, nessuna sovrapposizione
    trasferta = _richiesta_valida("trasferta_italia", "2026-03-02", giorni=3)
    telelavoro = {**_richiesta_valida("telelavoro", "2026-03-05", giorni=3), "stato": None}
    ok, _ = validator.valida_compatibilita(telelavoro, [trasferta])
    assert ok


def test_incompatibilita_non_si_applica_a_2025():
    # Stesse date ma anno 2025: il check non scatta
    trasferta = _richiesta_valida("trasferta_italia", "2025-03-02", giorni=5)
    telelavoro = {**_richiesta_valida("telelavoro", "2025-03-06", giorni=3), "stato": None}
    ok, _ = validator.valida_compatibilita(telelavoro, [trasferta])
    assert ok


def test_richieste_respinte_non_contano():
    trasferta_respinta = {
        **_richiesta_valida("trasferta_italia", "2026-03-03", giorni=5),
        "stato": "respinta",
    }
    telelavoro = {**_richiesta_valida("telelavoro", "2026-03-06", giorni=3), "stato": None}
    # La trasferta è respinta: non deve creare incompatibilità
    ok, _ = validator.valida_compatibilita(telelavoro, [trasferta_respinta])
    assert ok


# ---------------------------------------------------------------------------
# Test di integrazione via Flask client
# ---------------------------------------------------------------------------

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "PERCORSO_DATI", tmp_path / "richieste.json")
    app.config["TESTING"] = True
    return app.test_client()


def test_integrazione_telelavoro_respinto_per_incompatibilita(client):
    # Prima registra una trasferta valida
    client.post("/nuova", data={
        "dipendente": "Mario Bianchi",
        "data": "2026-03-03",
        "categoria": "trasferta_italia",
        "importo": "100.00",
        "giorni": "5",
    })
    # Poi prova a registrare un telelavoro che copre il 06/03 (dentro la trasferta)
    risposta = client.post("/nuova", data={
        "dipendente": "Mario Bianchi",
        "data": "2026-03-06",
        "categoria": "telelavoro",
        "importo": "10.50",
        "giorni": "3",
    })
    testo = risposta.get_data(as_text=True)
    assert "respinta" in testo
    assert "incompatibilità" in testo

    richieste = storage.carica()
    assert richieste[1]["stato"] == "respinta"
    assert "incompatibilità" in richieste[1]["motivazione"]
