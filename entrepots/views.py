from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from .models import Entrepot, Quai
from .forms import EntrepotForm, QuaiForm


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
        'page_title': f"{entrepot.nom} • Détails Entrepôt",
    }
    return render(request, 'entrepots/entrepot_detail.html', context)


@login_required
def entrepot_create(request):
    """
    C (Create) : Formulaire d'ajout d'un nouvel entrepôt.
    """
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
    """
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
    """
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
        'page_title': "Régulation des Quais • CargoLink",
    }
    return render(request, 'entrepots/quai_list.html', context)


def quai_detail(request, pk):
    """
    R (Read Detail) : Fiche technique et état opérationnel d'un quai.
    """
    quai = get_object_or_404(Quai.objects.select_related('entrepot'), pk=pk)
    return render(request, 'entrepots/quai_detail.html', {'quai': quai, 'page_title': f"{quai.numero} • Fiche Quai"})


@login_required
def quai_create(request, entrepot_pk=None):
    """
    C (Create) : Ajout d'un quai, optionnellement pré-attaché à un entrepôt.
    """
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
    """
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
    """
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
    """
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
