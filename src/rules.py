"""Parametri normativi per il calcolo dei rimborsi spese."""

# Circolare MEF n. 41/2024 – in vigore per spese con data fino al 31/12/2025
MASSIMALI_GIORNALIERI_2025 = {
    "trasferta_italia": 46.48,
    "trasferta_estero": 77.47,
    "pasto": 8.00,
}
MASSIMALE_KM_2025 = 0.42
MASSIMALE_NOTTE_2025 = 150.00
PLAFOND_MENSILE_2025 = 1200.00
RIFERIMENTO_NORMATIVO_2025 = "Circolare MEF n. 41/2024"

# Circolare MEF n. 18/2026 – in vigore per spese con data dal 01/01/2026
MASSIMALI_GIORNALIERI_2026 = {
    "trasferta_italia": 50.00,
    "trasferta_estero": 85.00,
    "pasto": 10.00,
}
MASSIMALE_KM_2026 = 0.45
MASSIMALE_NOTTE_2026 = 170.00
PLAFOND_MENSILE_2026 = 1400.00
RIFERIMENTO_NORMATIVO_2026 = "Circolare MEF n. 18/2026"

CATEGORIE = {
    "trasferta_italia": "Trasferta in Italia",
    "trasferta_estero": "Trasferta all'estero",
    "pasto": "Rimborso pasto",
    "chilometrico": "Rimborso chilometrico",
    "alloggio": "Rimborso alloggio",
}

CATEGORIE_A_GIORNATE = ("trasferta_italia", "trasferta_estero", "pasto")
