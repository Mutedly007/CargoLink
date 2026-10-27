"""
Estimations géographiques du module Livraisons (Module Eya).
Distances routières approximatives entre les villes tunisiennes, durée de trajet (ETA)
et empreinte carbone estimée (ODD 12 / 13). Aucune API externe : calcul local.
"""
import math
import unicodedata
from datetime import timedelta

# Coordonnées (latitude, longitude) des principales villes logistiques tunisiennes
VILLES = {
    'tunis': (36.8065, 10.1815),
    'rades': (36.7681, 10.2753),
    'ben arous': (36.7531, 10.2189),
    'ariana': (36.8665, 10.1647),
    'la marsa': (36.8782, 10.3247),
    'manouba': (36.8101, 10.0863),
    'bizerte': (37.2744, 9.8739),
    'nabeul': (36.4561, 10.7376),
    'hammamet': (36.4000, 10.6167),
    'zaghouan': (36.4029, 10.1429),
    'sousse': (35.8256, 10.6084),
    'monastir': (35.7643, 10.8113),
    'mahdia': (35.5047, 11.0622),
    'sfax': (34.7406, 10.7603),
    'gabes': (33.8815, 10.0982),
    'medenine': (33.3549, 10.5055),
    'zarzis': (33.5036, 11.1122),
    'tataouine': (32.9297, 10.4518),
    'kairouan': (35.6781, 10.0963),
    'kasserine': (35.1676, 8.8365),
    'sidi bouzid': (35.0382, 9.4849),
    'gafsa': (34.4250, 8.7842),
    'tozeur': (33.9197, 8.1335),
    'kebili': (33.7044, 8.9690),
    'beja': (36.7256, 9.1817),
    'jendouba': (36.5011, 8.7802),
    'le kef': (36.1742, 8.7049),
    'kef': (36.1742, 8.7049),
    'siliana': (36.0849, 9.3708),
}

# Facteur de correction distance à vol d'oiseau -> distance routière
FACTEUR_ROUTE = 1.25

# Vitesse moyenne réaliste par gabarit (km/h, pauses et trafic inclus)
VITESSE_PAR_TYPE = {
    'SEMI_REMORQUE': 62,
    'PORTEUR': 68,
    'FOURGON': 78,
    'FRIGORIFIQUE': 62,
    'CITERNE': 58,
    'PLATEAU': 58,
}

# Émissions moyennes (kg CO2 / km) d'un poids lourd selon sa norme
CO2_PAR_NORME = {
    'EURO_4': 1.05,
    'EURO_5': 0.98,
    'EURO_6': 0.90,
    'HYBRIDE': 0.65,
    'ELECTRIQUE': 0.10,
}

# Coefficient de gabarit appliqué aux émissions (un fourgon consomme ~3x moins)
COEF_CO2_TYPE = {
    'FOURGON': 0.35,
    'PORTEUR': 0.75,
}

# Temps forfaitaire de manœuvre / formalités au départ et à l'arrivée
MARGE_OPERATIONNELLE = timedelta(minutes=30)


def normaliser_ville(nom):
    """Minuscules, sans accents ni tirets : 'Radès' -> 'rades'."""
    if not nom:
        return ''
    texte = unicodedata.normalize('NFKD', nom).encode('ascii', 'ignore').decode('ascii')
    return texte.lower().replace('-', ' ').strip()


def coordonnees(nom_ville):
    """Retourne (lat, lon) d'une ville connue, ou None. Accepte 'Sfax Sud', 'Tunis Aéroport'..."""
    nom = normaliser_ville(nom_ville)
    if nom in VILLES:
        return VILLES[nom]
    for ville, coords in VILLES.items():
        if ville in nom:
            return coords
    return None


def distance_km(ville_a, ville_b):
    """Distance routière estimée en km entre deux villes, ou None si une ville est inconnue."""
    a, b = coordonnees(ville_a), coordonnees(ville_b)
    if not a or not b:
        return None
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    vol_oiseau = 6371 * 2 * math.asin(math.sqrt(h))
    # Livraison intra-ville : forfait minimal de 8 km
    return max(8, round(vol_oiseau * FACTEUR_ROUTE))


def duree_trajet(distance, type_camion='SEMI_REMORQUE'):
    """Durée de trajet estimée (timedelta) pour une distance et un gabarit donnés."""
    if distance is None:
        return None
    vitesse = VITESSE_PAR_TYPE.get(type_camion, 62)
    return timedelta(hours=distance / vitesse) + MARGE_OPERATIONNELLE


def co2_kg(distance, norme='EURO_6', type_camion='SEMI_REMORQUE'):
    """Empreinte carbone estimée (kg CO2) du trajet aller."""
    if distance is None:
        return None
    facteur = CO2_PAR_NORME.get(norme, 0.95) * COEF_CO2_TYPE.get(type_camion, 1.0)
    return round(distance * facteur, 1)
