import csv
from datetime import date, timedelta
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone

from .models import Chauffeur, VisiteChauffeur
from .forms import ChauffeurForm, VisiteChauffeurForm
from .ai_assistant import GeminiChauffeurAssistant
from creneaux.models import Creneau
from camions.models import Camion
from entrepots.models import Entrepot, Quai


def chauffeur_session_required(view_func):
    """
    Contrôle d'accès au module Chauffeurs (Khalil Hlila) :
    Vérifie qu'une session chauffeur (ou administrateur) est active.
    Si la session n'est pas ouverte ou que le rôle n'est pas autorisé,
    l'utilisateur est redirigé vers la page d'accueil principale ('landing').
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(
                request,
                "Accès restreint : Veuillez vous connecter avec votre session Chauffeur pour accéder à cet espace."
            )
            return redirect('landing')

        user = request.user
        user_role = getattr(getattr(user, 'profile', None), 'role', None)
        is_allowed = (
            user.is_superuser
            or user.is_staff
            or user_role in ('TRANSPORTEUR', 'ADMIN')
        )
        if not is_allowed:
            messages.error(
                request,
                "Accès refusé : Seuls les chauffeurs / transporteurs et administrateurs peuvent accéder à cet espace."
            )
            return redirect('landing')

        return view_func(request, *args, **kwargs)

    return _wrapped_view


@chauffeur_session_required
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
        'current_lang': request.GET.get('lang', '').strip() or 'fr',
    }
    return render(request, 'chauffeurs/chauffeur_list.html', context)


@chauffeur_session_required
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

    camions_disponibles = Camion.objects.filter(etat='DISPONIBLE').order_by('immatriculation')
    quais_disponibles = Quai.objects.filter(statut='DISPONIBLE').select_related('entrepot').order_by('entrepot__nom', 'numero')
    creneaux_disponibles = Creneau.objects.filter(
        quai__statut='DISPONIBLE',
        statut__in=['CONFIRME', 'EN_ATTENTE']
    ).select_related('quai', 'quai__entrepot').order_by('date_creneau', 'heure_debut')

    context = {
        'chauffeur': chauffeur,
        'visites': visites,
        'creneaux_associes': creneaux_associes,
        'camions_disponibles': camions_disponibles,
        'quais_disponibles': quais_disponibles,
        'creneaux_disponibles': creneaux_disponibles,
        'camion_actif': chauffeur.camion_associe_obj,
        'current_lang': request.GET.get('lang', '').strip() or 'fr',
    }
    return render(request, 'chauffeurs/chauffeur_detail.html', context)


@chauffeur_session_required
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
        'current_lang': request.GET.get('lang', '').strip() or 'fr',
    }
    return render(request, 'chauffeurs/chauffeur_form.html', context)


@chauffeur_session_required
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
        'current_lang': request.GET.get('lang', '').strip() or 'fr',
    }
    return render(request, 'chauffeurs/chauffeur_form.html', context)


@chauffeur_session_required
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


def _safe_redirect(next_url, chauffeur):
    """
    Redirection sécurisée garantissant la transmission du pk si la cible est chauffeur_detail.
    """
    if not next_url or next_url == 'chauffeurs:chauffeur_portal_mobile':
        return redirect('chauffeurs:chauffeur_portal_mobile')
    if next_url in ['chauffeurs:chauffeur_detail', 'chauffeur_detail']:
        return redirect('chauffeurs:chauffeur_detail', pk=chauffeur.pk)
    if next_url.startswith('/') or next_url.startswith('http'):
        return redirect(next_url)
    try:
        return redirect(next_url, pk=chauffeur.pk)
    except Exception:
        try:
            return redirect(next_url)
        except Exception:
            return redirect('chauffeurs:chauffeur_detail', pk=chauffeur.pk)


@chauffeur_session_required
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
    return _safe_redirect(next_url, chauffeur)



@chauffeur_session_required
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


@chauffeur_session_required
def chauffeur_portal_mobile(request):
    """
    Portail Chauffeur Mobile & Responsive (Conforme au slide 9).
    Offre une ergonomie optimisée pour smartphones : statut en temps réel,
    affectation camion/créneau/quai disponibles, prochain créneau et accès rapide.
    """
    chauffeurs = Chauffeur.objects.all().order_by('nom')
    chauffeur_id = request.GET.get('id')

    chauffeur_selectionne = None
    if chauffeur_id:
        chauffeur_selectionne = Chauffeur.objects.filter(pk=chauffeur_id).first()
    if not chauffeur_selectionne and request.user.is_authenticated:
        chauffeur_selectionne = (
            Chauffeur.objects.filter(transporteur_user=request.user).first()
            or Chauffeur.objects.filter(email__iexact=request.user.email).first()
            or Chauffeur.objects.filter(nom__icontains=request.user.last_name or request.user.username.split('_')[0]).first()
            or Chauffeur.objects.filter(prenom__icontains=request.user.first_name).first()
        )
    if not chauffeur_selectionne:
        chauffeur_selectionne = chauffeurs.first()

    prochain_creneau = None
    camion_actif = None
    if chauffeur_selectionne:
        prochain_creneau = Creneau.objects.filter(
            Q(chauffeur_nom__icontains=chauffeur_selectionne.nom) |
            Q(immatriculation_camion__iexact=chauffeur_selectionne.immatriculation_camion),
            statut__in=['CONFIRME', 'ARRIVE', 'EN_COURS', 'EN_ATTENTE']
        ).select_related('quai', 'quai__entrepot').order_by('-date_creneau').first()
        camion_actif = chauffeur_selectionne.camion_associe_obj

    camions_disponibles = Camion.objects.filter(etat='DISPONIBLE').order_by('immatriculation')
    quais_disponibles = Quai.objects.filter(statut='DISPONIBLE').select_related('entrepot').order_by('entrepot__nom', 'numero')
    creneaux_disponibles = Creneau.objects.filter(
        quai__statut='DISPONIBLE',
        statut__in=['CONFIRME', 'EN_ATTENTE']
    ).select_related('quai', 'quai__entrepot').order_by('date_creneau', 'heure_debut')

    context = {
        'chauffeurs': chauffeurs,
        'chauffeur': chauffeur_selectionne,
        'prochain_creneau': prochain_creneau,
        'camion_actif': camion_actif,
        'camions_disponibles': camions_disponibles,
        'quais_disponibles': quais_disponibles,
        'creneaux_disponibles': creneaux_disponibles,
    }
    return render(request, 'chauffeurs/chauffeur_portal_mobile.html', context)


@chauffeur_session_required
def chauffeur_affecter_mission(request, pk):
    """
    Affecte un chauffeur à un camion disponible et à un créneau sur quai disponible.
    Règles de validation :
    1. Le camion sélectionné DOIT être DISPONIBLE.
    2. Le quai sélectionné DOIT être DISPONIBLE.
    3. Le créneau sélectionné DOIT être sur un quai disponible (ou créé directement sur le quai libre).
    """
    chauffeur = get_object_or_404(Chauffeur, pk=pk)

    if request.method == 'POST':
        camion_id = request.POST.get('camion_id')
        quai_id = request.POST.get('quai_id')
        creneau_id = request.POST.get('creneau_id')
        type_op = request.POST.get('type_operation') or 'DECHARGEMENT'

        next_url = request.POST.get('next') or request.GET.get('next') or 'chauffeurs:chauffeur_portal_mobile'

        # 1. Vérification Camion Disponible
        camion = Camion.objects.filter(pk=camion_id).first()
        if not camion:
            messages.error(request, "Veuillez sélectionner un camion valide.")
            return _safe_redirect(next_url, chauffeur)

        if camion.etat != 'DISPONIBLE' and camion.immatriculation != chauffeur.immatriculation_camion:
            messages.error(
                request,
                f"Le camion {camion.immatriculation} n'est pas disponible (État actuel : {camion.get_etat_display()}). "
                f"Seul un camion disponible peut être affecté."
            )
            return _safe_redirect(next_url, chauffeur)

        # 2. Vérification Quai Disponible
        quai = Quai.objects.filter(pk=quai_id).select_related('entrepot').first()
        if not quai:
            messages.error(request, "Veuillez sélectionner un quai logistique valide.")
            return _safe_redirect(next_url, chauffeur)

        if quai.statut != 'DISPONIBLE':
            messages.error(
                request,
                f"Le quai {quai.numero} ({quai.entrepot.nom}) n'est pas disponible (Statut : {quai.get_statut_display()}). "
                f"Veuillez choisir un quai libre."
            )
            return _safe_redirect(next_url, chauffeur)

        # 3. Récupération ou création du créneau disponible
        creneau = None
        if creneau_id:
            creneau = Creneau.objects.filter(pk=creneau_id).first()
            if not creneau or creneau.statut in ['ANNULE', 'TERMINE']:
                messages.error(request, "Le créneau sélectionné n'est plus disponible.")
                return _safe_redirect(next_url, chauffeur)
            if creneau.quai_id != quai.id:
                creneau.quai = quai
                creneau.entrepot = quai.entrepot
        else:
            today = date.today()
            now = timezone.localtime().time()
            heure_fin = (timezone.localtime() + timedelta(hours=2)).time()
            creneau = Creneau.objects.create(
                entrepot=quai.entrepot,
                quai=quai,
                demandeur=request.user,
                date_creneau=today,
                heure_debut=now,
                heure_fin=heure_fin,
                type_operation=type_op,
                statut='CONFIRME',
                transporteur_nom=chauffeur.entreprise_transport,
                immatriculation_camion=camion.immatriculation,
                type_camion=camion.type_camion,
                chauffeur_nom=chauffeur.nom_complet,
                chauffeur_telephone=chauffeur.telephone,
                nb_palettes=15,
                consignes=f"Affectation opérationnelle directe du chauffeur {chauffeur.nom_complet} avec {camion.immatriculation}"
            )

        # 4. Affectation sur le Chauffeur
        chauffeur.immatriculation_camion = camion.immatriculation
        chauffeur.marque_camion = f"{camion.marque} {camion.modele}"
        chauffeur.type_camion = camion.type_camion
        chauffeur.capacite_camion_tonnes = camion.capacite_tonnage
        chauffeur.statut = 'EN_MISSION'
        chauffeur.save(update_fields=['immatriculation_camion', 'marque_camion', 'type_camion', 'capacite_camion_tonnes', 'statut'])

        # 5. Mise à jour de l'état du Camion
        camion.etat = 'EN_TRANSIT'
        camion.save(update_fields=['etat'])

        # 6. Mise à jour du Créneau
        creneau.chauffeur_nom = chauffeur.nom_complet
        creneau.chauffeur_telephone = chauffeur.telephone
        creneau.immatriculation_camion = camion.immatriculation
        creneau.transporteur_nom = chauffeur.entreprise_transport
        creneau.statut = 'CONFIRME'
        creneau.save()

        # 7. Création de la visite d'accès quai
        VisiteChauffeur.objects.create(
            chauffeur=chauffeur,
            entrepot=quai.entrepot,
            quai_numero=quai.numero,
            creneau=creneau,
            type_operation=creneau.type_operation,
            statut='PLANIFIE',
            date_visite=creneau.date_creneau,
            heure_arrivee=creneau.heure_debut,
            notes=f"Affectation réussie : Camion {camion.immatriculation} • Quai {quai.numero} ({quai.entrepot.nom}) • Créneau {creneau.reference}"
        )

        messages.success(
            request,
            f"Affectation réussie ! {chauffeur.nom_complet} est affecté au camion disponible {camion.immatriculation} "
            f"pour le créneau {creneau.reference} sur le {quai.numero} ({quai.entrepot.nom})."
        )

    return _safe_redirect(next_url, chauffeur)


@chauffeur_session_required
def chauffeur_liberer_mission(request, pk):
    """
    Libère l'affectation active du chauffeur : remet le camion en DISPONIBLE,
    clôture le créneau et rend le quai DISPONIBLE.
    """
    chauffeur = get_object_or_404(Chauffeur, pk=pk)
    next_url = request.POST.get('next') or request.GET.get('next') or 'chauffeurs:chauffeur_portal_mobile'

    # 1. Rendre le camion disponible
    immat = chauffeur.immatriculation_camion
    if immat:
        camion = Camion.objects.filter(immatriculation__iexact=immat).first()
        if camion:
            camion.etat = 'DISPONIBLE'
            camion.save(update_fields=['etat'])

    # 2. Clôturer les créneaux actifs
    creneaux_actifs = Creneau.objects.filter(
        Q(chauffeur_nom__icontains=chauffeur.nom) |
        Q(immatriculation_camion__iexact=immat),
        statut__in=['CONFIRME', 'ARRIVE', 'EN_COURS', 'EN_ATTENTE']
    )
    for cr in creneaux_actifs:
        cr.statut = 'TERMINE'
        cr.save(update_fields=['statut'])
        if cr.quai and cr.quai.statut != 'DISPONIBLE':
            cr.quai.statut = 'DISPONIBLE'
            cr.quai.save(update_fields=['statut'])

    # 3. Remettre le chauffeur en Disponible
    chauffeur.statut = 'DISPONIBLE'
    chauffeur.save(update_fields=['statut'])

    messages.info(
        request,
        f"Mission libérée avec succès pour {chauffeur.nom_complet}. "
        f"Le camion ({immat or 'N/A'}) et le quai sont de nouveau DISPONIBLES."
    )
    return _safe_redirect(next_url, chauffeur)


@chauffeur_session_required
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


@chauffeur_session_required
def chauffeur_ai_assistant(request):
    """
    Interface visuelle de l'Assistant Conversationnel IA pour les Chauffeurs (Option 4).
    Recherche en langage naturel, gestion des permis et historique multi-langues (FR, AR, EN).
    """
    api_key_configured = bool(getattr(settings, 'GEMINI_API_KEY', ''))

    chauffeurs = Chauffeur.objects.annotate(visites_count=Count('visites')).all()
    total_chauffeurs = chauffeurs.count()
    chauffeurs_disponibles_count = chauffeurs.filter(statut='DISPONIBLE').count()
    permis_expires_count = len([c for c in chauffeurs if c.est_permis_expire])
    permis_expire_bientot_count = len([c for c in chauffeurs if c.expire_bientot])

    top_chauffeur = chauffeurs.order_by('-visites_count').first()

    context = {
        'api_key_configured': api_key_configured,
        'total_chauffeurs': total_chauffeurs,
        'chauffeurs_disponibles_count': chauffeurs_disponibles_count,
        'permis_expires_count': permis_expires_count,
        'permis_expire_bientot_count': permis_expire_bientot_count,
        'top_chauffeur': top_chauffeur,
        'chauffeurs_list': chauffeurs.order_by('nom'),
    }
    return render(request, 'chauffeurs/ai_assistant.html', context)


@csrf_exempt
@chauffeur_session_required
def chauffeur_ai_chat_api(request):
    """
    Endpoint AJAX pour l'Assistant Conversationnel IA des Chauffeurs.
    Supporte les requêtes en français, arabe et anglais.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode POST requise'}, status=405)

    prompt = request.POST.get('prompt', '').strip()
    lang = request.POST.get('lang', 'fr').strip() or 'fr'
    api_key = request.POST.get('api_key', '').strip() or None

    if not prompt:
        return JsonResponse({'error': 'Veuillez saisir votre question.'}, status=400)

    assistant = GeminiChauffeurAssistant(api_key=api_key)
    result = assistant.ask(prompt, lang=lang, user=request.user)
    return JsonResponse(result)

