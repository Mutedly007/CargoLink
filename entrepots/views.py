from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from .models import Entrepot, Quai
from .forms import EntrepotForm, QuaiForm


# ==============================================================================
# CONTRÔLE D'ACCÈS & RÔLES
# ==============================================================================

def is_entrepot_manager(user):
    """
    Vérifie si l'utilisateur connecté est un Gestionnaire d'Entrepôt
    (ou Administrateur / Superutilisateur).
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile = getattr(user, 'profile', None)
    if profile:
        return profile.is_entrepot
    return False


# ==============================================================================
# CRUD ENTREPÔTS
# ==============================================================================

def entrepot_list(request):
    """
    R (Read List) : Affiche la liste des entrepôts avec recherche, filtres et métriques KPI.
    """
    query = request.GET.get('q', '').strip()
    statut_filter = request.GET.get('statut', '').strip()
    ville_filter = request.GET.get('ville', '').strip()

    entrepots = Entrepot.objects.annotate(
        quais_total=Count('quais')
    ).prefetch_related('quais')

    if query:
        entrepots = entrepots.filter(
            Q(nom__icontains=query) |
            Q(code__icontains=query) |
            Q(ville__icontains=query) |
            Q(adresse__icontains=query)
        )

    if statut_filter:
        entrepots = entrepots.filter(statut=statut_filter)

    if ville_filter:
        entrepots = entrepots.filter(ville__iexact=ville_filter)

    # Calcul des métriques globales pour le tableau de bord
    all_entrepots = Entrepot.objects.all()
    all_quais = Quai.objects.all()
    
    total_entrepots = all_entrepots.count()
    total_quais = all_quais.count()
    quais_disponibles = all_quais.filter(statut='DISPONIBLE').count()
    quais_occupes = all_quais.filter(statut='OCCUPE').count()
    capacite_globale = all_entrepots.aggregate(total=Sum('capacite_palettes'))['total'] or 0

    # Liste des villes uniques pour le filtre
    villes = Entrepot.objects.values_list('ville', flat=True).distinct().order_by('ville')

    context = {
        'entrepots': entrepots,
        'query': query,
        'statut_filter': statut_filter,
        'ville_filter': ville_filter,
        'villes': villes,
        'total_entrepots': total_entrepots,
        'total_quais': total_quais,
        'quais_disponibles': quais_disponibles,
        'quais_occupes': quais_occupes,
        'capacite_globale': capacite_globale,
        'can_manage_entrepots': is_entrepot_manager(request.user),
        'page_title': "Gestion des Entrepôts & Quais • CargoLink",
    }
    return render(request, 'entrepots/entrepot_list.html', context)


def entrepot_detail(request, pk):
    """
    R (Read Detail) : Vue détaillée d'un entrepôt et de tous ses quais associés.
    """
    entrepot = get_object_or_404(Entrepot.objects.prefetch_related('quais'), pk=pk)
    quais = entrepot.quais.all()

    context = {
        'entrepot': entrepot,
        'quais': quais,
        'can_manage_entrepots': is_entrepot_manager(request.user),
        'page_title': f"{entrepot.nom} • Détails Entrepôt",
    }
    return render(request, 'entrepots/entrepot_detail.html', context)


@login_required
def entrepot_create(request):
    """
    C (Create) : Formulaire d'ajout d'un nouvel entrepôt.
    Réservé exclusivement au rôle Gestionnaire d'Entrepôt (et Administrateur).
    """
    if not is_entrepot_manager(request.user):
        messages.warning(
            request,
            "Accès restreint : Seul le rôle Gestionnaire d'Entrepôt est habilité à ajouter des entrepôts. "
            "Votre profil dispose uniquement d'un droit de consultation."
        )
        return redirect('entrepots:entrepot_list')

    if request.method == 'POST':
        form = EntrepotForm(request.POST)
        if form.is_valid():
            entrepot = form.save(commit=False)
            if not entrepot.gestionnaire and request.user.is_authenticated:
                entrepot.gestionnaire = request.user
            entrepot.save()
            messages.success(
                request,
                f"L'entrepôt « {entrepot.nom} » ({entrepot.code}) a été créé avec succès !"
            )
            return redirect('entrepots:entrepot_detail', pk=entrepot.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs indiquées dans le formulaire.")
    else:
        form = EntrepotForm(initial={'gestionnaire': request.user if request.user.is_authenticated else None})

    context = {
        'form': form,
        'action_title': "Ajouter un Nouvel Entrepôt",
        'btn_label': "Enregistrer l'entrepôt",
        'is_edit': False,
        'page_title': "Nouvel Entrepôt • CargoLink",
    }
    return render(request, 'entrepots/entrepot_form.html', context)


@login_required
def entrepot_update(request, pk):
    """
    U (Update) : Modification des informations d'un entrepôt existant.
    Réservé exclusivement au rôle Gestionnaire d'Entrepôt (et Administrateur).
    """
    if not is_entrepot_manager(request.user):
        messages.warning(
            request,
            "Accès restreint : Seul le rôle Gestionnaire d'Entrepôt est habilité à modifier cet entrepôt. "
            "Votre profil dispose uniquement d'un droit de consultation."
        )
        return redirect('entrepots:entrepot_detail', pk=pk)

    entrepot = get_object_or_404(Entrepot, pk=pk)

    if request.method == 'POST':
        form = EntrepotForm(request.POST, instance=entrepot)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"L'entrepôt « {entrepot.nom} » a été mis à jour avec succès !"
            )
            return redirect('entrepots:entrepot_detail', pk=entrepot.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = EntrepotForm(instance=entrepot)

    context = {
        'form': form,
        'entrepot': entrepot,
        'action_title': f"Modifier l'Entrepôt : {entrepot.nom}",
        'btn_label': "Mettre à jour l'entrepôt",
        'is_edit': True,
        'page_title': f"Modifier {entrepot.nom} • CargoLink",
    }
    return render(request, 'entrepots/entrepot_form.html', context)


@login_required
def entrepot_delete(request, pk):
    """
    D (Delete) : Suppression d'un entrepôt avec avertissement des quais associés.
    Réservé exclusivement au rôle Gestionnaire d'Entrepôt (et Administrateur).
    """
    if not is_entrepot_manager(request.user):
        messages.warning(
            request,
            "Accès restreint : Seul le rôle Gestionnaire d'Entrepôt est habilité à supprimer cet entrepôt. "
            "Votre profil dispose uniquement d'un droit de consultation."
        )
        return redirect('entrepots:entrepot_detail', pk=pk)

    entrepot = get_object_or_404(Entrepot, pk=pk)

    if request.method == 'POST':
        nom = entrepot.nom
        code = entrepot.code
        entrepot.delete()
        messages.info(request, f"L'entrepôt « {nom} » ({code}) et tous ses quais associés ont été supprimés.")
        return redirect('entrepots:entrepot_list')

    context = {
        'entrepot': entrepot,
        'page_title': f"Supprimer {entrepot.nom} • CargoLink",
    }
    return render(request, 'entrepots/entrepot_confirm_delete.html', context)


# ==============================================================================
# CRUD QUAIS DE CHARGEMENT
# ==============================================================================

def quai_list(request):
    """
    R (Read List) : Vue d'ensemble de tous les quais du réseau avec filtres par statut et type.
    """
    statut_filter = request.GET.get('statut', '').strip()
    type_filter = request.GET.get('type', '').strip()
    entrepot_id = request.GET.get('entrepot', '').strip()

    quais = Quai.objects.select_related('entrepot').all()

    if statut_filter:
        quais = quais.filter(statut=statut_filter)
    if type_filter:
        quais = quais.filter(type_quai=type_filter)
    if entrepot_id:
        quais = quais.filter(entrepot_id=entrepot_id)

    entrepots = Entrepot.objects.all().order_by('nom')

    context = {
        'quais': quais,
        'entrepots': entrepots,
        'statut_filter': statut_filter,
        'type_filter': type_filter,
        'selected_entrepot_id': entrepot_id,
        'can_manage_entrepots': is_entrepot_manager(request.user),
        'page_title': "Régulation des Quais • CargoLink",
    }
    return render(request, 'entrepots/quai_list.html', context)


def quai_detail(request, pk):
    """
    R (Read Detail) : Fiche technique et état opérationnel d'un quai.
    """
    quai = get_object_or_404(Quai.objects.select_related('entrepot'), pk=pk)
    context = {
        'quai': quai,
        'can_manage_entrepots': is_entrepot_manager(request.user),
        'page_title': f"{quai.numero} • Fiche Quai",
    }
    return render(request, 'entrepots/quai_detail.html', context)


@login_required
def quai_create(request, entrepot_pk=None):
    """
    C (Create) : Ajout d'un quai, optionnellement pré-attaché à un entrepôt.
    Réservé exclusivement au rôle Gestionnaire d'Entrepôt (et Administrateur).
    """
    if not is_entrepot_manager(request.user):
        messages.warning(
            request,
            "Accès restreint : Seul le rôle Gestionnaire d'Entrepôt est habilité à ajouter des quais. "
            "Votre profil dispose uniquement d'un droit de consultation."
        )
        if entrepot_pk:
            return redirect('entrepots:entrepot_detail', pk=entrepot_pk)
        return redirect('entrepots:quai_list')

    initial_data = {}
    preset_entrepot = None
    if entrepot_pk:
        preset_entrepot = get_object_or_404(Entrepot, pk=entrepot_pk)
        initial_data['entrepot'] = preset_entrepot
    elif request.GET.get('entrepot'):
        preset_entrepot = Entrepot.objects.filter(pk=request.GET.get('entrepot')).first()
        if preset_entrepot:
            initial_data['entrepot'] = preset_entrepot

    if request.method == 'POST':
        form = QuaiForm(request.POST)
        if form.is_valid():
            quai = form.save()
            messages.success(
                request,
                f"Le quai « {quai.numero} » a été ajouté à l'entrepôt {quai.entrepot.nom} avec succès !"
            )
            return redirect('entrepots:entrepot_detail', pk=quai.entrepot.pk)
        else:
            messages.error(request, "Erreur dans les champs du quai. Veuillez vérifier.")
    else:
        form = QuaiForm(initial=initial_data)

    context = {
        'form': form,
        'preset_entrepot': preset_entrepot,
        'action_title': f"Ajouter un Quai {f'pour {preset_entrepot.nom}' if preset_entrepot else ''}",
        'btn_label': "Créer le quai",
        'is_edit': False,
        'page_title': "Nouveau Quai • CargoLink",
    }
    return render(request, 'entrepots/quai_form.html', context)


@login_required
def quai_update(request, pk):
    """
    U (Update) : Modification des paramètres d'un quai.
    Réservé exclusivement au rôle Gestionnaire d'Entrepôt (et Administrateur).
    """
    if not is_entrepot_manager(request.user):
        messages.warning(
            request,
            "Accès restreint : Seul le rôle Gestionnaire d'Entrepôt est habilité à modifier ce quai. "
            "Votre profil dispose uniquement d'un droit de consultation."
        )
        return redirect('entrepots:quai_detail', pk=pk)

    quai = get_object_or_404(Quai, pk=pk)

    if request.method == 'POST':
        form = QuaiForm(request.POST, instance=quai)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le quai « {quai.numero} » a été mis à jour !")
            return redirect('entrepots:entrepot_detail', pk=quai.entrepot.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs de saisie.")
    else:
        form = QuaiForm(instance=quai)

    context = {
        'form': form,
        'quai': quai,
        'action_title': f"Modifier le Quai : {quai.numero}",
        'btn_label': "Enregistrer les modifications",
        'is_edit': True,
        'page_title': f"Modifier {quai.numero} • CargoLink",
    }
    return render(request, 'entrepots/quai_form.html', context)


@login_required
def quai_delete(request, pk):
    """
    D (Delete) : Suppression d'un quai.
    Réservé exclusivement au rôle Gestionnaire d'Entrepôt (et Administrateur).
    """
    if not is_entrepot_manager(request.user):
        messages.warning(
            request,
            "Accès restreint : Seul le rôle Gestionnaire d'Entrepôt est habilité à supprimer ce quai. "
            "Votre profil dispose uniquement d'un droit de consultation."
        )
        return redirect('entrepots:quai_detail', pk=pk)

    quai = get_object_or_404(Quai, pk=pk)
    entrepot_pk = quai.entrepot.pk

    if request.method == 'POST':
        numero = quai.numero
        quai.delete()
        messages.info(request, f"Le quai « {numero} » a été supprimé.")
        return redirect('entrepots:entrepot_detail', pk=entrepot_pk)

    context = {
        'quai': quai,
        'page_title': f"Supprimer le Quai {quai.numero} • CargoLink",
    }
    return render(request, 'entrepots/quai_confirm_delete.html', context)


@login_required
def quai_toggle_status(request, pk):
    """
    Action rapide (Live Demo) : Bascule instantanément le statut d'un quai
    entre 'DISPONIBLE' et 'OCCUPE', permettant au jury de constater la mise à jour en direct.
    Réservé exclusivement au rôle Gestionnaire d'Entrepôt (et Administrateur).
    """
    if not is_entrepot_manager(request.user):
        messages.warning(
            request,
            "Accès restreint : Seul le rôle Gestionnaire d'Entrepôt est habilité à modifier l'état opérationnel d'un quai."
        )
        return redirect('entrepots:quai_detail', pk=pk)

    quai = get_object_or_404(Quai, pk=pk)
    if quai.statut == 'DISPONIBLE':
        quai.occuper()
        messages.warning(request, f"Le quai « {quai.numero} » est maintenant OCCUPÉ (opération en cours).")
    else:
        quai.liberer()
        messages.success(request, f"Le quai « {quai.numero} » a été LIBÉRÉ (disponible pour amarrage).")

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('entrepots:entrepot_detail', pk=quai.entrepot.pk)


# ==============================================================================
# SMART CAPACITY OPTIMIZER AI (Strict Scope: Entrepot & Quai)
# ==============================================================================
import json
from django.http import JsonResponse, HttpResponseBadRequest
from .services import CapacityAnalyzer, CapacityOptimizer, GeminiCapacityRecommender


@login_required
def capacity_optimizer_dashboard(request):
    """
    Tableau de bord visuel d'Intelligence de Capacité & Optimisation IA.
    Analyse les entrepôts et les quais, détecte les anomalies et formule
    des recommandations hiérarchisées avec Google Gemini et What-If simulator.
    """
    # 1. Analyse déterministe factuelle
    analysis = CapacityAnalyzer.get_full_analysis()
    opportunities = CapacityOptimizer.find_feasible_redistributions(analysis)

    # 2. Gestion des recommandations (avec mise en cache session)
    force_refresh = request.GET.get('refresh') == '1'
    recs_data = None

    if not force_refresh:
        recs_data = request.session.get('capacity_recommendations')

    if not recs_data:
        recs_data = GeminiCapacityRecommender.generate_recommendations(analysis, opportunities)
        request.session['capacity_recommendations'] = recs_data
        request.session.modified = True

    # 3. États de gestion des recommandations (Revues / Ignorées)
    dismissed_ids = set(request.session.get('dismissed_recs', []))
    reviewed_ids = set(request.session.get('reviewed_recs', []))

    recommendations = []
    for rec in recs_data.get('recommendations', []):
        r_copy = dict(rec)
        r_copy['is_dismissed'] = r_copy['id'] in dismissed_ids
        r_copy['is_reviewed'] = r_copy['id'] in reviewed_ids
        recommendations.append(r_copy)

    # Métriques pour le filtrage
    total_recs = len(recommendations)
    active_recs = sum(1 for r in recommendations if not r['is_dismissed'])
    high_prio_count = sum(1 for r in recommendations if r['priority_level'] == 'HIGH' and not r['is_dismissed'])
    reviewed_count = sum(1 for r in recommendations if r['is_reviewed'])
    dismissed_count = sum(1 for r in recommendations if r['is_dismissed'])

    # 4. Données préparées pour le simulateur What-If
    simulator_warehouses = []
    for ent in analysis['warehouses']:
        simulator_warehouses.append({
            'id': ent['id'],
            'nom': ent['nom'],
            'code': ent['code'],
            'ville': ent['ville'],
            'capacite_palettes': ent['capacite_palettes'],
            'superficie_m2': ent['superficie_m2'],
            'nb_quais': ent['nb_quais'],
            'quais_operationnels': ent['quais_operationnels'],
            'nb_occupes': ent['nb_occupes'],
            'nb_reserves': ent['nb_reserves'],
            'nb_disponibles': ent['nb_disponibles'],
            'utilization_pct': ent['utilization_pct'],
        })

    context = {
        'analysis': analysis,
        'metrics': analysis['metrics'],
        'thresholds': analysis['thresholds'],
        'warehouses': analysis['warehouses'],
        'underutilized_warehouses': analysis['underutilized_warehouses'],
        'near_capacity_warehouses': analysis['near_capacity_warehouses'],
        'critical_warehouses': analysis['critical_warehouses'],
        'anomalies': analysis['anomalies'],
        'city_imbalances': analysis['city_imbalances'],
        'data_limitations': analysis['data_limitations'],
        'opportunities': opportunities,
        'recs_summary': recs_data.get('summary', ''),
        'recs_source': recs_data.get('source', 'deterministic'),
        'recs_model': recs_data.get('model_used', 'Gemini 2.5 Flash'),
        'fallback_reason': recs_data.get('fallback_reason', ''),
        'recommendations': recommendations,
        'total_recs': total_recs,
        'active_recs': active_recs,
        'high_prio_count': high_prio_count,
        'reviewed_count': reviewed_count,
        'dismissed_count': dismissed_count,
        'simulator_warehouses_json': json.dumps(simulator_warehouses),
        'page_title': "Smart Capacity Optimizer AI • CargoLink",
    }

    return render(request, 'entrepots/capacity_optimizer.html', context)


@login_required
def capacity_optimizer_simulate_api(request):
    """
    Endpoint AJAX pour exécuter une simulation 'What-If' côté serveur.
    Validation stricte : ne modifie JAMAIS la base de données de production.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("Méthode POST requise.")

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': "Format JSON invalide."}, status=400)

    try:
        entrepot_id = int(data.get('entrepot_id', 0))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': "Identifiant d'entrepôt invalide."}, status=400)

    proposed_cap = data.get('proposed_capacite_palettes')
    if proposed_cap is not None:
        try:
            proposed_cap = int(proposed_cap)
        except (TypeError, ValueError):
            return JsonResponse({'success': False, 'error': "Capacité palettes invalide."}, status=400)

    hypo_docks = data.get('hypothetical_occupied_docks')
    if hypo_docks is not None:
        try:
            hypo_docks = int(hypo_docks)
        except (TypeError, ValueError):
            hypo_docks = None

    selected_quai_id = data.get('selected_quai_id')
    if selected_quai_id:
        try:
            selected_quai_id = int(selected_quai_id)
        except (TypeError, ValueError):
            selected_quai_id = None

    proposed_throughput = data.get('proposed_quai_throughput')
    if proposed_throughput is not None:
        try:
            proposed_throughput = int(proposed_throughput)
        except (TypeError, ValueError):
            proposed_throughput = None

    result = CapacityOptimizer.simulate_what_if(
        entrepot_id=entrepot_id,
        proposed_capacite_palettes=proposed_cap,
        hypothetical_occupied_docks=hypo_docks,
        selected_quai_id=selected_quai_id,
        proposed_quai_throughput=proposed_throughput,
    )
    return JsonResponse(result)


