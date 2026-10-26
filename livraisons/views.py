import csv
from datetime import date, datetime

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from camions.models import Camion
from chauffeurs.models import Chauffeur
from creneaux.models import Creneau
from entrepots.models import Entrepot

from . import geo, search, services
from .ai_service import DeepSeekLivraisonAI, explication_affectation_locale, risque_local
from .forms import (EchecForm, IncidentForm, LivraisonForm, MotifForm, PreuveLivraisonForm,
                    ReaffectationForm)
from .models import IncidentLivraison, Livraison, SuiviLivraison
from .permissions import (actions_autorisees, est_planificateur, est_transporteur, livraisons_session_required,
                          livraisons_visibles, peut_executer)
from .services import TransitionImpossible
from .smart_assign import MoteurAffectation


def _livraison_visible(request, pk):
    """Récupère une livraison dans le périmètre de l'utilisateur (404 sinon : on ne révèle pas son existence)."""
    qs = livraisons_visibles(request.user, Livraison.objects.select_related(
        'entrepot_origine', 'entrepot_destination', 'camion', 'chauffeur',
        'creneau_chargement__quai', 'creneau_dechargement__quai', 'createur',
    ))
    return get_object_or_404(qs, pk=pk)


def _refuser(request, livraison, message="Action non autorisée pour votre rôle ou dans l'état actuel de la livraison."):
    messages.error(request, message)
    return redirect('livraisons:livraison_detail', pk=livraison.pk)


# ==============================================================================
# TABLEAU DE BORD & RECHERCHE AVANCÉE
# ==============================================================================

@livraisons_session_required
def livraison_list(request):
    """Tableau de bord : KPI, recherche avancée multi-critères, recherche en langage naturel."""
    base = livraisons_visibles(request.user, Livraison.objects.select_related(
        'entrepot_origine', 'entrepot_destination', 'camion', 'chauffeur'
    ))
    filtres = search.lire_filtres(request.GET)
    resultats = search.appliquer_filtres(base, filtres)

    page = Paginator(resultats, 12).get_page(request.GET.get('page'))
    params = request.GET.copy()
    params.pop('page', None)

    context = {
        'page_obj': page,
        'livraisons': page.object_list,
        'filtres': filtres,
        'nb_filtres_actifs': search.compter_filtres_actifs(filtres),
        'querystring': params.urlencode(),
        'kpi': search.statistiques(base),
        'entrepots': Entrepot.objects.order_by('nom'),
        'chauffeurs': Chauffeur.objects.order_by('nom', 'prenom'),
        'camions': Camion.objects.order_by('immatriculation'),
        'statut_choices': [(code, Livraison(statut=code).statut_court) for code, _ in Livraison.STATUT_CHOICES],
        'type_choices': Livraison.TYPE_LIVRAISON_CHOICES,
        'priorite_choices': Livraison.PRIORITE_CHOICES,
        'marchandise_choices': Livraison.TYPE_MARCHANDISE_CHOICES,
        'tris': [(cle, libelle) for cle, (_, libelle) in search.TRIS.items()],
        'est_planificateur': est_planificateur(request.user),
        'explication_ia': request.GET.get('ia_explication', ''),
        'ia_disponible': DeepSeekLivraisonAI().disponible,
    }
    return render(request, 'livraisons/livraison_list.html', context)


@livraisons_session_required
@require_POST
def api_recherche_ia(request):
    """Recherche en langage naturel : DeepSeek (ou le moteur local) convertit la phrase en filtres validés."""
    texte = request.POST.get('texte', '').strip()
    if not texte:
        return JsonResponse({'success': False, 'message': "Décrivez les livraisons recherchées."}, status=400)
    resultat = DeepSeekLivraisonAI().interpreter_recherche(texte, list(Entrepot.objects.all()))
    filtres = resultat['filtres']
    filtres['ia_explication'] = resultat['explication']
    url = reverse('livraisons:livraison_list') + '?' + search.filtres_vers_querystring(filtres)
    return JsonResponse({'success': True, 'url': url, 'explication': resultat['explication'], 'source': resultat['source']})


