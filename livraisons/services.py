"""
Service de transitions du module Livraisons (Module Eya).
Chaque action fait avancer la livraison ET synchronise les modules de l'équipe :
- Créneaux (Kacem) : appel des méthodes existantes confirmer / marquer_arrive / mettre_a_quai / terminer / annuler
  (qui occupent et libèrent les quais d'Aziz)
- Camions (Rahma) : état du camion + ligne HistoriquePassage
- Chauffeurs (Khalil) : statut du chauffeur + ligne VisiteChauffeur
Toutes les actions sont atomiques : en cas d'erreur, rien n'est enregistré à moitié.
"""
import base64
import binascii
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from .models import IncidentLivraison, SuiviLivraison


class TransitionImpossible(Exception):
    """Levée quand une action n'est pas réalisable dans l'état actuel de la livraison."""


# Correspondance gabarit Camion (Rahma) -> gabarit Créneau (Kacem)
TYPE_CAMION_VERS_CRENEAU = {
    'SEMI_REMORQUE': 'SEMI_REMORQUE',
    'PORTEUR': 'PORTEUR',
    'FOURGON': 'FOURGON',
}


def _message_validation(exc):
    if hasattr(exc, 'message_dict'):
        return " ".join(msg for msgs in exc.message_dict.values() for msg in msgs)
    return " ".join(exc.messages)


def _journaliser(livraison, user, commentaire, localisation='', visible_public=True):
    SuiviLivraison.objects.create(
        livraison=livraison,
        statut=livraison.statut,
        auteur=user if (user and user.is_authenticated) else None,
        commentaire=commentaire[:255],
        localisation=localisation[:120],
        visible_public=visible_public,
    )


def _changer_etat_camion(camion, etat):
    """Mise à jour ciblée de l'état du camion (sans redéclencher les validations du formulaire Camion)."""
    if camion is None:
        return
    type(camion).objects.filter(pk=camion.pk).update(etat=etat, date_modification=timezone.now())
    camion.etat = etat


def _changer_statut_chauffeur(chauffeur, statut):
    if chauffeur is None:
        return
    chauffeur.statut = statut
    chauffeur.save(update_fields=['statut', 'date_modification'])


def _date_etape(livraison, statut):
    suivi = livraison.suivis.filter(statut=statut).order_by('date').first()
    return suivi.date if suivi else None


def synchroniser_creneau(livraison, creneau):
    """
    Recopie dans le créneau (module Kacem) les vraies données camion / chauffeur de la livraison.
    Les écrans de Kacem et le portail mobile de Khalil (recherche par nom / immatriculation)
    affichent ainsi des informations justes, sans modifier leur code.
    """
    if creneau is None:
        return
    champs = []
    if livraison.camion_id:
        creneau.immatriculation_camion = livraison.camion.immatriculation
        creneau.type_camion = TYPE_CAMION_VERS_CRENEAU.get(livraison.camion.type_camion, 'AUTRE')
        champs += ['immatriculation_camion', 'type_camion']
        if livraison.camion.societe_transport:
            creneau.transporteur_nom = livraison.camion.societe_transport
            champs.append('transporteur_nom')
    if livraison.chauffeur_id:
        creneau.chauffeur_nom = livraison.chauffeur.nom_complet
        creneau.chauffeur_telephone = livraison.chauffeur.telephone
        champs += ['chauffeur_nom', 'chauffeur_telephone']
        if not livraison.camion_id or not livraison.camion.societe_transport:
            creneau.transporteur_nom = livraison.chauffeur.entreprise_transport
            champs.append('transporteur_nom')
    if livraison.numero_bl and not creneau.numero_bl:
        creneau.numero_bl = livraison.numero_bl
        champs.append('numero_bl')
    creneau.nb_palettes = livraison.nb_palettes
    champs.append('nb_palettes')
    if livraison.poids_kg:
        creneau.poids_kg = livraison.poids_kg
        champs.append('poids_kg')
    creneau.save(update_fields=list(dict.fromkeys(champs + ['date_modification'])))


