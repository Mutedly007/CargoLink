"""
Règles de gestion du module Livraisons (Module Eya).
Contraintes « dures » partagées par la validation du modèle, le service de transitions
et le moteur d'affectation intelligente. Chaque fonction retourne un dict {champ: message}.
"""
from datetime import date

STATUTS_ACTIFS = ('PLANIFIEE', 'EN_CHARGEMENT', 'EN_TRANSIT', 'ARRIVEE')

ETATS_CAMION_BLOQUANTS = ('EN_MAINTENANCE', 'HORS_SERVICE')

# Catégories de permis autorisées par gabarit de camion (module Camions de Rahma)
PERMIS_PAR_TYPE_CAMION = {
    'FOURGON': ('B', 'C1', 'C', 'CE', 'D', 'ADR', 'C_CE_ADR'),
    'PORTEUR': ('C', 'CE', 'ADR', 'C_CE_ADR'),
    'FRIGORIFIQUE': ('C', 'CE', 'ADR', 'C_CE_ADR'),
    'CITERNE': ('C', 'CE', 'ADR', 'C_CE_ADR'),
    'PLATEAU': ('C', 'CE', 'ADR', 'C_CE_ADR'),
    'SEMI_REMORQUE': ('CE', 'C_CE_ADR'),
}

PERMIS_ADR = ('ADR', 'C_CE_ADR')


def verifier_camion(camion, poids_kg=None, nb_palettes=None, type_marchandise='STANDARD'):
    """R1, R2, R3, R6 : capacité, état et compatibilité marchandise du camion."""
    erreurs = {}
    if camion is None:
        return erreurs

    if camion.etat in ETATS_CAMION_BLOQUANTS:
        erreurs['camion'] = (
            f"Le camion {camion.immatriculation} est indisponible ({camion.get_etat_display()})."
        )
    elif poids_kg and camion.capacite_tonnage is not None:
        charge_max = int(camion.capacite_tonnage * 1000)
        if poids_kg > charge_max:
            erreurs['poids_kg'] = (
                f"Charge utile dépassée : {poids_kg:,} kg pour un camion de {charge_max:,} kg "
                f"({camion.immatriculation})."
            ).replace(',', ' ')

    if nb_palettes and camion.capacite_palettes and nb_palettes > camion.capacite_palettes:
        erreurs['nb_palettes'] = (
            f"Capacité palettes dépassée : {nb_palettes} palettes pour {camion.capacite_palettes} "
            f"places ({camion.immatriculation})."
        )

    if type_marchandise == 'FRIGORIFIQUE' and camion.type_camion != 'FRIGORIFIQUE':
        erreurs['camion'] = (
            f"Marchandise sous température dirigée : le camion {camion.immatriculation} "
            f"({camion.get_type_camion_display()}) n'est pas frigorifique."
        )
    return erreurs


def verifier_chauffeur(chauffeur, camion=None, type_marchandise='STANDARD', date_fin=None):
    """R4, R5 : aptitude du chauffeur (permis valide, catégorie, habilitation ADR, statut)."""
    erreurs = {}
    if chauffeur is None:
        return erreurs

    if chauffeur.statut == 'INACTIF':
        erreurs['chauffeur'] = f"{chauffeur.nom_complet} est inactif / suspendu."
    elif chauffeur.est_permis_expire:
        erreurs['chauffeur'] = (
            f"Le permis de {chauffeur.nom_complet} a expiré le "
            f"{chauffeur.date_expiration_permis.strftime('%d/%m/%Y')}."
        )
    elif date_fin and chauffeur.date_expiration_permis and chauffeur.date_expiration_permis < _as_date(date_fin):
        erreurs['chauffeur'] = (
            f"Le permis de {chauffeur.nom_complet} expire le "
            f"{chauffeur.date_expiration_permis.strftime('%d/%m/%Y')}, avant la fin de la livraison."
        )
    elif camion is not None:
        autorises = PERMIS_PAR_TYPE_CAMION.get(camion.type_camion)
        if autorises and chauffeur.categorie_permis not in autorises:
            erreurs['chauffeur'] = (
                f"Permis {chauffeur.get_categorie_permis_display()} insuffisant pour conduire un "
                f"{camion.get_type_camion_display()}."
            )

    if 'chauffeur' not in erreurs and type_marchandise == 'ADR' and chauffeur.categorie_permis not in PERMIS_ADR:
        erreurs['chauffeur'] = (
            f"Matières dangereuses : {chauffeur.nom_complet} ne possède pas l'habilitation ADR."
        )
    return erreurs


def conflits_planning(debut, fin, camion=None, chauffeur=None, exclure_pk=None):
    """R7 : aucune autre livraison active ne doit mobiliser le même camion / chauffeur sur la période."""
    from .models import Livraison

    erreurs = {}
    if not debut or not fin:
        return erreurs

    actives = Livraison.objects.filter(
        statut__in=STATUTS_ACTIFS,
        date_depart_prevue__lt=fin,
        date_livraison_prevue__gt=debut,
    )
    if exclure_pk:
        actives = actives.exclude(pk=exclure_pk)

    if camion is not None:
        conflit = actives.filter(camion=camion).first()
        if conflit:
            erreurs['camion'] = (
                f"Le camion {camion.immatriculation} est déjà engagé sur la livraison {conflit.reference} "
                f"({conflit.date_depart_prevue:%d/%m %H:%M} → {conflit.date_livraison_prevue:%d/%m %H:%M})."
            )
    if chauffeur is not None:
        conflit = actives.filter(chauffeur=chauffeur).first()
        if conflit:
            erreurs['chauffeur'] = (
                f"{chauffeur.nom_complet} est déjà affecté à la livraison {conflit.reference} sur cette période."
            )
    return erreurs


def _as_date(valeur):
    return valeur.date() if hasattr(valeur, 'date') else valeur


def permis_expire_bientot(chauffeur, jours=30):
    if not chauffeur or not chauffeur.date_expiration_permis:
        return False
    return 0 <= (chauffeur.date_expiration_permis - date.today()).days <= jours
