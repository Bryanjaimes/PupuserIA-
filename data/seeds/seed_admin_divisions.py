"""
Seed script — El Salvador administrative divisions.
====================================================
All 14 departments + 262 municipios with:
  - Official names (EN/ES)
  - Centroid coordinates (lat/lng)
  - Population (2023 est.)
  - Area (km²)
  - Department capital
  - Elevation (m, for municipio cabeceras)

Also generates initial DataCoverageGap records for every municipio
and computes coverage scores (all start at 0 — no data yet).

Usage:
  python -m data.seeds.seed_admin_divisions
  OR import and call seed_all(session)
"""

import json
from datetime import datetime
from uuid import uuid4

# ═══════════════════════════════════════════════════════
# 14 DEPARTMENTS
# ═══════════════════════════════════════════════════════
# Data sources:
#   - DIGESTYC (Dirección General de Estadística y Censos)
#   - Wikipedia / Instituto Geográfico Nacional
#   - Population: 2023 DIGESTYC projections

DEPARTMENTS = [
    {"id": 1,  "name": "Ahuachapán",       "name_es": "Ahuachapán",       "capital": "Ahuachapán",       "area_km2": 1239.6, "population": 363_470, "pop_year": 2023, "iso": "SV-AH", "lat": 13.920, "lng": -89.845},
    {"id": 2,  "name": "Santa Ana",         "name_es": "Santa Ana",         "capital": "Santa Ana",        "area_km2": 2023.2, "population": 600_992, "pop_year": 2023, "iso": "SV-SA", "lat": 14.000, "lng": -89.560},
    {"id": 3,  "name": "Sonsonate",         "name_es": "Sonsonate",         "capital": "Sonsonate",        "area_km2": 1225.8, "population": 519_229, "pop_year": 2023, "iso": "SV-SO", "lat": 13.700, "lng": -89.724},
    {"id": 4,  "name": "Chalatenango",      "name_es": "Chalatenango",      "capital": "Chalatenango",     "area_km2": 2016.6, "population": 211_889, "pop_year": 2023, "iso": "SV-CH", "lat": 14.120, "lng": -88.939},
    {"id": 5,  "name": "La Libertad",       "name_es": "La Libertad",       "capital": "Santa Tecla",      "area_km2": 1652.9, "population": 830_956, "pop_year": 2023, "iso": "SV-LI", "lat": 13.630, "lng": -89.360},
    {"id": 6,  "name": "San Salvador",      "name_es": "San Salvador",      "capital": "San Salvador",     "area_km2":  886.2, "population": 1_822_127, "pop_year": 2023, "iso": "SV-SS", "lat": 13.698, "lng": -89.191},
    {"id": 7,  "name": "Cuscatlán",         "name_es": "Cuscatlán",         "capital": "Cojutepeque",      "area_km2":  756.2, "population": 258_939, "pop_year": 2023, "iso": "SV-CU", "lat": 13.730, "lng": -88.940},
    {"id": 8,  "name": "La Paz",            "name_es": "La Paz",            "capital": "Zacatecoluca",     "area_km2": 1223.6, "population": 372_571, "pop_year": 2023, "iso": "SV-PA", "lat": 13.510, "lng": -88.870},
    {"id": 9,  "name": "Cabañas",           "name_es": "Cabañas",           "capital": "Sensuntepeque",    "area_km2": 1103.5, "population": 167_560, "pop_year": 2023, "iso": "SV-CA", "lat": 13.880, "lng": -88.630},
    {"id": 10, "name": "San Vicente",       "name_es": "San Vicente",       "capital": "San Vicente",      "area_km2": 1184.0, "population": 188_580, "pop_year": 2023, "iso": "SV-SV", "lat": 13.640, "lng": -88.780},
    {"id": 11, "name": "Usulután",          "name_es": "Usulután",          "capital": "Usulután",         "area_km2": 2130.4, "population": 380_786, "pop_year": 2023, "iso": "SV-US", "lat": 13.440, "lng": -88.440},
    {"id": 12, "name": "San Miguel",        "name_es": "San Miguel",        "capital": "San Miguel",       "area_km2": 2077.1, "population": 521_167, "pop_year": 2023, "iso": "SV-SM", "lat": 13.480, "lng": -88.180},
    {"id": 13, "name": "Morazán",           "name_es": "Morazán",           "capital": "San Francisco Gotera", "area_km2": 1447.4, "population": 201_811, "pop_year": 2023, "iso": "SV-MO", "lat": 13.750, "lng": -88.100},
    {"id": 14, "name": "La Unión",          "name_es": "La Unión",          "capital": "La Unión",         "area_km2": 2074.3, "population": 275_083, "pop_year": 2023, "iso": "SV-UN", "lat": 13.450, "lng": -87.840},
]


# ═══════════════════════════════════════════════════════
# 262 MUNICIPIOS — grouped by department
# ═══════════════════════════════════════════════════════
# fmt: off