def _verifier_creneau_coherent(creneau, entrepot):
    """
    Garde-fou inter-modules : un autre module (ex. affectation de mission des Chauffeurs) peut avoir
    déplacé ou clôturé le créneau lié. On refuse alors l'action plutôt que d'occuper le mauvais quai.
    """
    if creneau is None:
        return
    creneau.refresh_from_db()
    if creneau.entrepot_id != entrepot.id:
        raise TransitionImpossible(
            f"Le créneau {creneau.reference} a été déplacé vers un autre entrepôt ({creneau.entrepot.nom}). "
            f"Réservez un nouveau créneau pour cette livraison."
        )
    if creneau.statut == 'ANNULE':
        raise TransitionImpossible(f"Le créneau {creneau.reference} a été annulé dans le module Créneaux.")


def _creneau_arrivee_et_mise_a_quai(creneau, user):
    """Fait passer un créneau jusqu'à EN_COURS via les méthodes du module Créneaux."""
    if creneau is None or creneau.statut in ('EN_COURS', 'TERMINE', 'ANNULE'):
        return
    if creneau.statut in ('EN_ATTENTE', 'CONFIRME', 'EN_RETARD'):
        creneau.marquer_arrive(user=user)
    creneau.mettre_a_quai(user=user)


def _creneau_terminer(creneau, user):
    if creneau is None or creneau.statut in ('TERMINE', 'ANNULE'):
        return
    if creneau.statut != 'EN_COURS':
        _creneau_arrivee_et_mise_a_quai(creneau, user)
    creneau.terminer(user=user)


def _creneau_annuler(creneau, motif, user):
    if creneau is None or creneau.statut in ('TERMINE', 'ANNULE'):
        return
    creneau.annuler(motif=motif, user=user)


