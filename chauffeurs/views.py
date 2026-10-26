import csv
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required

from .models import Chauffeur, VisiteChauffeur
from .forms import ChauffeurForm, VisiteChauffeurForm
from creneaux.models import Creneau


def chauffeur_list(request):
    """
    R (Read List) : Liste complète des chauffeurs avec recherche,
    filtres avancés (statut, catégorie de permis, validité), et métriques KPI.
    Module sous la responsabilité de Khalil Hlila.
    """
    query = request.GET.get('q', '').strip()
    statut_filter = request.GET.get('statut', '').strip()
    categorie_filter = request.GET.get('categorie', '').strip()
    permis_alert_filter = request.GET.get('permis', '').strip()

    chauffeurs = Chauffeur.objects.annotate(
        total_visites_count=Count('visites')
    ).prefetch_related('visites')

    # Recherche multi-critères
    if query:
        chauffeurs = chauffeurs.filter(
            Q(nom__icontains=query) |
            Q(prenom__icontains=query) |
            Q(numero_permis__icontains=query) |
            Q(cin__icontains=query) |
            Q(immatriculation_camion__icontains=query) |
            Q(entreprise_transport__icontains=query) |
            Q(telephone__icontains=query) |
            Q(ville_residence__icontains=query)
        )

    # Filtre par statut opérationnel
    if statut_filter:
        chauffeurs = chauffeurs.filter(statut=statut_filter)

    # Filtre par catégorie de permis
    if categorie_filter:
        chauffeurs = chauffeurs.filter(categorie_permis=categorie_filter)

    # Filtre par alerte de validité permis
    today = date.today()
    in_30_days = today + timedelta(days=30)

    if permis_alert_filter == 'expire':
        chauffeurs = chauffeurs.filter(date_expiration_permis__lt=today)
    elif permis_alert_filter == 'bientot':
        chauffeurs = chauffeurs.filter(date_expiration_permis__gte=today, date_expiration_permis__lte=in_30_days)
    elif permis_alert_filter == 'valide':
        chauffeurs = chauffeurs.filter(date_expiration_permis__gt=in_30_days)

    # Métriques KPI globales pour le tableau de bord
    all_chauffeurs = Chauffeur.objects.all()
    total_chauffeurs = all_chauffeurs.count()
    chauffeurs_disponibles = all_chauffeurs.filter(statut='DISPONIBLE').count()
    chauffeurs_en_mission = all_chauffeurs.filter(statut='EN_MISSION').count()
    chauffeurs_a_quai = all_chauffeurs.filter(statut='A_QUAI').count()
    chauffeurs_en_repos = all_chauffeurs.filter(statut='EN_REPOS').count()

    permis_expires_count = all_chauffeurs.filter(date_expiration_permis__lt=today).count()
    permis_bientot_count = all_chauffeurs.filter(
        date_expiration_permis__gte=today,
        date_expiration_permis__lte=in_30_days
    ).count()
    permis_alertes_total = permis_expires_count + permis_bientot_count
    total_visites = VisiteChauffeur.objects.count()

    # Liste des catégories pour le filtre dropdown
    categories = Chauffeur.CATEGORIE_PERMIS_CHOICES
    statuts = Chauffeur.STATUT_CHOICES

    context = {
        'chauffeurs': chauffeurs,
        'query': query,
        'statut_filter': statut_filter,
        'categorie_filter': categorie_filter,
        'permis_alert_filter': permis_alert_filter,
        'categories': categories,
        'statuts': statuts,
        'total_chauffeurs': total_chauffeurs,
        'chauffeurs_disponibles': chauffeurs_disponibles,
        'chauffeurs_en_mission': chauffeurs_en_mission,
        'chauffeurs_a_quai': chauffeurs_a_quai,
        'chauffeurs_en_repos': chauffeurs_en_repos,
        'permis_alertes_total': permis_alertes_total,
        'permis_expires_count': permis_expires_count,
        'permis_bientot_count': permis_bientot_count,
        'total_visites': total_visites,
    }
    return render(request, 'chauffeurs/chauffeur_list.html', context)