@livraisons_session_required
def livraison_export_csv(request):
    """Export CSV des livraisons visibles selon les filtres courants (compatible Excel)."""
    filtres = search.lire_filtres(request.GET)
    livraisons = search.appliquer_filtres(
        livraisons_visibles(request.user, Livraison.objects.select_related(
            'entrepot_origine', 'entrepot_destination', 'camion', 'chauffeur')),
        filtres
    )
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="cargolink_livraisons_{date.today():%Y%m%d}.csv"'
    response.write('﻿'.encode('utf8'))
    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Référence', 'Code suivi', 'Type', 'Statut', 'Priorité', 'Départ', 'Destination',
        'Départ prévu', 'Échéance', 'Livrée le', 'À l\'heure', 'Camion', 'Chauffeur',
        'Marchandise', 'Palettes', 'Poids (kg)', 'N° BL', 'Distance (km)', 'CO2 estimé (kg)', 'Incidents',
    ])
    local = timezone.localtime
    for l in livraisons:
        a_l_heure = l.livree_a_l_heure
        writer.writerow([
            l.reference, l.code_suivi, l.get_type_livraison_display(), l.get_statut_display(),
            l.get_priorite_display(), l.entrepot_origine.nom, l.libelle_destination,
            local(l.date_depart_prevue).strftime('%d/%m/%Y %H:%M'),
            local(l.date_livraison_prevue).strftime('%d/%m/%Y %H:%M'),
            local(l.date_livraison_reelle).strftime('%d/%m/%Y %H:%M') if l.date_livraison_reelle else '',
            '' if a_l_heure is None else ('Oui' if a_l_heure else 'Non'),
            l.camion.immatriculation if l.camion_id else '', l.chauffeur.nom_complet if l.chauffeur_id else '',
            l.get_type_marchandise_display(), l.nb_palettes, l.poids_kg or '', l.numero_bl,
            l.distance_km or '', l.co2_estime_kg or '', l.incidents.count(),
        ])
    return response


# ==============================================================================
# CRUD
# ==============================================================================

@livraisons_session_required
def livraison_create(request):
    if not est_planificateur(request.user):
        messages.warning(request, "Accès restreint : seuls les planificateurs peuvent créer une livraison.")
        return redirect('livraisons:livraison_list')

    if request.method == 'POST':
        form = LivraisonForm(request.POST)
        if form.is_valid():
            livraison = form.save(commit=False)
            livraison.createur = request.user
            livraison.statut = 'BROUILLON'
            livraison.save()
            SuiviLivraison.objects.create(
                livraison=livraison, statut='BROUILLON', auteur=request.user, commentaire="Livraison créée."
            )
            messages.success(request, f"Livraison {livraison.reference} créée (code de suivi : {livraison.code_suivi}).")
            if 'planifier' in request.POST:
                try:
                    services.planifier(livraison, request.user)
                    messages.success(request, "Livraison planifiée : créneaux confirmés et ressources réservées.")
                except TransitionImpossible as exc:
                    messages.warning(request, f"Livraison enregistrée en brouillon. Planification impossible : {exc}")
            return redirect('livraisons:livraison_detail', pk=livraison.pk)
        messages.error(request, "Veuillez corriger les erreurs indiquées dans le formulaire.")
    else:
        initial = {}
        if request.GET.get('origine'):
            initial['entrepot_origine'] = request.GET.get('origine')
        form = LivraisonForm(initial=initial)

    return render(request, 'livraisons/livraison_form.html', {
        'form': form, 'is_edit': False, 'villes_connues': sorted(v.title() for v in geo.VILLES),
        'ia_disponible': DeepSeekLivraisonAI().disponible,
    })