MUNICIPIOS = [
    # ── 1. Ahuachapán (12 municipios) ──
    {"dept": 1, "name": "Ahuachapán",           "lat": 13.921, "lng": -89.845, "pop": 110_511, "area": 244.0, "elev": 785},
    {"dept": 1, "name": "Apaneca",              "lat": 13.858, "lng": -89.806, "pop":  8_861,  "area":  45.2, "elev": 1450},
    {"dept": 1, "name": "Atiquizaya",           "lat": 13.977, "lng": -89.752, "pop": 41_543,  "area":  66.4, "elev": 640},
    {"dept": 1, "name": "Concepción de Ataco",  "lat": 13.870, "lng": -89.850, "pop": 15_218,  "area": 102.8, "elev": 1275},
    {"dept": 1, "name": "El Refugio",           "lat": 13.961, "lng": -89.828, "pop":  6_206,  "area":  12.8, "elev": 653},
    {"dept": 1, "name": "Guaymango",            "lat": 13.751, "lng": -89.843, "pop": 21_239,  "area": 103.2, "elev": 400},
    {"dept": 1, "name": "Jujutla",              "lat": 13.787, "lng": -89.859, "pop": 28_895,  "area": 244.4, "elev": 250},
    {"dept": 1, "name": "San Francisco Menéndez","lat": 13.843, "lng": -90.016, "pop": 45_682, "area": 234.0, "elev": 100},
    {"dept": 1, "name": "San Lorenzo",          "lat": 13.961, "lng": -89.774, "pop": 11_126,  "area":  39.2, "elev": 750},
    {"dept": 1, "name": "San Pedro Puxtla",     "lat": 13.800, "lng": -89.782, "pop": 10_700,  "area":  61.6, "elev": 780},
    {"dept": 1, "name": "Tacuba",               "lat": 13.900, "lng": -89.930, "pop": 29_800,  "area": 130.4, "elev": 700},
    {"dept": 1, "name": "Turín",                "lat": 13.969, "lng": -89.805, "pop":  9_300,   "area":  22.0, "elev": 620},

    # ── 2. Santa Ana (13 municipios) ──
    {"dept": 2, "name": "Santa Ana",            "lat": 13.994, "lng": -89.560, "pop": 280_000, "area": 400.0, "elev": 665},
    {"dept": 2, "name": "Candelaria de la Frontera", "lat": 14.117, "lng": -89.651, "pop": 19_300, "area": 79.0, "elev": 670},
    {"dept": 2, "name": "Chalchuapa",           "lat": 13.987, "lng": -89.681, "pop": 85_398,  "area": 165.6, "elev": 700},
    {"dept": 2, "name": "Coatepeque",           "lat": 13.925, "lng": -89.510, "pop": 43_500,  "area": 135.2, "elev": 750},
    {"dept": 2, "name": "El Congo",             "lat": 13.908, "lng": -89.496, "pop": 28_000,  "area":  85.2, "elev": 780},
    {"dept": 2, "name": "El Porvenir",          "lat": 14.060, "lng": -89.630, "pop":  7_200,  "area":  34.0, "elev": 850},
    {"dept": 2, "name": "Masahuat",             "lat": 14.060, "lng": -89.400, "pop":  4_200,  "area":  55.0, "elev": 650},
    {"dept": 2, "name": "Metapán",              "lat": 14.333, "lng": -89.450, "pop": 65_000,  "area": 668.4, "elev": 470},
    {"dept": 2, "name": "San Antonio Pajonal",  "lat": 14.078, "lng": -89.486, "pop":  3_500,  "area":  30.0, "elev": 950},
    {"dept": 2, "name": "San Sebastián Salitrillo","lat": 14.038, "lng": -89.594, "pop": 21_200,"area": 23.6, "elev": 630},
    {"dept": 2, "name": "Santa Rosa Guachipilín","lat": 14.100, "lng": -89.400, "pop":  6_200, "area":  76.0, "elev": 850},
    {"dept": 2, "name": "Santiago de la Frontera","lat": 14.101, "lng": -89.683, "pop":  6_000, "area":  30.0, "elev": 750},
    {"dept": 2, "name": "Texistepeque",         "lat": 14.133, "lng": -89.500, "pop": 19_000,  "area": 135.0, "elev": 490},

    # ── 3. Sonsonate (16 municipios) ──
    {"dept": 3, "name": "Sonsonate",            "lat": 13.719, "lng": -89.724, "pop": 85_600,  "area": 232.8, "elev": 225},
    {"dept": 3, "name": "Acajutla",             "lat": 13.593, "lng": -89.827, "pop": 56_800,  "area": 166.0, "elev": 15},
    {"dept": 3, "name": "Armenia",              "lat": 13.743, "lng": -89.500, "pop": 37_500,  "area":  68.0, "elev": 520},
    {"dept": 3, "name": "Caluco",               "lat": 13.722, "lng": -89.659, "pop": 10_600,  "area":  36.0, "elev": 350},
    {"dept": 3, "name": "Cuisnahuat",           "lat": 13.643, "lng": -89.514, "pop": 11_000,  "area": 118.4, "elev": 350},
    {"dept": 3, "name": "Izalco",               "lat": 13.745, "lng": -89.673, "pop": 72_700,  "area": 175.2, "elev": 440},
    {"dept": 3, "name": "Juayúa",               "lat": 13.841, "lng": -89.747, "pop": 25_200,  "area":  69.6, "elev": 1030},
    {"dept": 3, "name": "Nahuizalco",           "lat": 13.774, "lng": -89.737, "pop": 52_000,  "area":  34.4, "elev": 540},
    {"dept": 3, "name": "Nahulingo",            "lat": 13.720, "lng": -89.679, "pop":  7_100,  "area":  12.8, "elev": 280},
    {"dept": 3, "name": "Salcoatitán",          "lat": 13.833, "lng": -89.770, "pop":  5_300,  "area":  27.6, "elev": 1045},
    {"dept": 3, "name": "San Antonio del Monte", "lat": 13.717, "lng": -89.739, "pop": 28_300, "area":  29.2, "elev": 240},
    {"dept": 3, "name": "San Julián",           "lat": 13.697, "lng": -89.566, "pop": 17_000,  "area":  54.0, "elev": 380},
    {"dept": 3, "name": "Santa Catarina Masahuat","lat": 13.664, "lng": -89.572, "pop": 13_200,"area":  42.0, "elev": 360},
    {"dept": 3, "name": "Santa Isabel Ishuatán", "lat": 13.650, "lng": -89.614, "pop": 11_500, "area": 142.0, "elev": 350},
    {"dept": 3, "name": "Santo Domingo de Guzmán","lat": 13.734, "lng": -89.788, "pop": 7_800,"area":  20.0, "elev": 420},
    {"dept": 3, "name": "Sonzacate",            "lat": 13.733, "lng": -89.710, "pop": 32_800,  "area":  10.8, "elev": 235},

    # ── 4. Chalatenango (33 municipios) ──
    {"dept": 4, "name": "Chalatenango",         "lat": 14.042, "lng": -88.939, "pop": 30_200,  "area": 131.6, "elev": 360},
    {"dept": 4, "name": "Agua Caliente",        "lat": 14.081, "lng": -88.751, "pop":  5_200,  "area":  23.6, "elev": 800},
    {"dept": 4, "name": "Arcatao",              "lat": 14.084, "lng": -88.765, "pop":  3_500,  "area":  43.2, "elev": 690},
    {"dept": 4, "name": "Azacualpa",            "lat": 14.100, "lng": -88.850, "pop":  3_800,  "area":  25.0, "elev": 580},
    {"dept": 4, "name": "Cancasque",            "lat": 14.031, "lng": -88.687, "pop":  2_200,  "area":  20.8, "elev": 540},
    {"dept": 4, "name": "Citalá",               "lat": 14.385, "lng": -89.185, "pop":  4_800,  "area":  29.6, "elev": 660},
    {"dept": 4, "name": "Comalapa",             "lat": 14.066, "lng": -88.838, "pop":  4_300,  "area":  39.2, "elev": 460},
    {"dept": 4, "name": "Concepción Quezaltepeque","lat": 14.126,"lng": -88.952, "pop": 7_400, "area":  55.0, "elev": 740},
    {"dept": 4, "name": "Dulce Nombre de María", "lat": 14.178,"lng": -89.016, "pop":  5_500,  "area":  50.0, "elev": 900},
    {"dept": 4, "name": "El Carrizal",          "lat": 14.087, "lng": -88.744, "pop":  2_400,  "area":  12.0, "elev": 815},
    {"dept": 4, "name": "El Paraíso",           "lat": 14.135, "lng": -88.780, "pop":  3_100,  "area":  25.0, "elev": 560},
    {"dept": 4, "name": "La Laguna",            "lat": 14.170, "lng": -88.879, "pop":  3_200,  "area":  44.0, "elev": 1050},
    {"dept": 4, "name": "La Palma",             "lat": 14.318, "lng": -89.168, "pop": 14_500,  "area": 136.4, "elev": 1000},
    {"dept": 4, "name": "La Reina",             "lat": 14.183, "lng": -88.967, "pop":  5_200,  "area":  58.0, "elev": 850},
    {"dept": 4, "name": "Las Flores",           "lat": 14.086, "lng": -88.713, "pop":  2_700,  "area":  39.0, "elev": 700},
    {"dept": 4, "name": "Las Vueltas",          "lat": 14.044, "lng": -88.759, "pop":  1_600,  "area":  15.0, "elev": 470},
    {"dept": 4, "name": "Nombre de Jesús",      "lat": 14.050, "lng": -88.750, "pop":  2_700,  "area":  20.0, "elev": 600},
    {"dept": 4, "name": "Nueva Concepción",     "lat": 14.128, "lng": -89.301, "pop": 33_500,  "area": 258.0, "elev": 300},
    {"dept": 4, "name": "Nueva Trinidad",       "lat": 14.131, "lng": -88.817, "pop":  2_700,  "area":  36.0, "elev": 780},
    {"dept": 4, "name": "Ojos de Agua",         "lat": 14.065, "lng": -88.734, "pop":  2_800,  "area":  18.0, "elev": 830},
    {"dept": 4, "name": "Potonico",             "lat": 14.003, "lng": -88.794, "pop":  2_800,  "area":  36.0, "elev": 400},
    {"dept": 4, "name": "San Antonio de la Cruz","lat": 14.174,"lng": -88.962, "pop":  2_100,  "area":  30.0, "elev": 720},
    {"dept": 4, "name": "San Antonio Los Ranchos","lat": 14.037,"lng": -88.868, "pop": 1_600,  "area":  18.0, "elev": 430},
    {"dept": 4, "name": "San Fernando",         "lat": 14.345, "lng": -89.080, "pop":  3_600,  "area":  58.0, "elev": 1020},
    {"dept": 4, "name": "San Francisco Lempa",  "lat": 14.000, "lng": -88.870, "pop":  1_300,  "area":   7.2, "elev": 370},
    {"dept": 4, "name": "San Francisco Morazán", "lat": 14.082,"lng": -88.836, "pop":  3_200,  "area":  48.0, "elev": 500},
    {"dept": 4, "name": "San Ignacio",          "lat": 14.340, "lng": -89.130, "pop":  8_900,  "area":  53.0, "elev": 1150},
    {"dept": 4, "name": "San Isidro Labrador",  "lat": 14.070, "lng": -88.710, "pop":  1_500,  "area":  16.0, "elev": 500},
    {"dept": 4, "name": "San José Cancasque",   "lat": 14.020, "lng": -88.674, "pop":  4_200,  "area":  22.0, "elev": 550},
    {"dept": 4, "name": "San Luis del Carmen",  "lat": 14.082, "lng": -88.808, "pop":  2_200,  "area":  17.2, "elev": 490},
    {"dept": 4, "name": "San Miguel de Mercedes","lat": 14.110,"lng": -88.776, "pop":  2_300,  "area":  26.0, "elev": 700},
    {"dept": 4, "name": "San Rafael",           "lat": 14.055, "lng": -89.280, "pop":  6_000,  "area":  45.0, "elev": 310},
    {"dept": 4, "name": "Tejutla",              "lat": 14.221, "lng": -89.103, "pop": 12_800,  "area": 108.0, "elev": 680},

    # ── 5. La Libertad (22 municipios) ──
    {"dept": 5, "name": "Santa Tecla",          "lat": 13.677, "lng": -89.290, "pop": 164_000, "area": 112.0, "elev": 920},
    {"dept": 5, "name": "Antiguo Cuscatlán",    "lat": 13.665, "lng": -89.260, "pop": 40_000,  "area":  19.4, "elev": 800},
    {"dept": 5, "name": "Chiltiupán",           "lat": 13.566, "lng": -89.413, "pop": 11_500,  "area": 100.0, "elev": 400},
    {"dept": 5, "name": "Ciudad Arce",          "lat": 13.838, "lng": -89.443, "pop": 70_500,  "area": 114.0, "elev": 475},
    {"dept": 5, "name": "Colón",                "lat": 13.724, "lng": -89.369, "pop": 110_000, "area":  47.0, "elev": 580},
    {"dept": 5, "name": "Comasagua",            "lat": 13.596, "lng": -89.367, "pop": 14_200,  "area":  66.4, "elev": 1020},
    {"dept": 5, "name": "Huizúcar",             "lat": 13.600, "lng": -89.241, "pop": 16_500,  "area":  56.0, "elev": 780},
    {"dept": 5, "name": "Jayaque",              "lat": 13.654, "lng": -89.441, "pop": 10_800,  "area":  44.0, "elev": 920},
    {"dept": 5, "name": "Jicalapa",             "lat": 13.535, "lng": -89.402, "pop":  5_500,  "area":  36.0, "elev": 225},
    {"dept": 5, "name": "La Libertad",          "lat": 13.488, "lng": -89.323, "pop": 43_200,  "area": 162.0, "elev": 10},
    {"dept": 5, "name": "Nuevo Cuscatlán",      "lat": 13.648, "lng": -89.271, "pop": 10_800,  "area":  16.0, "elev": 780},
    {"dept": 5, "name": "Opico",                "lat": 13.862, "lng": -89.390, "pop": 82_000,  "area": 250.0, "elev": 460},
    {"dept": 5, "name": "Quezaltepeque",        "lat": 13.831, "lng": -89.272, "pop": 65_000,  "area": 115.2, "elev": 490},
    {"dept": 5, "name": "Sacacoyo",             "lat": 13.722, "lng": -89.458, "pop": 12_200,  "area":  26.0, "elev": 580},
    {"dept": 5, "name": "San José Villanueva",  "lat": 13.586, "lng": -89.276, "pop": 23_000,  "area":  36.0, "elev": 260},
    {"dept": 5, "name": "San Juan Opico",       "lat": 13.876, "lng": -89.357, "pop": 78_000,  "area": 111.0, "elev": 450},
    {"dept": 5, "name": "San Matías",           "lat": 13.870, "lng": -89.465, "pop":  3_700,  "area":  32.0, "elev": 430},
    {"dept": 5, "name": "San Pablo Tacachico",  "lat": 13.974, "lng": -89.345, "pop": 24_500,  "area": 149.0, "elev": 360},
    {"dept": 5, "name": "Talnique",             "lat": 13.671, "lng": -89.426, "pop":  8_200,  "area":  24.0, "elev": 890},
    {"dept": 5, "name": "Tamanique",            "lat": 13.580, "lng": -89.420, "pop": 13_500,  "area":  84.0, "elev": 600},
    {"dept": 5, "name": "Teotepeque",           "lat": 13.564, "lng": -89.503, "pop": 10_200,  "area":  70.0, "elev": 380},
    {"dept": 5, "name": "Tepecoyo",             "lat": 13.660, "lng": -89.479, "pop": 14_000,  "area":  38.0, "elev": 780},

    # ── 6. San Salvador (19 municipios) ──
    {"dept": 6, "name": "San Salvador",         "lat": 13.698, "lng": -89.191, "pop": 570_000, "area": 72.3,  "elev": 658},
    {"dept": 6, "name": "Aguilares",            "lat": 13.957, "lng": -89.189, "pop": 26_000,  "area":  26.8, "elev": 340},
    {"dept": 6, "name": "Apopa",                "lat": 13.807, "lng": -89.181, "pop": 165_000, "area":  51.8, "elev": 460},
    {"dept": 6, "name": "Ayutuxtepeque",        "lat": 13.738, "lng": -89.205, "pop": 41_500,  "area":   8.4, "elev": 660},
    {"dept": 6, "name": "Cuscatancingo",        "lat": 13.730, "lng": -89.183, "pop": 78_000,  "area":   5.4, "elev": 620},
    {"dept": 6, "name": "Ciudad Delgado",       "lat": 13.726, "lng": -89.170, "pop": 140_000, "area":  33.4, "elev": 610},
    {"dept": 6, "name": "El Paisnal",           "lat": 13.972, "lng": -89.218, "pop": 16_000,  "area":  76.0, "elev": 345},
    {"dept": 6, "name": "Guazapa",              "lat": 13.878, "lng": -89.173, "pop": 26_000,  "area":  67.6, "elev": 420},
    {"dept": 6, "name": "Ilopango",             "lat": 13.695, "lng": -89.108, "pop": 130_000, "area":  34.6, "elev": 615},
    {"dept": 6, "name": "Mejicanos",            "lat": 13.729, "lng": -89.213, "pop": 165_000, "area":  22.1, "elev": 650},
    {"dept": 6, "name": "Nejapa",               "lat": 13.816, "lng": -89.228, "pop": 35_000,  "area":  83.4, "elev": 470},
    {"dept": 6, "name": "Panchimalco",          "lat": 13.610, "lng": -89.180, "pop": 45_000,  "area":  47.0, "elev": 560},
    {"dept": 6, "name": "Rosario de Mora",      "lat": 13.577, "lng": -89.199, "pop": 12_000,  "area":  30.0, "elev": 420},
    {"dept": 6, "name": "San Marcos",           "lat": 13.658, "lng": -89.183, "pop": 72_000,  "area":  14.8, "elev": 640},
    {"dept": 6, "name": "San Martín",           "lat": 13.787, "lng": -89.057, "pop": 105_000, "area":  55.8, "elev": 620},
    {"dept": 6, "name": "Santiago Texacuangos",  "lat": 13.627,"lng": -89.140, "pop": 20_000,  "area":  25.6, "elev": 750},
    {"dept": 6, "name": "Santo Tomás",          "lat": 13.640, "lng": -89.134, "pop": 32_500,  "area":  24.0, "elev": 650},
    {"dept": 6, "name": "Soyapango",            "lat": 13.710, "lng": -89.138, "pop": 290_000, "area":  29.7, "elev": 620},
    {"dept": 6, "name": "Tonacatepeque",        "lat": 13.779, "lng": -89.112, "pop": 115_000, "area":  67.6, "elev": 600},

    # ── 7. Cuscatlán (16 municipios) ──
    {"dept": 7, "name": "Cojutepeque",          "lat": 13.717, "lng": -88.935, "pop": 52_000,  "area":  30.0, "elev": 860},
    {"dept": 7, "name": "Candelaria",           "lat": 13.700, "lng": -88.877, "pop": 10_500,  "area":  31.0, "elev": 700},
    {"dept": 7, "name": "El Carmen",            "lat": 13.694, "lng": -88.944, "pop": 13_200,  "area":  26.0, "elev": 800},
    {"dept": 7, "name": "El Rosario",           "lat": 13.714, "lng": -88.965, "pop":  7_600,  "area":  18.0, "elev": 780},
    {"dept": 7, "name": "Monte San Juan",       "lat": 13.705, "lng": -88.981, "pop":  4_200,  "area":  14.0, "elev": 800},
    {"dept": 7, "name": "Oratorio de Concepción","lat": 13.710,"lng": -88.908, "pop":  2_800, "area":   6.8, "elev": 850},
    {"dept": 7, "name": "San Bartolomé Perulapía","lat": 13.748,"lng": -89.051, "pop": 10_000,"area":  14.0, "elev": 530},
    {"dept": 7, "name": "San Cristóbal",        "lat": 13.699, "lng": -88.894, "pop": 15_000,  "area":  46.0, "elev": 680},
    {"dept": 7, "name": "San José Guayabal",    "lat": 13.801, "lng": -89.007, "pop":  9_800,  "area":  76.0, "elev": 520},
    {"dept": 7, "name": "San Pedro Perulapán",  "lat": 13.766, "lng": -88.940, "pop": 55_000,  "area": 108.0, "elev": 690},
    {"dept": 7, "name": "San Rafael Cedros",    "lat": 13.728, "lng": -88.913, "pop": 20_500,  "area":  25.0, "elev": 720},
    {"dept": 7, "name": "San Ramón",            "lat": 13.699, "lng": -88.926, "pop":  8_200,  "area":  19.0, "elev": 760},
    {"dept": 7, "name": "Santa Cruz Analquito",  "lat": 13.701,"lng": -88.971, "pop":  3_600, "area":   8.0, "elev": 820},
    {"dept": 7, "name": "Santa Cruz Michapa",    "lat": 13.746,"lng": -88.983, "pop": 13_800, "area":  20.0, "elev": 600},
    {"dept": 7, "name": "Suchitoto",            "lat": 13.938, "lng": -89.028, "pop": 25_000,  "area": 329.2, "elev": 400},
    {"dept": 7, "name": "Tenancingo",           "lat": 13.685, "lng": -88.987, "pop":  7_000,  "area":  17.0, "elev": 810},

    # ── 8. La Paz (22 municipios) ──
    {"dept": 8, "name": "Zacatecoluca",         "lat": 13.517, "lng": -88.870, "pop": 75_000,  "area": 321.2, "elev": 260},
    {"dept": 8, "name": "Cuyultitán",           "lat": 13.534, "lng": -89.086, "pop":  7_300,  "area":   7.0, "elev": 80},
    {"dept": 8, "name": "El Rosario (LP)",      "lat": 13.498, "lng": -89.037, "pop": 26_000,  "area":  26.0, "elev": 120},
    {"dept": 8, "name": "Jerusalén",            "lat": 13.567, "lng": -88.853, "pop":  3_200,  "area":  19.0, "elev": 480},
    {"dept": 8, "name": "Mercedes La Ceiba",    "lat": 13.567, "lng": -88.860, "pop":  2_300,  "area":  12.0, "elev": 420},
    {"dept": 8, "name": "Olocuilta",            "lat": 13.568, "lng": -89.117, "pop": 46_000,  "area":  59.0, "elev": 130},
    {"dept": 8, "name": "Paraíso de Osorio",    "lat": 13.567, "lng": -88.870, "pop":  2_100,  "area":  12.0, "elev": 450},
    {"dept": 8, "name": "San Antonio Masahuat",  "lat": 13.510,"lng": -88.978, "pop":  5_100, "area":  19.0, "elev": 250},
    {"dept": 8, "name": "San Emigdio",          "lat": 13.480, "lng": -88.883, "pop":  3_100,  "area":  14.0, "elev": 280},
    {"dept": 8, "name": "San Francisco Chinameca","lat": 13.548,"lng": -89.066, "pop": 9_500, "area":  28.0, "elev": 100},
    {"dept": 8, "name": "San Juan Nonualco",    "lat": 13.554, "lng": -88.900, "pop": 25_000,  "area":  58.0, "elev": 330},
    {"dept": 8, "name": "San Juan Talpa",       "lat": 13.467, "lng": -89.083, "pop":  7_800,  "area":  31.0, "elev": 30},
    {"dept": 8, "name": "San Juan Tepezontes",   "lat": 13.569,"lng": -89.020, "pop":  5_300, "area":  26.0, "elev": 430},
    {"dept": 8, "name": "San Luis La Herradura", "lat": 13.335,"lng": -88.970, "pop": 21_000, "area": 104.0, "elev": 5},
    {"dept": 8, "name": "San Luis Talpa",       "lat": 13.473, "lng": -89.092, "pop": 23_000,  "area":  62.0, "elev": 25},
    {"dept": 8, "name": "San Miguel Tepezontes", "lat": 13.583,"lng": -89.032, "pop":  4_800, "area":  31.0, "elev": 530},
    {"dept": 8, "name": "San Pedro Masahuat",   "lat": 13.500, "lng": -89.004, "pop": 28_000,  "area":  73.0, "elev": 150},
    {"dept": 8, "name": "San Pedro Nonualco",   "lat": 13.586, "lng": -88.929, "pop": 12_000,  "area":  35.0, "elev": 560},
    {"dept": 8, "name": "San Rafael Obrajuelo",  "lat": 13.533,"lng": -88.910, "pop": 13_000, "area":  33.0, "elev": 280},
    {"dept": 8, "name": "Santa María Ostuma",   "lat": 13.596, "lng": -88.775, "pop":  5_800,  "area":  52.0, "elev": 820},
    {"dept": 8, "name": "Santiago Nonualco",    "lat": 13.515, "lng": -88.951, "pop": 40_000,  "area": 120.0, "elev": 240},
    {"dept": 8, "name": "Tapalhuaca",           "lat": 13.529, "lng": -88.971, "pop":  4_300,  "area":  20.0, "elev": 300},

    # ── 9. Cabañas (9 municipios) ──
    {"dept": 9, "name": "Sensuntepeque",        "lat": 13.876, "lng": -88.630, "pop": 47_000,  "area": 306.0, "elev": 750},
    {"dept": 9, "name": "Cinquera",             "lat": 13.881, "lng": -88.965, "pop":  2_800,  "area":  48.0, "elev": 500},
    {"dept": 9, "name": "Dolores",              "lat": 13.870, "lng": -88.707, "pop":  6_800,  "area":  36.0, "elev": 600},
    {"dept": 9, "name": "Guacotecti",           "lat": 13.872, "lng": -88.660, "pop":  6_200,  "area":  32.0, "elev": 650},
    {"dept": 9, "name": "Ilobasco",             "lat": 13.842, "lng": -88.845, "pop": 67_000,  "area": 249.6, "elev": 720},
    {"dept": 9, "name": "Jutiapa",              "lat": 13.839, "lng": -88.757, "pop": 13_500,  "area":  92.0, "elev": 500},
    {"dept": 9, "name": "San Isidro (CB)",      "lat": 13.841, "lng": -88.650, "pop": 10_000,  "area":  66.0, "elev": 580},
    {"dept": 9, "name": "Tejutepeque",          "lat": 13.840, "lng": -88.882, "pop":  6_200,  "area":  60.0, "elev": 580},
    {"dept": 9, "name": "Victoria",             "lat": 13.951, "lng": -88.646, "pop":  8_800,  "area": 115.0, "elev": 640},

    # ── 10. San Vicente (13 municipios) ──
    {"dept": 10, "name": "San Vicente",         "lat": 13.641, "lng": -88.784, "pop": 55_000,  "area": 267.0, "elev": 390},
    {"dept": 10, "name": "Apastepeque",         "lat": 13.665, "lng": -88.762, "pop": 20_000,  "area": 120.0, "elev": 620},
    {"dept": 10, "name": "Guadalupe",           "lat": 13.623, "lng": -88.779, "pop": 10_000,  "area":  30.0, "elev": 470},
    {"dept": 10, "name": "San Cayetano Istepeque","lat": 13.634,"lng": -88.828, "pop": 5_600, "area":  17.0, "elev": 430},
    {"dept": 10, "name": "San Esteban Catarina", "lat": 13.712,"lng": -88.703, "pop":  5_800, "area":  50.0, "elev": 820},
    {"dept": 10, "name": "San Ildefonso",       "lat": 13.678, "lng": -88.608, "pop":  8_800,  "area": 101.0, "elev": 400},
    {"dept": 10, "name": "San Lorenzo",         "lat": 13.668, "lng": -88.749, "pop":  7_500,  "area":  23.0, "elev": 600},
    {"dept": 10, "name": "San Sebastián",       "lat": 13.735, "lng": -88.832, "pop": 15_500,  "area":  66.0, "elev": 600},
    {"dept": 10, "name": "Santa Clara",         "lat": 13.663, "lng": -88.663, "pop":  6_000,  "area":  43.0, "elev": 420},
    {"dept": 10, "name": "Santo Domingo",       "lat": 13.710, "lng": -88.780, "pop":  7_200,  "area":  36.0, "elev": 700},
    {"dept": 10, "name": "Tecoluca",            "lat": 13.530, "lng": -88.780, "pop": 28_000,  "area": 285.0, "elev": 50},
    {"dept": 10, "name": "Tepetitán",           "lat": 13.663, "lng": -88.802, "pop":  4_500,  "area":  17.0, "elev": 420},
    {"dept": 10, "name": "Verapaz",             "lat": 13.646, "lng": -88.857, "pop": 10_000,  "area":  35.0, "elev": 500},

    # ── 11. Usulután (23 municipios) ──
    {"dept": 11, "name": "Usulután",            "lat": 13.441, "lng": -88.440, "pop": 77_000,  "area": 216.0, "elev": 90},
    {"dept": 11, "name": "Alegría",             "lat": 13.493, "lng": -88.493, "pop": 11_000,  "area":  62.0, "elev": 1240},
    {"dept": 11, "name": "Berlín",              "lat": 13.497, "lng": -88.530, "pop": 18_500,  "area":  88.0, "elev": 1020},
    {"dept": 11, "name": "California",          "lat": 13.466, "lng": -88.575, "pop":  3_500,  "area":  22.0, "elev": 320},
    {"dept": 11, "name": "Concepción Batres",   "lat": 13.372, "lng": -88.373, "pop": 12_500,  "area":  83.0, "elev": 80},
    {"dept": 11, "name": "El Triunfo",          "lat": 13.530, "lng": -88.545, "pop":  5_500,  "area":  35.0, "elev": 900},
    {"dept": 11, "name": "Ereguayquín",         "lat": 13.421, "lng": -88.385, "pop":  8_000,  "area":  38.0, "elev": 100},
    {"dept": 11, "name": "Estanzuelas",         "lat": 13.447, "lng": -88.435, "pop":  6_200,  "area":  30.0, "elev": 180},
    {"dept": 11, "name": "Jiquilisco",          "lat": 13.321, "lng": -88.573, "pop": 52_000,  "area": 446.0, "elev": 10},
    {"dept": 11, "name": "Jucuapa",             "lat": 13.517, "lng": -88.387, "pop": 18_000,  "area":  70.0, "elev": 500},
    {"dept": 11, "name": "Jucuarán",            "lat": 13.248, "lng": -88.248, "pop": 11_000,  "area": 160.0, "elev": 100},
    {"dept": 11, "name": "Mercedes Umaña",      "lat": 13.483, "lng": -88.445, "pop": 11_000,  "area":  44.0, "elev": 370},
    {"dept": 11, "name": "Nueva Granada",       "lat": 13.505, "lng": -88.482, "pop":  5_200,  "area":  96.0, "elev": 600},
    {"dept": 11, "name": "Ozatlán",             "lat": 13.385, "lng": -88.497, "pop": 15_000,  "area":  66.0, "elev": 200},
    {"dept": 11, "name": "Puerto El Triunfo",   "lat": 13.283, "lng": -88.550, "pop": 22_000,  "area": 108.0, "elev": 5},
    {"dept": 11, "name": "San Agustín",         "lat": 13.442, "lng": -88.601, "pop":  5_200,  "area":  52.0, "elev": 350},
    {"dept": 11, "name": "San Buenaventura",    "lat": 13.428, "lng": -88.387, "pop":  3_600,  "area":  13.0, "elev": 180},
    {"dept": 11, "name": "San Dionisio",        "lat": 13.473, "lng": -88.406, "pop":  4_800,  "area":  22.0, "elev": 300},
    {"dept": 11, "name": "San Francisco Javier", "lat": 13.438,"lng": -88.535, "pop":  3_500, "area":  13.0, "elev": 370},
    {"dept": 11, "name": "Santa Elena",         "lat": 13.385, "lng": -88.413, "pop": 17_500,  "area":  54.0, "elev": 100},
    {"dept": 11, "name": "Santa María",         "lat": 13.478, "lng": -88.535, "pop": 15_000,  "area":  87.0, "elev": 520},
    {"dept": 11, "name": "Santiago de María",   "lat": 13.486, "lng": -88.471, "pop": 21_000,  "area":  30.0, "elev": 920},
    {"dept": 11, "name": "Tecapán",             "lat": 13.466, "lng": -88.510, "pop":  7_000,  "area":  70.0, "elev": 600},

    # ── 12. San Miguel (20 municipios) ──
    {"dept": 12, "name": "San Miguel",          "lat": 13.480, "lng": -88.177, "pop": 270_000, "area": 594.0, "elev": 110},
    {"dept": 12, "name": "Carolina",            "lat": 13.715, "lng": -88.100, "pop":  5_500,  "area": 120.0, "elev": 780},
    {"dept": 12, "name": "Chapeltique",         "lat": 13.633, "lng": -88.267, "pop": 12_000,  "area":  76.0, "elev": 480},
    {"dept": 12, "name": "Chinameca",           "lat": 13.500, "lng": -88.333, "pop": 30_000,  "area":  82.0, "elev": 500},
    {"dept": 12, "name": "Chirilagua",          "lat": 13.224, "lng": -88.140, "pop": 22_000,  "area": 164.0, "elev": 30},
    {"dept": 12, "name": "Ciudad Barrios",      "lat": 13.767, "lng": -88.267, "pop": 28_000,  "area": 184.0, "elev": 810},
    {"dept": 12, "name": "Comacarán",           "lat": 13.522, "lng": -88.150, "pop":  3_200,  "area":  24.0, "elev": 360},
    {"dept": 12, "name": "El Tránsito",         "lat": 13.380, "lng": -88.333, "pop": 18_000,  "area": 100.0, "elev": 180},
    {"dept": 12, "name": "Lolotique",           "lat": 13.550, "lng": -88.350, "pop": 14_500,  "area":  70.0, "elev": 700},
    {"dept": 12, "name": "Moncagua",            "lat": 13.533, "lng": -88.250, "pop": 18_000,  "area":  58.0, "elev": 270},
    {"dept": 12, "name": "Nueva Guadalupe",     "lat": 13.540, "lng": -88.370, "pop":  9_500,  "area":  14.0, "elev": 400},
    {"dept": 12, "name": "Nuevo Edén de San Juan","lat": 13.743,"lng": -88.133, "pop":  5_200, "area":  96.0, "elev": 450},
    {"dept": 12, "name": "Quelepa",             "lat": 13.503, "lng": -88.233, "pop":  5_800,  "area":  13.0, "elev": 200},
    {"dept": 12, "name": "San Antonio",         "lat": 13.657, "lng": -88.133, "pop":  4_800,  "area":  48.0, "elev": 620},
    {"dept": 12, "name": "San Gerardo",         "lat": 13.630, "lng": -88.267, "pop":  4_500,  "area":  21.0, "elev": 550},
    {"dept": 12, "name": "San Jorge",           "lat": 13.433, "lng": -88.333, "pop": 10_500,  "area":  52.0, "elev": 310},
    {"dept": 12, "name": "San Luis de la Reina", "lat": 13.734,"lng": -88.133, "pop":  4_000, "area":  58.0, "elev": 600},
    {"dept": 12, "name": "San Rafael Oriente",  "lat": 13.385, "lng": -88.350, "pop": 13_000,  "area":  36.0, "elev": 240},
    {"dept": 12, "name": "Sesori",              "lat": 13.717, "lng": -88.367, "pop": 12_000,  "area": 162.0, "elev": 480},
    {"dept": 12, "name": "Uluazapa",            "lat": 13.450, "lng": -88.200, "pop":  6_000,  "area":  32.0, "elev": 190},

    # ── 13. Morazán (26 municipios) ──
    {"dept": 13, "name": "San Francisco Gotera", "lat": 13.700,"lng": -88.100, "pop": 26_000, "area":  48.0, "elev": 280},
    {"dept": 13, "name": "Arambala",            "lat": 13.908, "lng": -88.133, "pop":  2_500,  "area":  35.0, "elev": 860},
    {"dept": 13, "name": "Cacaopera",           "lat": 13.770, "lng": -88.083, "pop": 11_000,  "area":  76.0, "elev": 420},
    {"dept": 13, "name": "Chilanga",            "lat": 13.720, "lng": -88.117, "pop":  9_500,  "area":  75.0, "elev": 400},
    {"dept": 13, "name": "Corinto",             "lat": 13.780, "lng": -87.970, "pop": 17_500,  "area":  76.0, "elev": 460},
    {"dept": 13, "name": "Delicias de Concepción","lat": 13.700,"lng": -88.050, "pop": 3_200, "area":  16.0, "elev": 350},
    {"dept": 13, "name": "El Divisadero",       "lat": 13.700, "lng": -88.167, "pop":  7_500,  "area":  58.0, "elev": 380},
    {"dept": 13, "name": "El Rosario (MO)",     "lat": 13.750, "lng": -88.017, "pop":  5_200,  "area":  35.0, "elev": 400},
    {"dept": 13, "name": "Gualococti",          "lat": 13.780, "lng": -88.133, "pop":  3_500,  "area":  27.0, "elev": 520},
    {"dept": 13, "name": "Guatajiagua",         "lat": 13.667, "lng": -88.200, "pop": 12_500,  "area":  67.0, "elev": 350},
    {"dept": 13, "name": "Joateca",             "lat": 13.885, "lng": -88.067, "pop":  6_800,  "area":  72.0, "elev": 800},
    {"dept": 13, "name": "Jocoaitique",         "lat": 13.833, "lng": -88.117, "pop":  3_200,  "area":  30.0, "elev": 680},
    {"dept": 13, "name": "Jocoro",              "lat": 13.617, "lng": -88.017, "pop": 17_000,  "area":  62.0, "elev": 320},
    {"dept": 13, "name": "Lolotiquillo",        "lat": 13.750, "lng": -88.067, "pop":  5_800,  "area":  36.0, "elev": 500},
    {"dept": 13, "name": "Meanguera",           "lat": 13.867, "lng": -88.083, "pop":  5_200,  "area":  76.0, "elev": 800},
    {"dept": 13, "name": "Osicala",             "lat": 13.800, "lng": -88.150, "pop":  8_200,  "area":  68.0, "elev": 580},
    {"dept": 13, "name": "Perquín",             "lat": 13.956, "lng": -88.167, "pop":  3_500,  "area":  58.0, "elev": 1200},
    {"dept": 13, "name": "San Carlos",          "lat": 13.643, "lng": -88.100, "pop":  4_500,  "area":  36.0, "elev": 340},
    {"dept": 13, "name": "San Fernando (MO)",   "lat": 13.867, "lng": -88.167, "pop":  3_000,  "area":  42.0, "elev": 900},
    {"dept": 13, "name": "San Isidro (MO)",     "lat": 13.750, "lng": -88.133, "pop":  3_000,  "area":  21.0, "elev": 450},
    {"dept": 13, "name": "San Simón",           "lat": 13.817, "lng": -88.233, "pop":  7_800,  "area":  52.0, "elev": 550},
    {"dept": 13, "name": "Sensembra",           "lat": 13.733, "lng": -88.017, "pop":  3_200,  "area":  18.0, "elev": 380},
    {"dept": 13, "name": "Sociedad",            "lat": 13.717, "lng": -87.983, "pop": 10_500,  "area":  67.0, "elev": 400},
    {"dept": 13, "name": "Torola",              "lat": 13.883, "lng": -88.117, "pop":  2_500,  "area":  52.0, "elev": 750},
    {"dept": 13, "name": "Yamabal",             "lat": 13.683, "lng": -88.133, "pop":  4_200,  "area":  42.0, "elev": 400},
    {"dept": 13, "name": "Yoloaiquín",          "lat": 13.717, "lng": -88.167, "pop":  3_500,  "area":  22.0, "elev": 380},

    # ── 14. La Unión (18 municipios) ──
    {"dept": 14, "name": "La Unión",            "lat": 13.338, "lng": -87.843, "pop": 35_000,  "area":  96.0, "elev": 10},
    {"dept": 14, "name": "Anamorós",            "lat": 13.733, "lng": -87.883, "pop": 12_000,  "area":  96.0, "elev": 460},
    {"dept": 14, "name": "Bolívar",             "lat": 13.633, "lng": -87.833, "pop":  2_800,  "area":  24.0, "elev": 300},
    {"dept": 14, "name": "Concepción de Oriente","lat": 13.830,"lng": -87.867, "pop":  6_200, "area":  44.0, "elev": 500},
    {"dept": 14, "name": "Conchagua",           "lat": 13.307, "lng": -87.863, "pop": 40_000,  "area": 206.0, "elev": 200},
    {"dept": 14, "name": "El Carmen (LU)",      "lat": 13.550, "lng": -87.800, "pop":  9_500,  "area":  96.0, "elev": 300},
    {"dept": 14, "name": "El Sauce",            "lat": 13.650, "lng": -87.800, "pop":  8_500,  "area":  58.0, "elev": 310},
    {"dept": 14, "name": "Intipucá",            "lat": 13.200, "lng": -88.050, "pop":  8_500,  "area":  94.0, "elev": 10},
    {"dept": 14, "name": "Lislique",            "lat": 13.850, "lng": -87.933, "pop": 13_000,  "area":  56.0, "elev": 480},
    {"dept": 14, "name": "Meanguera del Golfo",  "lat": 13.183,"lng": -87.833, "pop":  3_500, "area":  14.0, "elev": 20},
    {"dept": 14, "name": "Nueva Esparta",       "lat": 13.750, "lng": -87.833, "pop":  4_200,  "area":  36.0, "elev": 380},
    {"dept": 14, "name": "Pasaquina",           "lat": 13.583, "lng": -87.833, "pop": 16_500,  "area": 238.0, "elev": 60},
    {"dept": 14, "name": "Polorós",             "lat": 13.800, "lng": -87.883, "pop":  7_200,  "area":  56.0, "elev": 540},
    {"dept": 14, "name": "San Alejo",           "lat": 13.433, "lng": -87.967, "pop": 19_000,  "area": 348.0, "elev": 180},
    {"dept": 14, "name": "San José",            "lat": 13.517, "lng": -87.850, "pop": 10_800,  "area":  80.0, "elev": 280},
    {"dept": 14, "name": "Santa Rosa de Lima",  "lat": 13.625, "lng": -87.893, "pop": 36_000,  "area": 120.0, "elev": 200},
    {"dept": 14, "name": "Yayantique",          "lat": 13.500, "lng": -87.833, "pop":  6_000,  "area":  52.0, "elev": 220},
    {"dept": 14, "name": "Yucuaiquín",          "lat": 13.517, "lng": -87.950, "pop":  8_200,  "area":  72.0, "elev": 300},
]
# fmt: on

