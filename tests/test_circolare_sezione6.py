"""Test derivati dalla Sezione 6 – Casi particolari ed esempi di calcolo
(Circolare MEF n. 18/2026)."""

from src import calculator, validator


def richiesta(**campi):
    base = {
        "dipendente": "Test Dipendente",
        "data": "2026-03-10",
        "categoria": "pasto",
        "importo": 10.0,
        "giorni": 1,
        "km": None,
        "notti": None,
    }
    base.update(campi)
    return base


class TestCaso61PlafondIncapiente:
    """Caso 6.1 – Plafond mensile incapiente.

    Rimborso pasto, 5 gg, importo 50,00 €, 2026.
    Massimale teorico = 5 × 10,00 = 50,00.
    """

    def test_capienza_esatta_tutto_esente(self):
        # già riconosciuta 1.350 → capienza = 50 → esente = 50, imponibile = 0
        r = richiesta(categoria="pasto", giorni=5, importo=50.00, data="2026-03-10")
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1350.00)
        assert esente == 50.00
        assert imponibile == 0.00

    def test_capienza_insufficiente_split(self):
        # già riconosciuta 1.380 → capienza = 20 → esente = 20, imponibile = 30
        r = richiesta(categoria="pasto", giorni=5, importo=50.00, data="2026-03-10")
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1380.00)
        assert esente == 20.00
        assert imponibile == 30.00


class TestCaso62TrasfertaEsteraCavalloSoglia:
    """Caso 6.2 – Trasferta estera a cavallo della soglia (6 giorni, 2026).

    Massimale = (5 × 85,00) + (1 × 76,50) = 501,50.
    Importo 500,00 < 501,50 → quota esente = 500,00, imponibile = 0,00.
    """

    def test_massimale_teorico_6_giorni(self):
        r = richiesta(categoria="trasferta_estero", giorni=6, data="2026-03-10")
        assert calculator.massimale_teorico(r) == 501.50

    def test_importo_sotto_massimale_tutto_esente(self):
        r = richiesta(categoria="trasferta_estero", giorni=6, importo=500.00, data="2026-03-10")
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.00)
        assert esente == 500.00
        assert imponibile == 0.00


class TestCaso63TrasfertaEstera5GiornateEsatte:
    """Caso 6.3 – Trasferta estera di 5 giornate esatte.

    La riduzione progressiva non si applica: massimale = 5 × 85,00 = 425,00.
    """

    def test_massimale_5_giorni_nessuna_riduzione(self):
        r = richiesta(categoria="trasferta_estero", giorni=5, data="2026-03-10")
        assert calculator.massimale_teorico(r) == 425.00


class TestCaso64TelelavOltreLimiteMensile:
    """Caso 6.4 – Lavoro agile oltre il limite mensile.

    15 giorni richiesti, 0 già usati → giorni ammessi = min(15, 12) = 12
    → massimale teorico = 12 × 3,50 = 42,00.
    Importo 52,50 > 42,00 → esente 42,00, imponibile 10,50.
    """

    def test_massimale_limitato_a_12_giorni(self):
        r = richiesta(categoria="telelavoro", giorni=15, importo=52.50, data="2026-03-10")
        assert calculator.massimale_teorico(r, giorni_telelavoro_gia_usati=0) == 42.00

    def test_esente_limitata_da_massimale_giorni(self):
        r = richiesta(categoria="telelavoro", giorni=15, importo=52.50, data="2026-03-10")
        esente, imponibile, _ = calculator.calcola(r, 0.00, giorni_telelavoro_gia_usati=0)
        assert esente == 42.00
        assert imponibile == 10.50


class TestCaso65IncompatibilitaGiornataSingola:
    """Caso 6.5 – Incompatibilità su giornata singola.

    Trasferta nazionale 02/03/2026–06/03/2026 (5 gg).
    Telelavoro 06/03/2026–08/03/2026 (3 gg).
    Il 06/03 è l'unico giorno comune → telelavoro respinto integralmente.
    """

    def test_telelavoro_respinto_per_un_solo_giorno_comune(self):
        trasferta = {
            "dipendente": "Test Dipendente",
            "data": "2026-03-02",
            "categoria": "trasferta_italia",
            "giorni": 5,
            "importo": 250.00,
            "stato": "valida",
            "quota_esente": 250.00,
        }
        telelavoro = {
            "dipendente": "Test Dipendente",
            "data": "2026-03-06",
            "categoria": "telelavoro",
            "giorni": 3,
            "importo": 10.50,
            "stato": None,
        }
        ok, motivazione = validator.valida_compatibilita(telelavoro, [trasferta])
        assert not ok
        assert motivazione == "incompatibilità telelavoro/trasferta"


class TestCaso66Richiesta2025PresentataNel2026:
    """Caso 6.6 – Richiesta 2025 presentata nel 2026.

    Rimborso pasto, 3 gg, data sostenimento 18/12/2025: si applicano i massimali
    previgenti (8,00 €/gg) e il plafond 2025 (1.200,00 €).
    La categoria telelavoro è rifiutata per date pre-2026.
    """

    def test_massimale_usa_regole_2025(self):
        # 3 × 8,00 = 24,00, non 3 × 10,00 = 30,00
        r = richiesta(categoria="pasto", giorni=3, importo=30.00, data="2025-12-18")
        assert calculator.massimale_teorico(r) == 24.00

    def test_calcolo_applica_massimale_2025(self):
        # importo 30 > massimale 24 → esente = 24, imponibile = 6
        r = richiesta(categoria="pasto", giorni=3, importo=30.00, data="2025-12-18")
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.00)
        assert esente == 24.00
        assert imponibile == 6.00

    def test_plafond_usa_limite_2025(self):
        # plafond 2025 = 1.200: se esaurito → tutto imponibile
        r = richiesta(categoria="pasto", giorni=3, importo=24.00, data="2025-12-18")
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1200.00)
        assert esente == 0.00
        assert imponibile == 24.00

    def test_telelavoro_data_2025_respinto_categoria_non_riconosciuta(self):
        r = richiesta(categoria="telelavoro", giorni=3, importo=10.50, data="2025-12-18")
        ok, motivazione = validator.valida(r)
        assert not ok
        assert motivazione == "categoria non riconosciuta"


class TestCaso67TrasfertaEsteraIniziata2025:
    """Caso 6.7 – Trasferta estera iniziata nel 2025 e conclusa nel 2026.

    La data di sostenimento è la data di inizio trasferta: si applica la disciplina
    previgente (77,47 €/giorno, nessuna riduzione progressiva).
    Esempio: 8 giorni, importo 800,00 → massimale = 77,47 × 8 = 619,76.
    """

    def test_massimale_usa_tariffa_2025_no_riduzione_progressiva(self):
        r = richiesta(categoria="trasferta_estero", giorni=8, importo=800.00, data="2025-12-28")
        assert calculator.massimale_teorico(r) == 619.76  # 77,47 × 8, piatto

    def test_calcolo_completo_trasferta_transfrontaliera(self):
        r = richiesta(categoria="trasferta_estero", giorni=8, importo=800.00, data="2025-12-28")
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.00)
        assert esente == 619.76
        assert imponibile == 180.24