@livraisons_session_required
def livraison_update(request, pk):
    livraison = _livraison_visible(request, pk)
    if not peut_executer(request.user, livraison, 'modifier'):
        return _refuser(request, livraison, "Cette livraison ne peut plus être modifiée (ou votre rôle ne le permet pas).")

    if request.method == 'POST':
        form = LivraisonForm(request.POST, instance=livraison)
        if form.is_valid():
            livraison = form.save()
            if livraison.statut == 'PLANIFIEE':
                for creneau in (livraison.creneau_chargement, livraison.creneau_dechargement):
                    if creneau is not None:
                        if creneau.statut == 'EN_ATTENTE':
                            creneau.confirmer(user=request.user)
                        services.synchroniser_creneau(livraison, creneau)
            SuiviLivraison.objects.create(
                livraison=livraison, statut=livraison.statut, auteur=request.user,
                commentaire="Informations de la livraison mises à jour.", visible_public=False,
            )
            messages.success(request, f"Livraison {livraison.reference} mise à jour.")
            return redirect('livraisons:livraison_detail', pk=livraison.pk)
        messages.error(request, "Veuillez corriger les erreurs indiquées dans le formulaire.")
    else:
        form = LivraisonForm(instance=livraison)

    return render(request, 'livraisons/livraison_form.html', {
        'form': form, 'is_edit': True, 'livraison': livraison,
        'villes_connues': sorted(v.title() for v in geo.VILLES),
        'ia_disponible': DeepSeekLivraisonAI().disponible,
    })


@livraisons_session_required
def livraison_detail(request, pk):
    livraison = _livraison_visible(request, pk)
    actions = actions_autorisees(request.user, livraison)
    suivis = livraison.suivis.select_related('auteur')
    context = {
        'livraison': livraison,
        'actions': actions,
        'suivis': suivis,
        'incidents': livraison.incidents.select_related('declare_par'),
        'risque': risque_local(livraison),
        'motif_form': MotifForm(),
        'echec_form': EchecForm(),
        'reaffectation_form': ReaffectationForm(),
        'est_planificateur': est_planificateur(request.user),
        'ia_disponible': DeepSeekLivraisonAI().disponible,
        'url_suivi_public': request.build_absolute_uri(
            reverse('livraisons:suivi_public', kwargs={'code': livraison.code_suivi})
        ),
    }
    return render(request, 'livraisons/livraison_detail.html', context)


# ==============================================================================
# TRANSITIONS D'ÉTAT (POST uniquement)
# ==============================================================================

ACTIONS_SIMPLES = {
    'planifier': (services.planifier, "Livraison planifiée : créneaux confirmés, ressources réservées."),
    'charger': (services.charger, "Camion à quai : chargement en cours. Le quai est maintenant occupé."),
    'partir': (services.partir, "Départ validé : quai libéré, camion en transit, historiques mis à jour."),
    'arriver': (services.arriver, "Arrivée à destination enregistrée."),
}


@livraisons_session_required
@require_POST
def livraison_action(request, pk, action):
    livraison = _livraison_visible(request, pk)
    if action == 'reserver_creneau':
        if not peut_executer(request.user, livraison, 'modifier'):
            return _refuser(request, livraison)
    elif not peut_executer(request.user, livraison, action):
        return _refuser(request, livraison)

    try:
        if action in ACTIONS_SIMPLES:
            fonction, message = ACTIONS_SIMPLES[action]
            fonction(livraison, request.user)
            messages.success(request, message)
        elif action == 'annuler':
            form = MotifForm(request.POST)
            if not form.is_valid():
                return _refuser(request, livraison, "Le motif d'annulation est obligatoire.")
            services.annuler(livraison, request.user, form.cleaned_data['motif'])
            messages.warning(request, f"Livraison {livraison.reference} annulée. Les créneaux liés ont été libérés.")
        elif action == 'echouer':
            form = EchecForm(request.POST)
            if not form.is_valid():
                return _refuser(request, livraison, "Le motif de l'échec est obligatoire.")
            services.echouer(livraison, request.user, form.cleaned_data['motif'], form.cleaned_data['type_incident'])
            messages.warning(request, "Échec de livraison enregistré. Camion et chauffeur remis à disposition.")
        elif action == 'reaffecter':
            form = ReaffectationForm(request.POST)
            if not form.is_valid():
                return _refuser(request, livraison, " ".join(form.non_field_errors()) or "Réaffectation invalide.")
            services.reaffecter(
                livraison, request.user, form.cleaned_data['camion'], form.cleaned_data['chauffeur'],
                form.cleaned_data['ancien_camion_en_panne'], form.cleaned_data['commentaire'],
            )
            messages.success(request, "Réaffectation effectuée et créneaux mis à jour.")
        elif action == 'reserver_creneau':
            sens = request.POST.get('sens')
            if sens not in ('chargement', 'dechargement'):
                return _refuser(request, livraison, "Type de créneau inconnu.")
            creneau, resultat = services.reserver_creneau_auto(livraison, request.user, sens)
            messages.success(
                request,
                f"Créneau {creneau.reference} réservé sur {creneau.quai.numero} "
                f"({creneau.heure_debut:%H:%M}-{creneau.heure_fin:%H:%M}) — score allocateur {resultat.get('score_optimal')}/100."
            )
        else:
            return _refuser(request, livraison, "Action inconnue.")
    except TransitionImpossible as exc:
        messages.error(request, str(exc))
    return redirect('livraisons:livraison_detail', pk=livraison.pk)


