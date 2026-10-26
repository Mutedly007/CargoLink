"""
Contrôle d'accès du module Livraisons (Module Eya).
Périmètre de données et actions autorisées selon le rôle CargoLink (accounts.UserProfile.role).
"""
from functools import wraps

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect

ROLES_CARGOLINK = ('ENTREPOT', 'ENTERPOT', 'TRANSPORTEUR', 'PLANIFICATEUR', 'ADMIN')

# Statuts dans lesquels chaque action est possible
ACTIONS_PAR_STATUT = {
    'modifier': ('BROUILLON', 'PLANIFIEE'),
    'planifier': ('BROUILLON',),
    'charger': ('PLANIFIEE',),
    'partir': ('EN_CHARGEMENT',),
    'arriver': ('EN_TRANSIT',),
    'livrer': ('ARRIVEE',),
    'echouer': ('EN_TRANSIT', 'ARRIVEE'),
    'annuler': ('BROUILLON', 'PLANIFIEE', 'EN_CHARGEMENT'),
    'reaffecter': ('PLANIFIEE', 'EN_CHARGEMENT', 'EN_TRANSIT'),
    'incident': ('PLANIFIEE', 'EN_CHARGEMENT', 'EN_TRANSIT', 'ARRIVEE'),
}


def role_de(user):
    return getattr(getattr(user, 'profile', None), 'role', None)


def est_planificateur(user):
    """Planificateur, Administrateur CargoLink ou superutilisateur : accès complet aux livraisons."""
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.is_staff or role_de(user) in ('PLANIFICATEUR', 'ADMIN')


def est_transporteur(user):
    return user.is_authenticated and role_de(user) == 'TRANSPORTEUR'


def est_gestionnaire_entrepot(user):
    return user.is_authenticated and role_de(user) in ('ENTREPOT', 'ENTERPOT')


def livraisons_session_required(view_func):
    """
    Contrôle d'accès au module Livraisons : tous les rôles CargoLink connectés,
    chacun limité ensuite à son périmètre (voir livraisons_visibles).
    Même comportement que creneaux_session_required / chauffeur_session_required.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(
                request,
                "Accès restreint : Veuillez vous connecter pour accéder au module des livraisons."
            )
            return redirect('landing')
        if not (est_planificateur(request.user) or role_de(request.user) in ROLES_CARGOLINK):
            messages.error(request, "Accès refusé : votre profil ne dispose d'aucun rôle logistique CargoLink.")
            return redirect('landing')
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def livraisons_visibles(user, queryset=None):
    """
    Périmètre de données :
    - Planificateur / Admin : toutes les livraisons
    - Transporteur : livraisons de ses chauffeurs (Chauffeur.transporteur_user) ou de ses camions (Camion.transporteur)
    - Gestionnaire d'entrepôt : livraisons au départ ou à destination de ses entrepôts (Entrepot.gestionnaire)
    """
    from .models import Livraison

    qs = queryset if queryset is not None else Livraison.objects.all()
    if est_planificateur(user):
        return qs
    if est_transporteur(user):
        return qs.filter(Q(chauffeur__transporteur_user=user) | Q(camion__transporteur=user)).distinct()
    if est_gestionnaire_entrepot(user):
        return qs.filter(
            Q(entrepot_origine__gestionnaire=user) | Q(entrepot_destination__gestionnaire=user)
        ).distinct()
    return qs.none()


def est_transporteur_de(user, livraison):
    if not est_transporteur(user):
        return False
    return bool(
        (livraison.chauffeur_id and livraison.chauffeur.transporteur_user_id == user.id)
        or (livraison.camion_id and livraison.camion.transporteur_id == user.id)
    )


def gere_destination(user, livraison):
    return bool(
        est_gestionnaire_entrepot(user)
        and livraison.entrepot_destination_id
        and livraison.entrepot_destination.gestionnaire_id == user.id
    )


def gere_un_entrepot_de(user, livraison):
    if not est_gestionnaire_entrepot(user):
        return False
    return livraison.entrepot_origine.gestionnaire_id == user.id or gere_destination(user, livraison)


def peut_executer(user, livraison, action):
    """Vérifie qu'un utilisateur peut réaliser une action sur une livraison dans son état actuel."""
    if livraison.statut not in ACTIONS_PAR_STATUT.get(action, ()):
        return False
    if est_planificateur(user):
        return True
    if action in ('charger', 'partir'):
        return est_transporteur_de(user, livraison)
    if action in ('arriver', 'livrer', 'echouer'):
        return est_transporteur_de(user, livraison) or gere_destination(user, livraison)
    if action == 'incident':
        return est_transporteur_de(user, livraison) or gere_un_entrepot_de(user, livraison)
    # modifier, planifier, annuler, reaffecter : réservés aux planificateurs
    return False


def actions_autorisees(user, livraison):
    return {action for action in ACTIONS_PAR_STATUT if peut_executer(user, livraison, action)}