def _enregistrer_passage(livraison, entrepot, creneau, type_operation, entree, sortie):
    """Alimente automatiquement les historiques de Rahma (HistoriquePassage) et de Khalil (VisiteChauffeur)."""
    from camions.models import HistoriquePassage
    from chauffeurs.models import VisiteChauffeur

    quai = creneau.quai if creneau else None
    note = f"Livraison {livraison.reference} ({livraison.get_type_livraison_display()})"
    if entrepot is None:
        note += f" • Client : {livraison.destinataire_nom}, {livraison.ville_livraison}"

    if livraison.camion_id:
        HistoriquePassage.objects.create(
            camion=livraison.camion,
            entrepot=entrepot,
            quai=quai,
            creneau=creneau,
            date_entree=entree,
            date_sortie=sortie,
            type_operation=type_operation,
            statut='TERMINE',
            poids_mesure_kg=livraison.poids_kg,
            numero_bon_livraison=livraison.numero_bl,
            observations=note,
        )
    if livraison.chauffeur_id:
        entree_locale, sortie_locale = timezone.localtime(entree), timezone.localtime(sortie)
        VisiteChauffeur.objects.create(
            chauffeur=livraison.chauffeur,
            entrepot=entrepot,
            creneau=creneau,
            quai_numero=quai.numero if quai else ("Client" if entrepot is None else "Quai Standard"),
            numero_bl=livraison.numero_bl,
            type_operation=type_operation,
            statut='TERMINE',
            date_visite=entree_locale.date(),
            heure_arrivee=entree_locale.time(),
            heure_depart=sortie_locale.time(),
            duree_minutes=max(1, int((sortie - entree).total_seconds() // 60)),
            emargement_valide=True,
            notes=note,
        )


def _verifier_etat(livraison, attendus, action):
    if livraison.statut not in attendus:
        raise TransitionImpossible(
            f"Action « {action} » impossible : la livraison est actuellement « {livraison.get_statut_display()} »."
        )


# ==============================================================================
# TRANSITIONS
# ==============================================================================

@transaction.atomic
def planifier(livraison, user):
    """BROUILLON -> PLANIFIEE : validation complète, confirmation des créneaux liés."""
    _verifier_etat(livraison, ('BROUILLON',), "planifier")
    if not livraison.camion_id or not livraison.chauffeur_id:
        raise TransitionImpossible("Affectez un camion et un chauffeur avant de planifier la livraison.")

    livraison.statut = 'PLANIFIEE'
    try:
        livraison.full_clean()
    except ValidationError as exc:
        livraison.statut = 'BROUILLON'
        raise TransitionImpossible(_message_validation(exc))
    livraison.save()

    for creneau in (livraison.creneau_chargement, livraison.creneau_dechargement):
        if creneau is not None:
            if creneau.statut == 'EN_ATTENTE':
                creneau.confirmer(user=user)
            synchroniser_creneau(livraison, creneau)

    _journaliser(
        livraison, user,
        f"Livraison planifiée : camion {livraison.camion.immatriculation}, chauffeur {livraison.chauffeur.nom_complet}."
    )
    return livraison


@transaction.atomic
def charger(livraison, user):
    """PLANIFIEE -> EN_CHARGEMENT : arrivée au quai de départ, quai occupé."""
    _verifier_etat(livraison, ('PLANIFIEE',), "démarrer le chargement")
    _verifier_creneau_coherent(livraison.creneau_chargement, livraison.entrepot_origine)
    _creneau_arrivee_et_mise_a_quai(livraison.creneau_chargement, user)
    _changer_etat_camion(livraison.camion, 'A_QUAI')
    _changer_statut_chauffeur(livraison.chauffeur, 'A_QUAI')

    livraison.statut = 'EN_CHARGEMENT'
    livraison.save(update_fields=['statut', 'date_modification'])
    quai = livraison.creneau_chargement.quai.numero if livraison.creneau_chargement_id else "quai de départ"
    _journaliser(livraison, user, f"Camion à quai ({quai}). Chargement en cours.", livraison.ville_depart)
    return livraison


@transaction.atomic
def partir(livraison, user):
    """EN_CHARGEMENT -> EN_TRANSIT : quai libéré, camion sur la route, historiques alimentés."""
    _verifier_etat(livraison, ('EN_CHARGEMENT',), "valider le départ")
    maintenant = timezone.now()
    creneau = livraison.creneau_chargement
    _creneau_terminer(creneau, user)
    _changer_etat_camion(livraison.camion, 'EN_TRANSIT')
    _changer_statut_chauffeur(livraison.chauffeur, 'EN_MISSION')

    entree = (creneau.heure_arrivee_reelle if creneau and creneau.heure_arrivee_reelle else None) \
        or _date_etape(livraison, 'EN_CHARGEMENT') or maintenant
    _enregistrer_passage(livraison, livraison.entrepot_origine, creneau, 'CHARGEMENT', entree, maintenant)

    livraison.statut = 'EN_TRANSIT'
    livraison.date_depart_reelle = maintenant
    livraison.save(update_fields=['statut', 'date_depart_reelle', 'date_modification'])
    eta = timezone.localtime(livraison.eta)
    _journaliser(
        livraison, user, f"Départ du site. Arrivée estimée à {eta:%H:%M} le {eta:%d/%m}.", livraison.ville_depart
    )
    return livraison


@transaction.atomic
def arriver(livraison, user, localisation=''):
    """EN_TRANSIT -> ARRIVEE : arrivée à destination (mise à quai si transfert inter-entrepôts)."""
    _verifier_etat(livraison, ('EN_TRANSIT',), "déclarer l'arrivée")
    if livraison.type_livraison == 'INTER_ENTREPOT':
        _verifier_creneau_coherent(livraison.creneau_dechargement, livraison.entrepot_destination)
        _creneau_arrivee_et_mise_a_quai(livraison.creneau_dechargement, user)
        _changer_etat_camion(livraison.camion, 'A_QUAI')
        _changer_statut_chauffeur(livraison.chauffeur, 'A_QUAI')

    livraison.statut = 'ARRIVEE'
    livraison.date_arrivee_reelle = timezone.now()
    livraison.save(update_fields=['statut', 'date_arrivee_reelle', 'date_modification'])
    _journaliser(livraison, user, "Arrivée à destination.", localisation or livraison.ville_arrivee)
    return livraison


def _image_depuis_data_url(data_url, nom):
    """Convertit la signature dessinée (canvas -> data:image/png;base64,...) en fichier image."""
    if not data_url or not data_url.startswith('data:image/png;base64,'):
        return None
    try:
        contenu = base64.b64decode(data_url.split(',', 1)[1], validate=True)
    except (binascii.Error, ValueError):
        return None
    if not contenu.startswith(b'\x89PNG') or len(contenu) > 2 * 1024 * 1024:
        return None
    return ContentFile(contenu, name=nom)


@transaction.atomic
def livrer(livraison, user, receptionnaire_nom, signature_data_url='', photo=None,
           reserves='', conforme=True, note_satisfaction=None):
    """ARRIVEE -> LIVREE : preuve de livraison obligatoire (R11), libération des ressources."""
    _verifier_etat(livraison, ('ARRIVEE',), "valider la livraison")
    signature = _image_depuis_data_url(signature_data_url, f"signature_{livraison.reference}.png")
    if not receptionnaire_nom.strip():
        raise TransitionImpossible("Le nom du réceptionnaire est obligatoire pour valider la livraison.")
    if signature is None and not photo:
        raise TransitionImpossible("Une signature ou une photo de preuve est obligatoire pour valider la livraison.")

    maintenant = timezone.now()
    creneau = livraison.creneau_dechargement if livraison.type_livraison == 'INTER_ENTREPOT' else None
    _creneau_terminer(creneau, user)
    _changer_etat_camion(livraison.camion, 'DISPONIBLE')
    _changer_statut_chauffeur(livraison.chauffeur, 'DISPONIBLE')

    entree = livraison.date_arrivee_reelle or maintenant
    entrepot = livraison.entrepot_destination if livraison.type_livraison == 'INTER_ENTREPOT' else None
    _enregistrer_passage(livraison, entrepot, creneau, 'DECHARGEMENT', entree, maintenant)

    livraison.receptionnaire_nom = receptionnaire_nom.strip()
    if signature is not None:
        livraison.signature.save(signature.name, signature, save=False)
    if photo:
        livraison.photo_preuve = photo
    livraison.reserves = reserves
    livraison.livraison_conforme = conforme
    livraison.note_satisfaction = note_satisfaction
    livraison.date_livraison_reelle = maintenant
    livraison.est_en_retard = maintenant > livraison.date_livraison_prevue
    livraison.statut = 'LIVREE'
    livraison.save()

    if not conforme:
        IncidentLivraison.objects.create(
            livraison=livraison, type_incident='DOMMAGE', gravite='MOYENNE',
            description=reserves or "Livraison déclarée non conforme à la réception.",
            declare_par=user if user.is_authenticated else None,
        )
    retard = f" avec {livraison.retard_minutes} min de retard" if livraison.est_en_retard else " dans les délais"
    _journaliser(livraison, user, f"Livraison réceptionnée par {livraison.receptionnaire_nom}{retard}.",
                 livraison.ville_arrivee)
    return livraison


@transaction.atomic
def echouer(livraison, user, motif, type_incident='REFUS_CLIENT'):
    """EN_TRANSIT / ARRIVEE -> ECHEC : motif obligatoire, incident créé, ressources libérées."""
    _verifier_etat(livraison, ('EN_TRANSIT', 'ARRIVEE'), "déclarer l'échec")
    if not motif.strip():
        raise TransitionImpossible("Le motif de l'échec est obligatoire.")

    creneau = livraison.creneau_dechargement
    if creneau is not None and creneau.statut == 'EN_COURS':
        _creneau_terminer(creneau, user)
    else:
        _creneau_annuler(creneau, f"Échec de la livraison {livraison.reference} : {motif}", user)
    _changer_etat_camion(livraison.camion, 'DISPONIBLE')
    _changer_statut_chauffeur(livraison.chauffeur, 'DISPONIBLE')

    IncidentLivraison.objects.create(
        livraison=livraison, type_incident=type_incident, gravite='CRITIQUE', description=motif,
        declare_par=user if user.is_authenticated else None,
    )
    livraison.statut = 'ECHEC'
    livraison.motif_echec = motif
    livraison.save(update_fields=['statut', 'motif_echec', 'date_modification'])
    _journaliser(livraison, user, "Livraison en échec. Le planificateur organise la suite (retour ou nouvelle tentative).")
    return livraison


@transaction.atomic
def annuler(livraison, user, motif):
    """BROUILLON / PLANIFIEE / EN_CHARGEMENT -> ANNULEE : créneaux annulés via le module Créneaux."""
    _verifier_etat(livraison, ('BROUILLON', 'PLANIFIEE', 'EN_CHARGEMENT'), "annuler")
    if not motif.strip():
        raise TransitionImpossible("Le motif d'annulation est obligatoire.")

    etait_a_quai = livraison.statut == 'EN_CHARGEMENT'
    for creneau in (livraison.creneau_chargement, livraison.creneau_dechargement):
        _creneau_annuler(creneau, f"Livraison {livraison.reference} annulée : {motif}", user)
    if etait_a_quai:
        _changer_etat_camion(livraison.camion, 'DISPONIBLE')
        _changer_statut_chauffeur(livraison.chauffeur, 'DISPONIBLE')

    livraison.statut = 'ANNULEE'
    livraison.motif_annulation = motif
    livraison.save(update_fields=['statut', 'motif_annulation', 'date_modification'])
    _journaliser(livraison, user, f"Livraison annulée. Motif : {motif}")
    return livraison


@transaction.atomic
def supprimer(livraison, user):
    """
    Suppression définitive d'une livraison en attente (BROUILLON / PLANIFIEE).
    Les créneaux liés sont d'abord annulés via le module Créneaux pour libérer les quais ;
    le suivi et les incidents sont supprimés avec la livraison (CASCADE).
    Retourne la référence supprimée.
    """
    _verifier_etat(livraison, ('BROUILLON', 'PLANIFIEE'), "supprimer")
    reference = livraison.reference
    for creneau in (livraison.creneau_chargement, livraison.creneau_dechargement):
        _creneau_annuler(creneau, f"Livraison {reference} supprimée.", user)
    livraison.delete()
    return reference


@transaction.atomic
def reaffecter(livraison, user, camion=None, chauffeur=None, ancien_camion_en_panne=False, commentaire=''):
    """
    Remplace le camion et/ou le chauffeur (après une panne par exemple).
    Les règles R1 à R7 sont revérifiées sur la nouvelle affectation.
    """
    _verifier_etat(livraison, ('PLANIFIEE', 'EN_CHARGEMENT', 'EN_TRANSIT'), "réaffecter")
    ancien_camion, ancien_chauffeur = livraison.camion, livraison.chauffeur
    if (camion is None or camion == ancien_camion) and (chauffeur is None or chauffeur == ancien_chauffeur):
        raise TransitionImpossible("Sélectionnez un camion ou un chauffeur différent de l'affectation actuelle.")

    if camion is not None:
        livraison.camion = camion
    if chauffeur is not None:
        livraison.chauffeur = chauffeur
    try:
        livraison.full_clean()
    except ValidationError as exc:
        raise TransitionImpossible(_message_validation(exc))

    en_cours = livraison.statut in ('EN_CHARGEMENT', 'EN_TRANSIT')
    etat_camion = {'EN_CHARGEMENT': 'A_QUAI', 'EN_TRANSIT': 'EN_TRANSIT'}.get(livraison.statut)
    statut_chauffeur = {'EN_CHARGEMENT': 'A_QUAI', 'EN_TRANSIT': 'EN_MISSION'}.get(livraison.statut)

    if livraison.camion != ancien_camion:
        if ancien_camion_en_panne:
            _changer_etat_camion(ancien_camion, 'EN_MAINTENANCE')
        elif en_cours:
            _changer_etat_camion(ancien_camion, 'DISPONIBLE')
        if en_cours:
            _changer_etat_camion(livraison.camion, etat_camion)
    if livraison.chauffeur != ancien_chauffeur:
        if en_cours:
            _changer_statut_chauffeur(ancien_chauffeur, 'DISPONIBLE')
            _changer_statut_chauffeur(livraison.chauffeur, statut_chauffeur)

    livraison.save()
    for creneau in (livraison.creneau_chargement, livraison.creneau_dechargement):
        if creneau is not None and creneau.statut not in ('TERMINE', 'ANNULE'):
            synchroniser_creneau(livraison, creneau)

    if ancien_camion_en_panne:
        livraison.incidents.filter(resolu=False, type_incident__in=['PANNE', 'ACCIDENT']).update(
            resolu=True, date_resolution=timezone.now(),
            resolution=f"Véhicule de remplacement affecté : {livraison.camion.immatriculation}."
        )
    _journaliser(
        livraison, user,
        f"Réaffectation : camion {livraison.camion.immatriculation}, chauffeur {livraison.chauffeur.nom_complet}. "
        f"{commentaire}".strip()
    )
    return livraison


def declarer_incident(livraison, user, type_incident, gravite, description, photo=None):
    incident = IncidentLivraison.objects.create(
        livraison=livraison, type_incident=type_incident, gravite=gravite, description=description,
        photo=photo, declare_par=user if user.is_authenticated else None,
    )
    _journaliser(
        livraison, user, f"Incident déclaré : {incident.get_type_incident_display()}.", visible_public=False
    )
    return incident


# ==============================================================================
# RÉSERVATION AUTOMATIQUE DE CRÉNEAU (via l'allocateur de quais de Kacem)
# ==============================================================================

def duree_operation_quai(nb_palettes, debit_palettes_heure=33):
    """Durée de chargement / déchargement estimée, arrondie au quart d'heure (minimum 30 min)."""
    minutes = max(30, int(nb_palettes * 60 / max(debit_palettes_heure, 1)))
    return timedelta(minutes=((minutes + 14) // 15) * 15)


@transaction.atomic
def reserver_creneau_auto(livraison, user, sens):
    """
    Réserve automatiquement le créneau de chargement (sens='chargement') ou de déchargement
    (sens='dechargement') sur le meilleur quai, choisi par SmartDockAllocator (module Kacem).
    Le créneau est créé EN_ATTENTE puis confirmé à la planification de la livraison.
    """
    from creneaux.ai_optimizer import SmartDockAllocator
    from creneaux.models import Creneau

    if sens == 'chargement':
        if livraison.creneau_chargement_id:
            raise TransitionImpossible("Un créneau de chargement est déjà lié à cette livraison.")
        entrepot = livraison.entrepot_origine
        duree = duree_operation_quai(livraison.nb_palettes)
        fin = timezone.localtime(livraison.date_depart_prevue)
        debut = fin - duree
        type_operation = 'CHARGEMENT'
    else:
        if livraison.type_livraison != 'INTER_ENTREPOT':
            raise TransitionImpossible("Une livraison client n'utilise pas de créneau de déchargement.")
        if livraison.creneau_dechargement_id:
            raise TransitionImpossible("Un créneau de déchargement est déjà lié à cette livraison.")
        entrepot = livraison.entrepot_destination
        duree = duree_operation_quai(livraison.nb_palettes)
        # Arrivée estimée arrondie au quart d'heure suivant
        eta = timezone.localtime(livraison.eta).replace(second=0, microsecond=0)
        debut = eta + timedelta(minutes=(-eta.minute) % 15)
        fin = debut + duree
        type_operation = 'DECHARGEMENT'

    if debut.date() != fin.date():
        raise TransitionImpossible("Le créneau calculé chevauche minuit : ajustez les horaires de la livraison.")

    type_camion = TYPE_CAMION_VERS_CRENEAU.get(livraison.camion.type_camion, 'AUTRE') if livraison.camion_id else 'SEMI_REMORQUE'
    resultat = SmartDockAllocator().recommend_best_dock(
        entrepot_id=entrepot.id,
        date_creneau=debut.date(),
        heure_debut=debut.time().replace(second=0, microsecond=0),
        heure_fin=fin.time().replace(second=0, microsecond=0),
        type_marchandise=livraison.type_marchandise,
        type_camion=type_camion,
        nb_palettes=livraison.nb_palettes,
    )
    if not resultat.get('success'):
        raise TransitionImpossible(
            f"Aucun quai disponible à {entrepot.nom} de {debut:%H:%M} à {fin:%H:%M} : {resultat.get('message', '')}"
        )

    creneau = Creneau(
        entrepot=entrepot,
        quai_id=resultat['meilleur_quai_id'],
        demandeur=user if user.is_authenticated else None,
        date_creneau=debut.date(),
        heure_debut=debut.time().replace(second=0, microsecond=0),
        heure_fin=fin.time().replace(second=0, microsecond=0),
        type_operation=type_operation,
        statut='EN_ATTENTE',
        priorite=livraison.priorite,
        transporteur_nom=(livraison.camion.societe_transport if livraison.camion_id else '') or "À affecter",
        immatriculation_camion=livraison.camion.immatriculation if livraison.camion_id else "À affecter",
        type_camion=type_camion,
        chauffeur_nom=livraison.chauffeur.nom_complet if livraison.chauffeur_id else "À affecter",
        type_marchandise=livraison.type_marchandise,
        nb_palettes=livraison.nb_palettes,
        poids_kg=livraison.poids_kg,
        numero_bl=livraison.numero_bl,
        consignes=f"Créneau réservé automatiquement pour la livraison {livraison.reference}.",
    )
    try:
        creneau.full_clean()
    except ValidationError as exc:
        raise TransitionImpossible(_message_validation(exc))
    creneau.save()
    creneau._enregistrer_historique('EN_ATTENTE', user, f"Créneau réservé par la livraison {livraison.reference}.")

    if sens == 'chargement':
        livraison.creneau_chargement = creneau
    else:
        livraison.creneau_dechargement = creneau
    livraison.save(update_fields=[f'creneau_{sens}', 'date_modification'])
    _journaliser(
        livraison, user,
        f"Créneau {creneau.reference} réservé sur {creneau.quai.numero} ({entrepot.nom}) "
        f"de {creneau.heure_debut:%H:%M} à {creneau.heure_fin:%H:%M}. {resultat.get('explication', '')}",
        visible_public=False,
    )
    return creneau, resultat


def marquer_retards(maintenant=None):
    """
    Signale les livraisons actives dont l'échéance est dépassée (ou dont l'ETA dépasse l'échéance).
    Utilisée par la commande check_retards_livraisons. Retourne la liste des livraisons nouvellement signalées.
    """
    from .models import Livraison

    maintenant = maintenant or timezone.now()
    nouvelles = []
    for livraison in Livraison.objects.filter(
        statut__in=('PLANIFIEE', 'EN_CHARGEMENT', 'EN_TRANSIT'), est_en_retard=False
    ).select_related('camion', 'entrepot_origine', 'entrepot_destination'):
        if maintenant > livraison.date_livraison_prevue or livraison.eta > livraison.date_livraison_prevue:
            livraison.est_en_retard = True
            livraison.save(update_fields=['est_en_retard', 'date_modification'])
            SuiviLivraison.objects.create(
                livraison=livraison,
                statut=livraison.statut,
                commentaire=f"Retard détecté : arrivée estimée {timezone.localtime(livraison.eta):%d/%m %H:%M}, "
                            f"échéance {timezone.localtime(livraison.date_livraison_prevue):%d/%m %H:%M}.",
            )
            nouvelles.append(livraison)
    return nouvelles