@livraisons_session_required
def livraison_pod(request, pk):
    """Saisie de la preuve de livraison (signature au doigt, photo, réserves) — optimisée mobile."""
    livraison = _livraison_visible(request, pk)
    if not peut_executer(request.user, livraison, 'livrer'):
        return _refuser(request, livraison, "La preuve de livraison ne peut être saisie qu'après l'arrivée à destination.")

    if request.method == 'POST':
        form = PreuveLivraisonForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                services.livrer(
                    livraison, request.user,
                    receptionnaire_nom=form.cleaned_data['receptionnaire_nom'],
                    signature_data_url=form.cleaned_data['signature_data'],
                    photo=form.cleaned_data['photo_preuve'],
                    reserves=form.cleaned_data['reserves'],
                    conforme=form.cleaned_data['livraison_conforme'],
                    note_satisfaction=form.cleaned_data['note_satisfaction'],
                )
                messages.success(request, f"Livraison {livraison.reference} validée. Merci !")
                if est_transporteur(request.user):
                    return redirect('livraisons:mes_missions')
                return redirect('livraisons:livraison_detail', pk=livraison.pk)
            except TransitionImpossible as exc:
                form.add_error(None, str(exc))
    else:
        form = PreuveLivraisonForm(initial={'receptionnaire_nom': livraison.destinataire_nom})
    return render(request, 'livraisons/livraison_pod.html', {'livraison': livraison, 'form': form})


@livraisons_session_required
def incident_create(request, pk):
    livraison = _livraison_visible(request, pk)
    if not peut_executer(request.user, livraison, 'incident'):
        return _refuser(request, livraison, "Impossible de déclarer un incident sur cette livraison.")
    if request.method == 'POST':
        form = IncidentForm(request.POST, request.FILES)
        if form.is_valid():
            incident = services.declarer_incident(
                livraison, request.user, form.cleaned_data['type_incident'], form.cleaned_data['gravite'],
                form.cleaned_data['description'], form.cleaned_data.get('photo'),
            )
            messages.warning(request, f"Incident « {incident.get_type_incident_display()} » déclaré. Le planificateur est alerté.")
            if est_transporteur(request.user):
                return redirect('livraisons:mes_missions')
            return redirect('livraisons:livraison_detail', pk=livraison.pk)
    else:
        form = IncidentForm()
    return render(request, 'livraisons/incident_form.html', {'livraison': livraison, 'form': form})


@livraisons_session_required
@require_POST
def incident_resoudre(request, pk):
    incident = get_object_or_404(IncidentLivraison, pk=pk)
    livraison = _livraison_visible(request, incident.livraison_id)
    if not est_planificateur(request.user):
        return _refuser(request, livraison, "Seul un planificateur peut clôturer un incident.")
    incident.resolu = True
    incident.resolution = request.POST.get('resolution', '').strip()[:500] or "Incident traité."
    incident.date_resolution = timezone.now()
    incident.save(update_fields=['resolu', 'resolution', 'date_resolution'])
    messages.success(request, "Incident marqué comme résolu.")
    return redirect('livraisons:livraison_detail', pk=livraison.pk)


# ==============================================================================
# ESPACE CHAUFFEUR MOBILE, BON DE LIVRAISON, SUIVI PUBLIC
# ==============================================================================