@login_required
def capacity_optimizer_action_api(request):
    """
    Gestion des statuts des recommandations (Marquer comme revue, ignorer, rétablir).
    Sauvegardé dans la session du gestionnaire sans impacter le schéma de BDD.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("Méthode POST requise.")

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': "Format JSON invalide."}, status=400)

    rec_id = str(data.get('rec_id', '')).strip()
    action = str(data.get('action', '')).strip()

    if not rec_id:
        return JsonResponse({'success': False, 'error': "ID de recommandation manquant."}, status=400)

    dismissed = set(request.session.get('dismissed_recs', []))
    reviewed = set(request.session.get('reviewed_recs', []))

    if action == 'dismiss':
        dismissed.add(rec_id)
    elif action == 'review':
        reviewed.add(rec_id)
    elif action == 'unreview':
        reviewed.discard(rec_id)
    elif action == 'restore':
        dismissed.discard(rec_id)
    else:
        return JsonResponse({'success': False, 'error': "Action non reconnue."}, status=400)

    request.session['dismissed_recs'] = list(dismissed)
    request.session['reviewed_recs'] = list(reviewed)
    request.session.modified = True

    return JsonResponse({
        'success': True,
        'rec_id': rec_id,
        'action': action,
        'is_dismissed': rec_id in dismissed,
        'is_reviewed': rec_id in reviewed,
        'dismissed_count': len(dismissed),
        'reviewed_count': len(reviewed),
    })


@login_required
def capacity_optimizer_refresh_api(request):
    """
    Régénération forcée des recommandations IA à la demande de l'utilisateur.
    """
    analysis = CapacityAnalyzer.get_full_analysis()
    opportunities = CapacityOptimizer.find_feasible_redistributions(analysis)

    recs_data = GeminiCapacityRecommender.generate_recommendations(analysis, opportunities)
    request.session['capacity_recommendations'] = recs_data
    request.session.modified = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'summary': recs_data.get('summary'),
            'source': recs_data.get('source'),
            'model_used': recs_data.get('model_used'),
            'recommendations': recs_data.get('recommendations', []),
        })

    messages.success(request, "L'analyse IA de capacité a été recalculée avec succès !")
    return redirect('entrepots:capacity_optimizer')
