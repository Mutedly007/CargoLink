import csv
from datetime import datetime, date, time, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count
from django.urls import reverse

from .models import Creneau, HistoriqueStatutCreneau
from .forms import CreneauForm, DemandeCreneauForm, AnnulationCreneauForm
from entrepots.models import Entrepot, Quai


# ==============================================================================
# TABLEAU DE BORD & LISTE DES CRÉNEAUX
# ==============================================================================

def creneau_list(request):
    """
    Vue principale : Liste des créneaux, indicateurs KPI et filtres multi-critères.
    """
    today = date.today()
    date_filter = request.GET.get('date', '').strip()
    statut_filter = request.GET.get('statut', '').strip()
    entrepot_filter = request.GET.get('entrepot', '').strip()
    type_op_filter = request.GET.get('type_op', '').strip()
    query = request.GET.get('q', '').strip()

    creneaux = Creneau.objects.select_related('entrepot', 'quai', 'demandeur').all()

    # Filtre par recherche textuelle
    if query:
        creneaux = creneaux.filter(
            Q(reference__icontains=query) |
            Q(transporteur_nom__icontains=query) |
            Q(immatriculation_camion__icontains=query) |
            Q(chauffeur_nom__icontains=query) |
            Q(numero_bl__icontains=query)
        )

    # Filtre date
    if date_filter:
        try:
            target_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            creneaux = creneaux.filter(date_creneau=target_date)
        except ValueError:
            pass

    # Filtre statut
    if statut_filter:
        creneaux = creneaux.filter(statut=statut_filter)

    # Filtre entrepôt
    if entrepot_filter:
        creneaux = creneaux.filter(entrepot_id=entrepot_filter)

    # Filtre type opération
    if type_op_filter:
        creneaux = creneaux.filter(type_operation=type_op_filter)

    # Métriques KPI
    all_creneaux = Creneau.objects.all()
    creneaux_du_jour = all_creneaux.filter(date_creneau=today)
    
    total_creneaux = all_creneaux.count()
    total_aujourdhui = creneaux_du_jour.count()
    en_attente_count = all_creneaux.filter(statut='EN_ATTENTE').count()
    en_cours_count = all_creneaux.filter(statut='EN_COURS').count()
    termines_count = all_creneaux.filter(statut='TERMINE').count()
    confirme_count = all_creneaux.filter(statut='CONFIRME').count()

    entrepots = Entrepot.objects.all().order_by('nom')

    context = {
        'creneaux': creneaux,
        'today': today,
        'date_filter': date_filter,
        'statut_filter': statut_filter,
        'entrepot_filter': entrepot_filter,
        'type_op_filter': type_op_filter,
        'query': query,
        'entrepots': entrepots,
        'statut_choices': Creneau.STATUT_CHOICES,
        'type_op_choices': Creneau.TYPE_OPERATION_CHOICES,
        # KPIs
        'total_creneaux': total_creneaux,
        'total_aujourdhui': total_aujourdhui,
        'en_attente_count': en_attente_count,
        'en_cours_count': en_cours_count,
        'termines_count': termines_count,
        'confirme_count': confirme_count,
    }
    return render(request, 'creneaux/creneau_list.html', context)


# ==============================================================================
# PLANNING VISUEL (TIMELINE HORAIRE DES QUAIS)
# ==============================================================================

def creneau_planning(request):
    """
    Vue Planning / Grille horaire : Visualisation de l'occupation des quais par heure
    pour une journée donnée et un entrepôt spécifique.
    """
    today = date.today()
    selected_date_str = request.GET.get('date', today.strftime('%Y-%m-%d'))
    selected_entrepot_id = request.GET.get('entrepot', '')

    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today

    entrepots = Entrepot.objects.all().order_by('nom')
    current_entrepot = None

    if selected_entrepot_id:
        current_entrepot = entrepots.filter(id=selected_entrepot_id).first()
    if not current_entrepot and entrepots.exists():
        current_entrepot = entrepots.first()

    quais_data = []
    # Tranches horaires de 06:00 à 21:00
    heures = [f"{h:02d}:00" for h in range(6, 22)]

    if current_entrepot:
        quais = current_entrepot.quais.all().order_by('numero')
        creneaux_jour = Creneau.objects.filter(
            entrepot=current_entrepot,
            date_creneau=selected_date
        ).exclude(statut='ANNULE').select_related('quai')

        for quai in quais:
            quai_creneaux = [c for c in creneaux_jour if c.quai_id == quai.id]
            quais_data.append({
                'quai': quai,
                'creneaux': quai_creneaux
            })

    # Navigation date précédente / suivante
    prev_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)

    context = {
        'entrepots': entrepots,
        'current_entrepot': current_entrepot,
        'selected_date': selected_date,
        'prev_date': prev_date,
        'next_date': next_date,
        'quais_data': quais_data,
        'heures': heures,
    }
    return render(request, 'creneaux/creneau_planning.html', context)


# ==============================================================================
# CRÉATION & DEMANDE DE CRÉNEAU
# ==============================================================================