@livraisons_session_required
def mes_missions(request):
    """Vue mobile du transporteur : livraisons actives et prochaines, avec la prochaine action en un geste."""
    qs = livraisons_visibles(request.user, Livraison.objects.select_related(
        'entrepot_origine', 'entrepot_destination', 'camion', 'chauffeur',
        'creneau_chargement__quai', 'creneau_dechargement__quai',
    ))
    en_cours = qs.filter(statut__in=('PLANIFIEE', 'EN_CHARGEMENT', 'EN_TRANSIT', 'ARRIVEE')).order_by('date_depart_prevue')
    recentes = qs.filter(statut__in=('LIVREE', 'ECHEC')).order_by('-date_livraison_reelle', '-date_modification')[:5]
    missions = [{'livraison': l, 'actions': actions_autorisees(request.user, l)} for l in en_cours]
    return render(request, 'livraisons/mes_missions.html', {'missions': missions, 'recentes': recentes})


@livraisons_session_required
def bon_livraison(request, pk):
    livraison = _livraison_visible(request, pk)
    return render(request, 'livraisons/bon_livraison.html', {
        'livraison': livraison,
        'url_suivi_public': request.build_absolute_uri(
            reverse('livraisons:suivi_public', kwargs={'code': livraison.code_suivi})
        ),
        'imprime_le': timezone.localtime(),
    })


def suivi_recherche(request):
    """Page publique : saisie du code de suivi (sans connexion)."""
    code = request.GET.get('code', '').strip().upper()
    if code:
        return redirect('livraisons:suivi_public', code=code)
    return render(request, 'livraisons/suivi_public.html', {'livraison': None, 'code': ''})


def suivi_public(request, code):
    """
    Suivi public par code (sans connexion) : statut, étapes et heure estimée uniquement.
    Aucune donnée personnelle (téléphone, nom du chauffeur, adresse exacte) n'est exposée.
    """
    livraison = Livraison.objects.select_related('entrepot_origine', 'entrepot_destination', 'camion').filter(
        code_suivi=code.upper()
    ).first()
    if livraison is None:
        return render(request, 'livraisons/suivi_public.html', {'livraison': None, 'code': code, 'introuvable': True},
                      status=404)
    return render(request, 'livraisons/suivi_public.html', {
        'livraison': livraison,
        'code': code,
        'etapes_publiques': livraison.suivis.filter(visible_public=True).order_by('date'),
    })


# ==============================================================================
# API IA & AIDE À LA SAISIE (AJAX)
# ==============================================================================

def _parse_datetime(valeur):
    if not valeur:
        return None
    try:
        return timezone.make_aware(datetime.strptime(valeur, '%Y-%m-%dT%H:%M'))
    except ValueError:
        return None


def _parse_int(valeur):
    try:
        return int(valeur) if valeur not in (None, '') else None
    except (TypeError, ValueError):
        return None


@livraisons_session_required
@require_POST
def api_smart_assign(request):
    """Affectation intelligente : classement des couples camion + chauffeur, explication IA optionnelle."""
    if not est_planificateur(request.user):
        return JsonResponse({'success': False, 'message': "Réservé aux planificateurs."}, status=403)

    debut = _parse_datetime(request.POST.get('date_depart_prevue'))
    fin = _parse_datetime(request.POST.get('date_livraison_prevue'))
    origine = Entrepot.objects.filter(pk=_parse_int(request.POST.get('entrepot_origine'))).first()
    if debut and not fin and origine:
        if request.POST.get('type_livraison') == 'INTER_ENTREPOT':
            destination = Entrepot.objects.filter(pk=_parse_int(request.POST.get('entrepot_destination'))).first()
            ville = destination.ville if destination else ''
        else:
            ville = request.POST.get('ville_livraison', '')
        duree = geo.duree_trajet(geo.distance_km(origine.ville, ville))
        fin = debut + duree if duree else None
    if not debut or not fin:
        return JsonResponse({
            'success': False,
            'message': "Renseignez le départ prévu et la destination (ou l'échéance) pour lancer l'affectation intelligente."
        })

    type_marchandise = request.POST.get('type_marchandise') or 'STANDARD'
    resultat = MoteurAffectation().recommander(
        poids_kg=_parse_int(request.POST.get('poids_kg')),
        nb_palettes=_parse_int(request.POST.get('nb_palettes')),
        type_marchandise=type_marchandise,
        debut=debut, fin=fin,
        livraison_pk=_parse_int(request.POST.get('livraison_pk')),
    )
    contexte = {
        'marchandise': dict(Livraison.TYPE_MARCHANDISE_CHOICES).get(type_marchandise, type_marchandise),
        'poids_kg': request.POST.get('poids_kg'), 'nb_palettes': request.POST.get('nb_palettes'),
        'depart': timezone.localtime(debut).strftime('%d/%m/%Y %H:%M'),
        'echeance': timezone.localtime(fin).strftime('%d/%m/%Y %H:%M'),
        'priorite': request.POST.get('priorite', 'NORMALE'),
    }
    if request.POST.get('ia') == '1':
        resultat['explication'] = DeepSeekLivraisonAI().expliquer_affectation(resultat, contexte)
    else:
        resultat['explication'] = explication_affectation_locale(resultat)
    return JsonResponse(resultat)


