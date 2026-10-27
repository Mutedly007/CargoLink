"""
Recherche avancée multi-critères du module Livraisons (Module Eya).
Les mêmes filtres servent au formulaire de recherche, à l'export CSV et à la recherche
en langage naturel (dont la sortie IA est convertie en ces filtres validés).
"""
from datetime import date

from django.db.models import Count, Q

TRIS = {
    'recent': ('-date_depart_prevue', "Départ le plus récent"),
    'echeance': ('date_livraison_prevue', "Échéance la plus proche"),
    'priorite': ('priorite_ordre', "Priorité (urgentes d'abord)"),
    'reference': ('reference', "Référence"),
    'creation': ('-date_creation', "Dernières créées"),
}


def _date(valeur):
    try:
        return date.fromisoformat(valeur) if valeur else None
    except (TypeError, ValueError):
        return None


def lire_filtres(params):
    """Extrait les filtres d'un QueryDict (GET) dans un dict normalisé."""
    return {
        'q': params.get('q', '').strip(),
        'statut': [s for s in params.getlist('statut') if s],
        'entrepot': params.get('entrepot', '').strip(),
        'ville': params.get('ville', '').strip(),
        'type_livraison': params.get('type_livraison', '').strip(),
        'priorite': params.get('priorite', '').strip(),
        'type_marchandise': params.get('type_marchandise', '').strip(),
        'chauffeur': params.get('chauffeur', '').strip(),
        'camion': params.get('camion', '').strip(),
        'date_du': params.get('date_du', '').strip(),
        'date_au': params.get('date_au', '').strip(),
        'en_retard': params.get('en_retard') in ('1', 'on', 'true', 'True'),
        'avec_incident': params.get('avec_incident') in ('1', 'on', 'true', 'True'),
        'tri': params.get('tri', 'recent') if params.get('tri') in TRIS else 'recent',
    }


def appliquer_filtres(queryset, filtres):
    qs = queryset
    q = filtres.get('q')
    if q:
        qs = qs.filter(
            Q(reference__icontains=q) | Q(code_suivi__iexact=q) | Q(numero_bl__icontains=q)
            | Q(destinataire_nom__icontains=q) | Q(description_marchandise__icontains=q)
            | Q(camion__immatriculation__icontains=q)
            | Q(chauffeur__nom__icontains=q) | Q(chauffeur__prenom__icontains=q)
            | Q(entrepot_origine__nom__icontains=q) | Q(entrepot_destination__nom__icontains=q)
        )
    if filtres.get('statut'):
        qs = qs.filter(statut__in=filtres['statut'])
    if filtres.get('entrepot'):
        qs = qs.filter(Q(entrepot_origine_id=filtres['entrepot']) | Q(entrepot_destination_id=filtres['entrepot']))
    if filtres.get('ville'):
        ville = filtres['ville']
        qs = qs.filter(
            Q(entrepot_origine__ville__icontains=ville) | Q(entrepot_destination__ville__icontains=ville)
            | Q(ville_livraison__icontains=ville)
        )
    for champ in ('type_livraison', 'priorite', 'type_marchandise'):
        if filtres.get(champ):
            qs = qs.filter(**{champ: filtres[champ]})
    if filtres.get('chauffeur'):
        qs = qs.filter(chauffeur_id=filtres['chauffeur'])
    if filtres.get('camion'):
        qs = qs.filter(camion_id=filtres['camion'])
    du, au = _date(filtres.get('date_du')), _date(filtres.get('date_au'))
    if du:
        qs = qs.filter(date_depart_prevue__date__gte=du)
    if au:
        qs = qs.filter(date_depart_prevue__date__lte=au)
    if filtres.get('en_retard'):
        qs = qs.filter(est_en_retard=True)
    if filtres.get('avec_incident'):
        qs = qs.filter(incidents__resolu=False).distinct()

    tri = TRIS.get(filtres.get('tri') or 'recent', TRIS['recent'])[0]
    if tri == 'priorite_ordre':
        from django.db.models import Case, IntegerField, Value, When
        qs = qs.annotate(priorite_ordre=Case(
            When(priorite='URGENTE', then=Value(0)), When(priorite='NORMALE', then=Value(1)),
            default=Value(2), output_field=IntegerField(),
        )).order_by('priorite_ordre', 'date_livraison_prevue')
    else:
        qs = qs.order_by(tri)
    return qs


def filtres_vers_querystring(filtres):
    """Convertit des filtres (ex. issus de l'IA) en paramètres d'URL pour la liste."""
    from django.http import QueryDict

    qd = QueryDict(mutable=True)
    for cle, valeur in filtres.items():
        if isinstance(valeur, list):
            qd.setlist(cle, valeur)
        elif valeur is True:
            qd[cle] = '1'
        elif valeur:
            qd[cle] = str(valeur)
    return qd.urlencode()


def compter_filtres_actifs(filtres):
    return sum(1 for cle, valeur in filtres.items() if cle != 'tri' and valeur)


def statistiques(queryset):
    """Indicateurs KPI calculés sur le périmètre visible de l'utilisateur."""
    from django.utils import timezone

    aujourd_hui = timezone.localdate()
    livrees = queryset.filter(statut='LIVREE', date_livraison_reelle__isnull=False)
    nb_livrees = livrees.count()
    a_l_heure = sum(1 for reelle, prevue in livrees.values_list('date_livraison_reelle', 'date_livraison_prevue')
                    if reelle <= prevue)
    return {
        'du_jour': queryset.filter(date_depart_prevue__date=aujourd_hui).exclude(statut='ANNULEE').count(),
        'en_cours': queryset.filter(statut__in=('EN_CHARGEMENT', 'EN_TRANSIT', 'ARRIVEE')).count(),
        'a_planifier': queryset.filter(statut='BROUILLON').count(),
        'en_retard': queryset.filter(est_en_retard=True).exclude(statut__in=('LIVREE', 'ANNULEE', 'ECHEC')).count(),
        'taux_a_l_heure': round(100 * a_l_heure / nb_livrees) if nb_livrees else None,
        'incidents_ouverts': queryset.filter(incidents__resolu=False).aggregate(n=Count('incidents'))['n'] or 0,
        'total': queryset.count(),
    }