def chauffeur_detail(request, pk):
    """
    R (Read Detail) : Fiche détaillée du chauffeur avec ses informations personnelles,
    état de son permis, camion associé, et historique complet des visites et créneaux.
    """
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    visites = chauffeur.visites.select_related('entrepot', 'creneau').order_by('-date_visite', '-id')

    # Recherche de créneaux associés par nom ou téléphone dans le module Créneaux
    creneaux_associes = Creneau.objects.filter(
        Q(chauffeur_nom__icontains=chauffeur.nom) |
        Q(immatriculation_camion__iexact=chauffeur.immatriculation_camion)
    ).select_related('quai', 'quai__entrepot').order_by('-date_creneau')[:5]

    context = {
        'chauffeur': chauffeur,
        'visites': visites,
        'creneaux_associes': creneaux_associes,
    }
    return render(request, 'chauffeurs/chauffeur_detail.html', context)


def chauffeur_create(request):
    """
    C (Create) : Ajout d'un nouveau chauffeur dans le réseau CargoLink.
    """
    if request.method == 'POST':
        form = ChauffeurForm(request.POST, request.FILES)
        if form.is_valid():
            chauffeur = form.save()
            messages.success(
                request,
                f"Le chauffeur {chauffeur.nom_complet} ({chauffeur.numero_permis}) a été enregistré avec succès !"
            )
            return redirect('chauffeurs:chauffeur_detail', pk=chauffeur.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs indiquées dans le formulaire.")
    else:
        form = ChauffeurForm()

    context = {
        'form': form,
        'action_title': "Nouveau Chauffeur",
        'button_text': "Enregistrer le Chauffeur",
    }
    return render(request, 'chauffeurs/chauffeur_form.html', context)


def chauffeur_update(request, pk):
    """
    U (Update) : Modification des informations d'un chauffeur existant.
    """
    chauffeur = get_object_or_404(Chauffeur, pk=pk)

    if request.method == 'POST':
        form = ChauffeurForm(request.POST, request.FILES, instance=chauffeur)
        if form.is_valid():
            chauffeur = form.save()
            messages.success(request, f"La fiche de {chauffeur.nom_complet} a été mise à jour.")
            return redirect('chauffeurs:chauffeur_detail', pk=chauffeur.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = ChauffeurForm(instance=chauffeur)

    context = {
        'form': form,
        'chauffeur': chauffeur,
        'action_title': f"Modifier {chauffeur.nom_complet}",
        'button_text': "Enregistrer les Modifications",
    }
    return render(request, 'chauffeurs/chauffeur_form.html', context)


def chauffeur_delete(request, pk):
    """
    D (Delete) : Suppression d'un chauffeur avec écran de confirmation.
    """
    chauffeur = get_object_or_404(Chauffeur, pk=pk)

    if request.method == 'POST':
        nom_supprime = chauffeur.nom_complet
        chauffeur.delete()
        messages.success(request, f"Le chauffeur {nom_supprime} a été supprimé avec succès.")
        return redirect('chauffeurs:chauffeur_list')

    context = {
        'chauffeur': chauffeur,
    }
    return render(request, 'chauffeurs/chauffeur_confirm_delete.html', context)


def chauffeur_statut_update(request, pk):
    """
    Mise à jour rapide du statut opérationnel en 1 clic (Disponible, En mission, À quai, En repos).
    """
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    nouveau_statut = request.POST.get('nouveau_statut') or request.GET.get('nouveau_statut')

    valid_statuts = [s[0] for s in Chauffeur.STATUT_CHOICES]
    if nouveau_statut in valid_statuts:
        chauffeur.statut = nouveau_statut
        chauffeur.save(update_fields=['statut'])
        messages.success(request, f"Statut de {chauffeur.nom_complet} changé en « {chauffeur.get_statut_display()} ».")

    next_url = request.POST.get('next') or request.GET.get('next') or 'chauffeurs:chauffeur_detail'
    if next_url == 'chauffeurs:chauffeur_detail':
        return redirect('chauffeurs:chauffeur_detail', pk=chauffeur.pk)
    return redirect(next_url)


def visite_create(request, chauffeur_pk):
    """
    Enregistre un nouveau passage ou contrôle de visite en entrepôt pour un chauffeur donné.
    """
    chauffeur = get_object_or_404(Chauffeur, pk=chauffeur_pk)

    if request.method == 'POST':
        form = VisiteChauffeurForm(request.POST)
        if form.is_valid():
            visite = form.save(commit=False)
            visite.chauffeur = chauffeur
            visite.save()
            messages.success(
                request,
                f"Visite sur le site « {visite.entrepot.nom if visite.entrepot else 'Entrepôt'} » enregistrée pour {chauffeur.nom_complet} !"
            )
            return redirect('chauffeurs:chauffeur_detail', pk=chauffeur.pk)
        else:
            messages.error(request, "Veuillez vérifier les informations de la visite.")
    else:
        form = VisiteChauffeurForm(initial={'date_visite': date.today()})

    context = {
        'form': form,
        'chauffeur': chauffeur,
        'action_title': f"Enregistrer une Visite pour {chauffeur.nom_complet}",
    }
    return render(request, 'chauffeurs/visite_form.html', context)


def chauffeur_portal_mobile(request):
    """
    Portail Chauffeur Mobile & Responsive (Conforme au slide 9).
    Offre une ergonomie optimisée pour smartphones : statut en temps réel,
    prochain créneau, bouton d'urgence et accès rapide aux quais.
    """
    chauffeurs = Chauffeur.objects.all().order_by('nom')
    chauffeur_id = request.GET.get('id')

    chauffeur_selectionne = None
    if chauffeur_id:
        chauffeur_selectionne = Chauffeur.objects.filter(pk=chauffeur_id).first()
    if not chauffeur_selectionne:
        chauffeur_selectionne = chauffeurs.first()

    prochain_creneau = None
    if chauffeur_selectionne:
        prochain_creneau = Creneau.objects.filter(
            Q(chauffeur_nom__icontains=chauffeur_selectionne.nom) |
            Q(immatriculation_camion__iexact=chauffeur_selectionne.immatriculation_camion),
            statut__in=['CONFIRME', 'ARRIVE', 'EN_COURS']
        ).first()

    context = {
        'chauffeurs': chauffeurs,
        'chauffeur': chauffeur_selectionne,
        'prochain_creneau': prochain_creneau,
    }
    return render(request, 'chauffeurs/chauffeur_portal_mobile.html', context)


def chauffeurs_export(request):
    """
    Export CSV des données chauffeurs pour reporting et tableaux de bord (Slide 8).
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="cargolink_chauffeurs_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Nom Complet', 'Téléphone', 'Email', 'CIN',
        'Numéro Permis', 'Catégorie Permis', 'Expiration Permis', 'Statut Permis',
        'Entreprise de Transport', 'Immatriculation Camion', 'Type Camion',
        'Capacité (T)', 'Statut Opérationnel', 'Nombre de Visites'
    ])

    for c in Chauffeur.objects.all().annotate(nb_v=Count('visites')):
        writer.writerow([
            c.pk,
            c.nom_complet,
            c.telephone,
            c.email or "N/A",
            c.cin or "N/A",
            c.numero_permis,
            c.get_categorie_permis_display(),
            c.date_expiration_permis,
            c.statut_validite_permis,
            c.entreprise_transport,
            c.immatriculation_camion or "N/A",
            c.get_type_camion_display(),
            c.capacite_camion_tonnes,
            c.get_statut_display(),
            c.nb_v,
        ])

    return response