# Coverage categories tracked per municipio
COVERAGE_CATEGORIES = [
    "property_listings",    # Do we have real estate listings?
    "pricing_data",         # Do we have actual sale/rental prices?
    "property_images",      # Are there high-quality property images?
    "street_imagery",       # Google Street View / Mapillary coverage?
    "tourism_info",         # Hotels, restaurants, attractions data?
    "infrastructure_data",  # Roads, utilities, internet connectivity?
    "safety_data",          # Crime stats / perception at local level?
    "demographic_data",     # Population, income, employment at muni level?
]


def generate_seed_sql() -> str:
    """Generate raw SQL INSERT statements for use without Python ORM."""

    lines = [
        "-- ================================================",
        "-- El Salvador Administrative Divisions Seed Data",
        "-- Generated by seed_admin_divisions.py",
        "-- ================================================",
        "",
        "BEGIN;",
        "",
        "-- Enable PostGIS",
        "CREATE EXTENSION IF NOT EXISTS postgis;",
        "",
        "-- ── Departments ──",
    ]

    for d in DEPARTMENTS:
        lines.append(
            f"INSERT INTO departments (id, name, name_es, capital, area_km2, population, population_year, iso_code, centroid_lat, centroid_lng) "
            f"VALUES ({d['id']}, '{d['name']}', '{d['name_es']}', '{d['capital']}', {d['area_km2']}, {d['population']}, {d['pop_year']}, "
            f"'{d['iso']}', {d['lat']}, {d['lng']}) ON CONFLICT (id) DO NOTHING;"
        )

    lines.append("")
    lines.append("-- ── Municipios ──")

    for i, m in enumerate(MUNICIPIOS, start=1):
        name_escaped = m["name"].replace("'", "''")
        lines.append(
            f"INSERT INTO municipios (id, name, name_es, department_id, population, population_year, area_km2, elevation_m, centroid_lat, centroid_lng) "
            f"VALUES ({i}, '{name_escaped}', '{name_escaped}', {m['dept']}, {m['pop']}, 2023, "
            f"{m.get('area', 0)}, {m.get('elev', 0)}, {m['lat']}, {m['lng']}) ON CONFLICT (id) DO NOTHING;"
        )

    lines.append("")
    lines.append("-- ── Initial Coverage Gap Records (all scored 0 = no data) ──")

    gap_id = 0
    for i, m in enumerate(MUNICIPIOS, start=1):
        for cat in COVERAGE_CATEGORIES:
            gap_id += 1
            name_escaped = m["name"].replace("'", "''")
            # Determine priority: larger populations = higher priority
            pop = m.get("pop", 0)
            if pop >= 50_000:
                priority = "critical"
            elif pop >= 20_000:
                priority = "high"
            elif pop >= 10_000:
                priority = "medium"
            else:
                priority = "low"

            needs_field = "true" if pop >= 5_000 else "false"

            lines.append(
                f"INSERT INTO data_coverage_gaps (id, municipio_id, category, coverage_score, priority, needs_field_research) "
                f"VALUES (gen_random_uuid(), {i}, '{cat}', 0.0, '{priority}', {needs_field}) "
                f"ON CONFLICT ON CONSTRAINT uq_gap_municipio_cat DO NOTHING;"
            )

    lines.append("")
    lines.append("COMMIT;")
    lines.append("")

    return "\n".join(lines)