def creneau_create(request):
    """
    Création directe d'un créneau (pour les gestionnaires d'entrepôt et planificateurs).
    """
    entrepot_id = request.GET.get('entrepot') or None
    quai_id = request.GET.get('quai') or None

    if request.method == 'POST':
        form = CreneauForm(request.POST)
        if form.is_valid():
            creneau = form.save(commit=False)
            if request.user.is_authenticated:
                creneau.demandeur = request.user
            # Par défaut, création directe = CONFIRME
            creneau.statut = 'CONFIRME'
            creneau.save()
            creneau._enregistrer_historique('CONFIRME', request.user, "Créneau créé directement par le gestionnaire.")
            messages.success(request, f"Créneau {creneau.reference} planifié avec succès pour le quai {creneau.quai.numero} !")
            return redirect('creneaux:creneau_detail', pk=creneau.pk)
    else:
        initial = {}
        if entrepot_id:
            initial['entrepot'] = entrepot_id
        if quai_id:
            initial['quai'] = quai_id
        form = CreneauForm(initial=initial, entrepot_id=entrepot_id)

    return render(request, 'creneaux/creneau_form.html', {
        'form': form,
        'title': "Planifier un nouveau créneau",
        'subtitle': "Assignation directe d'un créneau horaire sur un quai logistique",
        'action_label': "Enregistrer le créneau"
    })


def demande_creneau(request):
    """
    Demande de créneau (Module Kacem - Slide 16 : 'Demande de créneau').
    Enregistre une sollicitation de créneau horaire à l'état EN_ATTENTE pour arbitrage.
    """
    if request.method == 'POST':
        form = DemandeCreneauForm(request.POST)
        if form.is_valid():
            creneau = form.save(commit=False)
            if request.user.is_authenticated:
                creneau.demandeur = request.user
            creneau.statut = 'EN_ATTENTE'
            creneau.save()
            creneau._enregistrer_historique('EN_ATTENTE', request.user, "Demande de créneau enregistrée. En attente de confirmation.")
            messages.success(
                request,
                f"Votre demande de créneau (Réf: {creneau.reference}) a été enregistrée avec succès ! "
                f"Elle est actuellement en attente de vérification et confirmation par le gestionnaire."
            )
            return redirect('creneaux:creneau_detail', pk=creneau.pk)
    else:
        form = DemandeCreneauForm()

    return render(request, 'creneaux/demande_creneau.html', {
        'form': form,
        'title': "Demande de Créneau Horaire",
        'subtitle': "Solliciter un créneau d'intervention sur quai logistique (chargement ou déchargement)",
        'action_label': "Transmettre la demande de créneau"
    })


def creneau_confirm(request, pk):
    """
    Confirmation de créneau (Module Kacem - Slide 16 : 'Confirmation').
    Valide un créneau en attente et l'intègre définitivement au planning des quais.
    """
    creneau = get_object_or_404(Creneau, pk=pk)
    creneau.confirmer(user=request.user)
    messages.success(request, f"Le créneau {creneau.reference} a été confirmé et validé au planning !")
    return redirect('creneaux:creneau_detail', pk=creneau.pk)


# ==============================================================================
# DÉTAIL D'UN CRÉNEAU & ACTIONS DE STATUT
# ==============================================================================

def creneau_detail(request, pk):
    """
    Fiche détaillée d'un créneau : informations complètes, timeline d'état,
    historique des jalons et actions de transition en direct.
    """
    creneau = get_object_or_404(
        Creneau.objects.select_related('entrepot', 'quai', 'demandeur').prefetch_related('historique'),
        pk=pk
    )
    return render(request, 'creneaux/creneau_detail.html', {'creneau': creneau})


def creneau_update(request, pk):
    """
    Modification d'un créneau existant.
    """
    creneau = get_object_or_404(Creneau, pk=pk)

    if request.method == 'POST':
        form = CreneauForm(request.POST, instance=creneau)
        if form.is_valid():
            creneau = form.save()
            creneau._enregistrer_historique(creneau.statut, request.user, "Détails du créneau modifiés.")
            messages.success(request, f"Le créneau {creneau.reference} a été mis à jour.")
            return redirect('creneaux:creneau_detail', pk=creneau.pk)
    else:
        form = CreneauForm(instance=creneau)

    return render(request, 'creneaux/creneau_form.html', {
        'form': form,
        'creneau': creneau,
        'title': f"Modifier le créneau {creneau.reference}",
        'subtitle': f"Ajustement des horaires, du quai ou des informations du camion",
        'action_label': "Enregistrer les modifications"
    })


def creneau_cancel(request, pk):
    """
    Annulation motivée d'un créneau.
    """
    creneau = get_object_or_404(Creneau, pk=pk)

    if request.method == 'POST':
        form = AnnulationCreneauForm(request.POST)
        if form.is_valid():
            motif = form.cleaned_data['motif_annulation']
            creneau.annuler(motif=motif, user=request.user)
            messages.warning(request, f"Le créneau {creneau.reference} a été annulé.")
            return redirect('creneaux:creneau_detail', pk=creneau.pk)
    else:
        form = AnnulationCreneauForm()

    return render(request, 'creneaux/creneau_confirm_cancel.html', {
        'creneau': creneau,
        'form': form
    })