@livraisons_session_required
@require_POST
def api_analyse_risque(request, pk):
    livraison = _livraison_visible(request, pk)
    return JsonResponse(DeepSeekLivraisonAI().analyser_risque(livraison))


@livraisons_session_required
@require_POST
def api_message_destinataire(request, pk):
    livraison = _livraison_visible(request, pk)
    langue = request.POST.get('langue', 'fr')
    objectif = request.POST.get('objectif', 'information')
    if objectif not in ('information', 'retard', 'livree'):
        objectif = 'information'
    return JsonResponse(DeepSeekLivraisonAI().rediger_message(livraison, langue, objectif))


@livraisons_session_required
def api_creneaux(request):
    """Créneaux ouverts d'un entrepôt (pour filtrer dynamiquement les listes du formulaire)."""
    entrepot_id = _parse_int(request.GET.get('entrepot'))
    type_operation = request.GET.get('type') if request.GET.get('type') in ('CHARGEMENT', 'DECHARGEMENT') else None
    creneaux = Creneau.objects.filter(
        entrepot_id=entrepot_id, type_operation=type_operation, statut__in=('EN_ATTENTE', 'CONFIRME')
    ).select_related('quai').order_by('date_creneau', 'heure_debut') if entrepot_id and type_operation else []
    return JsonResponse({'creneaux': [
        {
            'id': c.id,
            'label': f"{c.reference} • {c.quai.numero} • {c.date_creneau:%d/%m} {c.heure_debut:%H:%M}-{c.heure_fin:%H:%M} "
                     f"({c.get_statut_display()})",
        } for c in creneaux
    ]})


@livraisons_session_required
def api_estimation(request):
    """Distance, durée, échéance suggérée et CO2 estimés pour le formulaire (calcul local, sans IA)."""
    origine = Entrepot.objects.filter(pk=_parse_int(request.GET.get('origine'))).first()
    destination = Entrepot.objects.filter(pk=_parse_int(request.GET.get('destination'))).first()
    ville = destination.ville if destination else request.GET.get('ville', '')
    camion = Camion.objects.filter(pk=_parse_int(request.GET.get('camion'))).first()
    type_camion = camion.type_camion if camion else 'SEMI_REMORQUE'
    distance = geo.distance_km(origine.ville if origine else '', ville)
    if distance is None:
        return JsonResponse({'success': False, 'message': "Ville non reconnue : estimation indisponible."})
    duree = geo.duree_trajet(distance, type_camion)
    depart = _parse_datetime(request.GET.get('depart'))
    return JsonResponse({
        'success': True,
        'distance_km': distance,
        'duree_minutes': int(duree.total_seconds() // 60),
        'echeance_suggeree': timezone.localtime(depart + duree).strftime('%Y-%m-%dT%H:%M') if depart else None,
        'co2_kg': geo.co2_kg(distance, camion.norme_anti_pollution if camion else 'EURO_6', type_camion),
    })