def generate_coverage_report() -> str:
    """
    Generate a text report of expected data coverage gaps.
    This is the "where we need boots on the ground" analysis.
    """
    report_lines = [
        "=" * 70,
        "EL SALVADOR — DATA COVERAGE GAP ANALYSIS",
        "=" * 70,
        "",
        f"Total Departments: {len(DEPARTMENTS)}",
        f"Total Municipios:  {len(MUNICIPIOS)}",
        f"Coverage Categories: {len(COVERAGE_CATEGORIES)}",
        f"Total Gap Records: {len(MUNICIPIOS) * len(COVERAGE_CATEGORIES)}",
        "",
        "─" * 70,
        "PRIORITY BREAKDOWN (by population)",
        "─" * 70,
    ]

    priority_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    dept_stats: dict[int, dict] = {}

    for m in MUNICIPIOS:
        pop = m.get("pop", 0)
        if pop >= 50_000:
            p = "critical"
        elif pop >= 20_000:
            p = "high"
        elif pop >= 10_000:
            p = "medium"
        else:
            p = "low"
        priority_counts[p] += 1

        d = m["dept"]
        if d not in dept_stats:
            dept_stats[d] = {"count": 0, "total_pop": 0, "names": []}
        dept_stats[d]["count"] += 1
        dept_stats[d]["total_pop"] += pop
        dept_stats[d]["names"].append(m["name"])

    for p, count in priority_counts.items():
        report_lines.append(f"  {p.upper():10s}: {count} municipios")

    report_lines.append("")
    report_lines.append("─" * 70)
    report_lines.append("CRITICAL GAPS — NEEDS IMMEDIATE FIELD RESEARCH")
    report_lines.append("(Municipios with 50,000+ population, zero property data)")
    report_lines.append("─" * 70)

    for m in sorted(MUNICIPIOS, key=lambda x: x.get("pop", 0), reverse=True):
        if m.get("pop", 0) >= 50_000:
            dept_name = next((d["name"] for d in DEPARTMENTS if d["id"] == m["dept"]), "?")
            report_lines.append(
                f"  🔴 {m['name']:30s} | {dept_name:20s} | Pop: {m['pop']:>10,} | "
                f"Coords: ({m['lat']:.3f}, {m['lng']:.3f})"
            )

    report_lines.append("")
    report_lines.append("─" * 70)
    report_lines.append("KNOWN DATA DESERT ZONES")
    report_lines.append("(Areas where imagery, listings, and info are hardest to find)")
    report_lines.append("─" * 70)

    # These are empirically known hard-to-reach / under-documented areas
    DESERTS = [
        ("Morazán — Northern Mountains", [
            "Perquín", "Arambala", "Meanguera", "Joateca", "Torola",
            "San Fernando (MO)", "Jocoaitique",
        ], "Remote mountainous terrain, Ruta de Paz area. Former conflict zone. Very few real estate listings or street imagery. NEEDS: local contacts, drone photography, community engagement."),

        ("Chalatenango — Northern Border", [
            "Citalá", "San Ignacio", "La Palma", "San Fernando",
            "Dulce Nombre de María", "Arcatao", "Las Vueltas", "Las Flores",
        ], "Rural highlands near Honduras border. Limited internet. Some ecotourism (La Palma artisan town). NEEDS: road condition surveys, property value baselines, local market interviews."),

        ("Cabañas — Interior", [
            "Cinquera", "Victoria", "Dolores", "Guacotecti",
            "San Isidro (CB)", "Tejutepeque",
        ], "Least-visited department. Former guerrilla territory. Cinquera forest reserve. Very few online listings. NEEDS: municipal office data, local broker contacts, environmental surveys."),

        ("La Unión — Eastern Coast", [
            "Meanguera del Golfo", "Intipucá", "Conchagua",
            "Bolívar", "Nueva Esparta",
        ], "Islands in Gulf of Fonseca (Meanguera del Golfo). Intipucá = remittance town. Conchagua volcano area. NEEDS: coastal property surveys, tourism asset inventory, port development data."),

        ("Northern Usulután / San Miguel", [
            "Carolina", "Nuevo Edén de San Juan", "San Luis de la Reina",
            "San Antonio", "Sesori",
        ], "Remote eastern highlands. Very limited road access. Sparse population. Almost zero online real estate presence. NEEDS: community-level data, basic mapping, school inventories."),

        ("Sonsonate — Indigenous Areas", [
            "Cuisnahuat", "Santa Isabel Ishuatán",
            "Santo Domingo de Guzmán", "Santa Catarina Masahuat",
        ], "Indigenous Nahua-Pipil communities. Rich cultural heritage but limited digital presence. NEEDS: culturally sensitive documentation, community permissions, bilingual (Náhuat/Spanish) data collection."),
    ]

    for zone_name, municipios, notes in DESERTS:
        report_lines.append(f"\n  📍 {zone_name}")
        report_lines.append(f"     Municipios: {', '.join(municipios)}")
        report_lines.append(f"     Notes: {notes}")

    report_lines.append("")
    report_lines.append("─" * 70)
    report_lines.append("HIGH-VALUE TARGETS — BEST DATA AVAILABLE")
    report_lines.append("(Start scrapers here for quickest results)")
    report_lines.append("─" * 70)

    HIGH_VALUE = [
        ("San Salvador Metro", ["San Salvador", "Soyapango", "Mejicanos", "Apopa", "Ilopango", "Ciudad Delgado", "Santa Tecla", "Antiguo Cuscatlán"],
         "Highest listing density on Encuentra24 / OLX. Many real estate agents online. Google Street View coverage good."),
        ("Beach & Tourism Corridor", ["La Libertad", "Tamanique", "El Tunco area (Tamanique)", "Acajutla", "San Luis La Herradura"],
         "Active vacation rental market. Airbnb/VRBO presence. High foreigner interest."),
        ("Eastern Urban", ["San Miguel", "Santa Ana", "Usulután"],
         "Second/third tier cities with active property markets. Some online listings."),
        ("Coffee Route", ["Apaneca", "Juayúa", "Concepción de Ataco", "Salcoatitán"],
         "Ruta de las Flores tourism zone. Growing boutique hotel / B&B market."),
    ]

    for zone_name, municipios, notes in HIGH_VALUE:
        report_lines.append(f"\n  🟢 {zone_name}")
        report_lines.append(f"     Municipios: {', '.join(municipios)}")
        report_lines.append(f"     Notes: {notes}")

    report_lines.append("")
    report_lines.append("─" * 70)
    report_lines.append("DEPARTMENT SUMMARY")
    report_lines.append("─" * 70)

    for d in DEPARTMENTS:
        stats = dept_stats.get(d["id"], {"count": 0, "total_pop": 0})
        report_lines.append(
            f"  {d['name']:25s} | {stats['count']:>3d} municipios | "
            f"Pop: {stats['total_pop']:>10,} | Area: {d['area_km2']:>8,.1f} km²"
        )

    report_lines.append("")
    report_lines.append("─" * 70)
    report_lines.append("NEXT STEPS FOR FIELD RESEARCH")
    report_lines.append("─" * 70)
    report_lines.append("""
  1. HIGH-VALUE SCRAPING FIRST: Run scrapers on San Salvador metro,
     beach corridor, and Ruta de las Flores. This gives us quickest ROI.

  2. MUNICIPAL OFFICE PARTNERSHIPS: Contact alcaldías in Cabañas,
     northern Morazán, and Chalatenango for cadastral records,
     property tax data, and local market info.

  3. DRONE PHOTOGRAPHY CAMPAIGN: Focus on data deserts — northern
     Morazán (Perquín area), northern Chalatenango (La Palma area),
     and Cabañas interior. Budget: ~$50/municipio for local operators.

  4. COMMUNITY RESEARCHER NETWORK: Hire 3-5 local researchers
     ($300-500/month) to collect property prices, take photos,
     and document infrastructure in remote municipios.

  5. SATELLITE IMAGERY: Use Sentinel-2 or Planet Labs for development
     detection in areas with zero street-level imagery. Free tier
     available for educational/NGO use.

  6. PARTNER WITH UNIVERSITIES: UES, UCA, and UTEC have sociology/
     geography departments that could assist with field data collection
     as part of student research projects.
""")

    return "\n".join(report_lines)


if __name__ == "__main__":
    import sys
    import os

    # Write seed SQL
    sql = generate_seed_sql()
    sql_path = os.path.join(os.path.dirname(__file__), "001_admin_divisions.sql")
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write(sql)
    print(f"✅ Wrote seed SQL to {sql_path}")
    print(f"   → {len(DEPARTMENTS)} departments")
    print(f"   → {len(MUNICIPIOS)} municipios")
    print(f"   → {len(MUNICIPIOS) * len(COVERAGE_CATEGORIES)} coverage gap records")

    # Write coverage report
    report = generate_coverage_report()
    report_path = os.path.join(os.path.dirname(__file__), "coverage_gap_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ Wrote coverage gap report to {report_path}")

    # Also print the report
    print("\n" + report)