def creneau_action_statut(request, pk, action):
    """
    Transitions d'état en 1 clic pour le suivi opérationnel en temps réel (Slide 8).
    Actions disponibles: confirmer, arriver, mettre_a_quai, terminer.
    """
    creneau = get_object_or_404(Creneau, pk=pk)

    if action == 'confirmer':
        creneau.confirmer(user=request.user)
        messages.success(request, f"Créneau {creneau.reference} confirmé et validé au planning !")
    elif action == 'arriver':
        creneau.marquer_arrive(user=request.user)
        messages.info(request, f"Camion {creneau.immatriculation_camion} enregistré comme arrivé sur le site.")
    elif action == 'mettre_a_quai':
        creneau.mettre_a_quai(user=request.user)
        messages.success(request, f"Camion mis à quai ({creneau.quai.numero}). Début des opérations !")
    elif action == 'terminer':
        creneau.terminer(user=request.user)
        messages.success(request, f"Opération terminée avec succès. Le quai {creneau.quai.numero} est de nouveau libre !")
    else:
        messages.error(request, "Action non reconnue.")

    return redirect('creneaux:creneau_detail', pk=creneau.pk)


# ==============================================================================
# EXPORT DES CRÉNEAUX (CSV / EXCEL)
# ==============================================================================

def creneau_export_csv(request):
    """
    Export CSV des créneaux selon les filtres courants pour rapports logistiques.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="cargolink_creneaux_{date.today().strftime("%Y%m%d")}.csv"'
    
    # UTF-8 BOM pour compatibilité avec Microsoft Excel
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Référence', 'Date', 'Début', 'Fin', 'Entrepôt', 'Quai',
        'Opération', 'Statut', 'Transporteur', 'Camion', 'Chauffeur',
        'Téléphone', 'Marchandise', 'Nb Palettes', 'N° BL'
    ])

    creneaux = Creneau.objects.select_related('entrepot', 'quai').all()

    for c in creneaux:
        writer.writerow([
            c.reference,
            c.date_creneau.strftime('%d/%m/%Y'),
            c.heure_debut.strftime('%H:%M'),
            c.heure_fin.strftime('%H:%M'),
            c.entrepot.nom,
            c.quai.numero,
            c.get_type_operation_display(),
            c.get_statut_display(),
            c.transporteur_nom,
            c.immatriculation_camion,
            c.chauffeur_nom,
            c.chauffeur_telephone,
            c.get_type_marchandise_display(),
            c.nb_palettes,
            c.numero_bl or ''
        ])

    return response


# ==============================================================================
# API HELPER (AJAX pour filtrage des quais par entrepôt)
# ==============================================================================

def api_quais_by_entrepot(request, entrepot_id):
    """
    Retourne la liste JSON des quais d'un entrepôt donné pour alimenter dynamiquement les selects.
    """
    quais = Quai.objects.filter(entrepot_id=entrepot_id).values('id', 'numero', 'type_quai', 'statut')
    return JsonResponse({'quais': list(quais)})


def api_ai_recommend_dock(request):
    """
    Endpoint AJAX d'Attribution Intelligente des Quais par IA (Module Kacem - Volet IA).
    Calcule le quai optimal en fonction du débit, du gabarit, de la marchandise et de l'équilibrage de charge.
    """
    from .ai_optimizer import SmartDockAllocator

    entrepot_id = request.GET.get('entrepot_id') or request.POST.get('entrepot_id')
    date_str = request.GET.get('date') or request.POST.get('date')
    heure_debut_str = request.GET.get('heure_debut') or request.POST.get('heure_debut')
    heure_fin_str = request.GET.get('heure_fin') or request.POST.get('heure_fin')
    type_marchandise = request.GET.get('type_marchandise') or request.POST.get('type_marchandise') or 'STANDARD'
    type_camion = request.GET.get('type_camion') or request.POST.get('type_camion') or 'SEMI_REMORQUE'
    nb_palettes = request.GET.get('nb_palettes') or request.POST.get('nb_palettes') or 10

    if not entrepot_id or not date_str or not heure_debut_str or not heure_fin_str:
        return JsonResponse({
            'success': False,
            'message': "Veuillez d'abord sélectionner l'entrepôt, la date et les horaires pour permettre à l'IA d'analyser la disponibilité des quais."
        })

    try:
        date_creneau = datetime.strptime(date_str, '%Y-%m-%d').date()
        h1 = datetime.strptime(heure_debut_str, '%H:%M').time()
        h2 = datetime.strptime(heure_fin_str, '%H:%M').time()
        nb_pal = int(nb_palettes)
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': f"Format de données invalide : {str(e)}"
        })

    allocator = SmartDockAllocator()
    result = allocator.recommend_best_dock(
        entrepot_id=int(entrepot_id),
        date_creneau=date_creneau,
        heure_debut=h1,
        heure_fin=h2,
        type_marchandise=type_marchandise,
        type_camion=type_camion,
        nb_palettes=nb_pal
    )

    return JsonResponse(result)
