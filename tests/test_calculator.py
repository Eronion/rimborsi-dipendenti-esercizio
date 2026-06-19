from src import calculator


def richiesta(**campi):
    base = {
        "dipendente": "Maria Rossi",
        "data": "2025-10-06",
        "categoria": "pasto",
        "importo": 10.0,
        "giorni": 1,
        "km": None,
        "notti": None,
    }
    base.update(campi)
    return base


class TestMassimaleTeorico:
    def test_trasferta_italia(self):
        r = richiesta(categoria="trasferta_italia", giorni=4)
        assert calculator.massimale_teorico(r) == 185.92

    def test_trasferta_estero(self):
        r = richiesta(categoria="trasferta_estero", giorni=3)
        assert calculator.massimale_teorico(r) == 232.41

    def test_pasto(self):
        r = richiesta(categoria="pasto", giorni=5)
        assert calculator.massimale_teorico(r) == 40.0

    def test_chilometrico(self):
        r = richiesta(categoria="chilometrico", km=250)
        assert calculator.massimale_teorico(r) == 105.0

    def test_alloggio(self):
        r = richiesta(categoria="alloggio", notti=2)
        assert calculator.massimale_teorico(r) == 300.0


class TestTrasfertaEstero2026:
    def test_5_giorni_cap_pieno(self):
        r = richiesta(categoria="trasferta_estero", giorni=5, data="2026-03-10")
        assert calculator.massimale_teorico(r) == 425.00

    def test_6_giorni_riduzione_10pct(self):
        r = richiesta(categoria="trasferta_estero", giorni=6, data="2026-03-10")
        assert calculator.massimale_teorico(r) == 501.50

    def test_10_giorni_no_terzo_scaglione(self):
        r = richiesta(categoria="trasferta_estero", giorni=10, data="2026-03-10")
        assert calculator.massimale_teorico(r) == 807.50

    def test_12_giorni_doppia_riduzione(self):
        r = richiesta(categoria="trasferta_estero", giorni=12, data="2026-03-10")
        assert calculator.massimale_teorico(r) == 943.50

    def test_5_giorni_2025_nessuna_riduzione(self):
        r = richiesta(categoria="trasferta_estero", giorni=5, data="2025-10-06")
        assert calculator.massimale_teorico(r) == 387.35


class TestTelelavoro:
    def test_sotto_limite_mensile(self):
        r = richiesta(categoria="telelavoro", giorni=5, importo=17.50, data="2026-03-10")
        assert calculator.massimale_teorico(r, giorni_telelavoro_gia_usati=0) == 17.50

    def test_giorni_limitati_da_residuo(self):
        r = richiesta(categoria="telelavoro", giorni=8, importo=28.00, data="2026-03-10")
        # residuo: 12 - 7 = 5 giorni consentiti → 5 × 3.50 = 17.50
        assert calculator.massimale_teorico(r, giorni_telelavoro_gia_usati=7) == 17.50

    def test_residuo_zero_tutto_imponibile(self):
        r = richiesta(categoria="telelavoro", giorni=3, importo=10.50, data="2026-03-10")
        esente, imponibile, _ = calculator.calcola(r, 0.0, giorni_telelavoro_gia_usati=12)
        assert esente == 0.0
        assert imponibile == 10.50

    def test_oltre_12_giorni(self):
        r = richiesta(categoria="telelavoro", giorni=15, importo=52.50, data="2026-03-10")
        # min(15, 12) = 12 giorni → 12 × 3.50 = 42.00
        assert calculator.massimale_teorico(r, giorni_telelavoro_gia_usati=0) == 42.00

    def test_esempio_circolare_sezione3(self):
        # Esempio §3: 8 già usati, richiesta 6 gg, importo 21.00
        # allowed = min(6, 12-8) = 4 → cap = 14.00 → esente = 14.00, imponibile = 7.00
        r = richiesta(categoria="telelavoro", giorni=6, importo=21.00, data="2026-03-10")
        esente, imponibile, _ = calculator.calcola(r, 0.0, giorni_telelavoro_gia_usati=8)
        assert esente == 14.00
        assert imponibile == 7.00


class TestMassimali2026:
    def test_trasferta_italia_2026(self):
        r = richiesta(categoria="trasferta_italia", giorni=4, data="2026-03-10")
        assert calculator.massimale_teorico(r) == 200.00

    def test_trasferta_estero_2026(self):
        r = richiesta(categoria="trasferta_estero", giorni=3, data="2026-03-10")
        assert calculator.massimale_teorico(r) == 255.00

    def test_pasto_2026(self):
        r = richiesta(categoria="pasto", giorni=5, data="2026-03-10")
        assert calculator.massimale_teorico(r) == 50.00

    def test_chilometrico_2026(self):
        r = richiesta(categoria="chilometrico", km=250, data="2026-03-10")
        assert calculator.massimale_teorico(r) == 112.50

    def test_alloggio_2026(self):
        r = richiesta(categoria="alloggio", notti=2, data="2026-03-10")
        assert calculator.massimale_teorico(r) == 340.00

    def test_plafond_2026_capienza_residua(self):
        r = richiesta(categoria="alloggio", notti=2, importo=200.0, data="2026-03-10")
        esente, imponibile, dettaglio = calculator.calcola(r, esente_gia_riconosciuta=1300.0)
        assert esente == 100.0
        assert imponibile == 100.0
        assert dettaglio["capienza_plafond"] == 100.0

    def test_plafond_2026_esaurito(self):
        r = richiesta(categoria="pasto", giorni=1, importo=10.0, data="2026-03-10")
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1400.0)
        assert esente == 0.0
        assert imponibile == 10.0

    def test_transitional_2025_date_usa_cap_vecchi(self):
        r = richiesta(categoria="pasto", giorni=5, importo=50.0, data="2025-12-31")
        assert calculator.massimale_teorico(r) == 40.0  # 5 × 8.00, non 5 × 10.00

    def test_transitional_2025_date_usa_plafond_vecchio(self):
        r = richiesta(categoria="pasto", giorni=1, importo=8.0, data="2025-12-31")
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1200.0)
        assert esente == 0.0  # plafond 1200 esaurito
        assert imponibile == 8.0

    def test_transitional_2026_date_usa_plafond_nuovo(self):
        r = richiesta(categoria="pasto", giorni=1, importo=10.0, data="2026-01-01")
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1200.0)
        assert esente == 10.0  # capienza residua 1400 - 1200 = 200
        assert imponibile == 0.0


class TestCalcola:
    def test_importo_sotto_massimale_tutto_esente(self):
        r = richiesta(categoria="pasto", giorni=5, importo=35.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
        assert esente == 35.0
        assert imponibile == 0.0

    def test_importo_sopra_massimale_eccedenza_imponibile(self):
        r = richiesta(categoria="trasferta_italia", giorni=2, importo=120.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
        assert esente == 92.96
        assert imponibile == 27.04

    def test_plafond_incapiente_limita_la_quota_esente(self):
        r = richiesta(categoria="alloggio", notti=2, importo=300.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1100.0)
        assert esente == 100.0
        assert imponibile == 200.0

    def test_plafond_esaurito_tutto_imponibile(self):
        r = richiesta(categoria="pasto", giorni=1, importo=8.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1200.0)
        assert esente == 0.0
        assert imponibile == 8.0

    def test_dettaglio_del_calcolo(self):
        r = richiesta(categoria="trasferta_estero", giorni=2, importo=200.0)
        _, _, dettaglio = calculator.calcola(r, esente_gia_riconosciuta=1100.0)
        assert dettaglio == {
            "massimale_teorico": 154.94,
            "esente_teorica": 154.94,
            "capienza_plafond": 100.0,
        }
