from datetime import date, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Chauffeur(models.Model):
    """
    Modèle central pour la gestion des chauffeurs de fret et transporteurs.
    Module sous la responsabilité de Khalil Hlila (CodeCraft / CargoLink).
    Gère l'identité, le permis, les contacts, l'entreprise de transport,
    le camion attitré et l'historique complet des visites sur site.
    """

    STATUT_CHOICES = [
        ('DISPONIBLE', 'Disponible / En attente de mission'),
        ('EN_MISSION', 'En mission / Sur la route'),
        ('A_QUAI', 'À quai / Présent en entrepôt'),
        ('EN_REPOS', 'En repos réglementaire'),
        ('INACTIF', 'Inactif / Suspendu / Congé'),
    ]

    CATEGORIE_PERMIS_CHOICES = [
        ('C', 'Permis C (Poids Lourd > 3.5t)'),
        ('CE', 'Permis CE (Poids Lourd + Remorque / Semi)'),
        ('C1', 'Permis C1 (Poids Lourd Léger 3.5t - 7.5t)'),
        ('B', 'Permis B (Fourgonnette / Véhicule Utilitaire)'),
        ('D', 'Permis D (Transport en commun)'),
        ('ADR', 'Certification ADR (Marchandises Dangereuses)'),
        ('C_CE_ADR', 'Polyvalent : C + CE + Spécialisation ADR'),
    ]

    TYPE_CAMION_CHOICES = [
        ('SEMI_REMORQUE', 'Semi-remorque (40T)'),
        ('PORTEUR', 'Porteur (19T)'),
        ('FOURGON', 'Fourgon utilitaire (<3.5T)'),
        ('CITERNE', 'Camion Citerne'),
        ('FRIGORIFIQUE', 'Camion Frigorifique'),
        ('PLATEAU', 'Plateau porte-conteneur'),
    ]

    # --- 1. Informations Personnelles ---
    prenom = models.CharField(max_length=80, verbose_name="Prénom")
    nom = models.CharField(max_length=80, verbose_name="Nom de famille")
    cin = models.CharField(max_length=30, blank=True, verbose_name="Numéro CIN / Identité")
    email = models.EmailField(blank=True, verbose_name="Adresse Email")
    telephone = models.CharField(max_length=40, verbose_name="Téléphone principal")
    telephone_urgence = models.CharField(max_length=40, blank=True, verbose_name="Téléphone d'urgence")
    photo = models.ImageField(upload_to='chauffeurs/photos/', blank=True, null=True, verbose_name="Photo d'identité")
    date_naissance = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    date_embauche = models.DateField(default=date.today, verbose_name="Date d'embauche / Début d'activité")
    ville_residence = models.CharField(max_length=100, default="Tunis", verbose_name="Ville / Résidence de base")

    # --- 2. Permis de Conduire ---
    numero_permis = models.CharField(max_length=50, unique=True, verbose_name="Numéro de permis")
    categorie_permis = models.CharField(
        max_length=20,
        choices=CATEGORIE_PERMIS_CHOICES,
        default='CE',
        verbose_name="Catégorie du permis"
    )
    date_delivrance_permis = models.DateField(null=True, blank=True, verbose_name="Date de délivrance")
    date_expiration_permis = models.DateField(verbose_name="Date d'expiration / Validité")

    # --- 3. Entreprise de Transport & Rattachement ---
    entreprise_transport = models.CharField(
        max_length=150,
        default="Express Cargo Tunisie",
        verbose_name="Société / Entreprise de transport"
    )
    transporteur_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chauffeurs_assignes',
        verbose_name="Compte transporteur associé"
    )

    # --- 4. Camion Associé ---
    immatriculation_camion = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Immatriculation du camion associé"
    )
    marque_camion = models.CharField(
        max_length=80,
        blank=True,
        default="Volvo Trucks",
        verbose_name="Marque / Modèle du camion"
    )
    type_camion = models.CharField(
        max_length=30,
        choices=TYPE_CAMION_CHOICES,
        default='SEMI_REMORQUE',
        verbose_name="Type de camion habituel"
    )
    capacite_camion_tonnes = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=24.00,
        verbose_name="Capacité de charge (Tonnes)"
    )

    # --- 5. Statut & Suivi ---
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='DISPONIBLE',
        verbose_name="Statut opérationnel"
    )
    badge_acces_portuaire = models.BooleanField(
        default=True,
        verbose_name="Badge d'accès portuaire / sécurisé actif"
    )
    observations = models.TextField(blank=True, verbose_name="Remarques & Consignes particulières")

    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Enregistré le")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name = "Chauffeur"
        verbose_name_plural = "Chauffeurs"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom_complet} • {self.entreprise_transport} ({self.get_statut_display()})"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}".strip()

    @property
    def initiales(self):
        p = self.prenom[:1] if self.prenom else ""
        n = self.nom[:1] if self.nom else ""
        return (p + n).upper() or "CH"

    def get_absolute_url(self):
        return reverse('chauffeurs:chauffeur_detail', kwargs={'pk': self.pk})

    # --- Calculs de Validité du Permis ---
    @property
    def jours_avant_expiration(self):
        if not self.date_expiration_permis:
            return 999
        delta = (self.date_expiration_permis - date.today()).days
        return delta

    @property
    def est_permis_expire(self):
        return self.jours_avant_expiration < 0

    @property
    def expire_bientot(self):
        return 0 <= self.jours_avant_expiration <= 30

    @property
    def statut_validite_permis(self):
        if self.est_permis_expire:
            return 'EXPIRE'
        if self.expire_bientot:
            return 'EXPIRE_BIENTOT'
        return 'VALIDE'

    @property
    def badge_statut_css(self):
        mapping = {
            'DISPONIBLE': 'status-badge-disponible',
            'EN_MISSION': 'status-badge-mission',
            'A_QUAI': 'status-badge-quai',
            'EN_REPOS': 'status-badge-repos',
            'INACTIF': 'status-badge-inactif',
        }
        return mapping.get(self.statut, 'status-badge-inactif')

    @property
    def nb_visites(self):
        return self.visites.count()

    @property
    def derniere_visite(self):
        return self.visites.order_by('-date_visite', '-heure_arrivee').first()


class VisiteChauffeur(models.Model):
    """
    Historique des passages, contrôles et visites aux entrepôts / quais
    réalisés par un chauffeur dans le réseau CargoLink.
    """

    TYPE_OPERATION_CHOICES = [
        ('DECHARGEMENT', 'Déchargement (Réception marchandise)'),
        ('CHARGEMENT', 'Chargement (Expédition marchandise)'),
        ('CONTROLE_DOUANE', 'Contrôle Douane / Sécurité Portuaire'),
        ('RELIEVE', 'Relève d\'équipage / Stationnement'),
    ]

    STATUT_VISITE_CHOICES = [
        ('PLANIFIE', 'Visite planifiée'),
        ('ARRIVE', 'Arrivé sur le site'),
        ('A_QUAI', 'À quai en cours'),
        ('TERMINE', 'Visite achevée / Sortie validée'),
        ('ANNULE', 'Annulée'),
    ]

    chauffeur = models.ForeignKey(
        Chauffeur,
        on_delete=models.CASCADE,
        related_name='visites',
        verbose_name="Chauffeur"
    )
    entrepot = models.ForeignKey(
        'entrepots.Entrepot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visites_chauffeurs',
        verbose_name="Entrepôt visité"
    )
    creneau = models.ForeignKey(
        'creneaux.Creneau',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visites_chauffeur_associees',
        verbose_name="Créneau associé (optionnel)"
    )
    quai_numero = models.CharField(max_length=60, default="Quai Standard", verbose_name="Quai / Emplacement")
    numero_bl = models.CharField(max_length=80, blank=True, verbose_name="N° Bon de Livraison / CMR")
    type_operation = models.CharField(
        max_length=30,
        choices=TYPE_OPERATION_CHOICES,
        default='DECHARGEMENT',
        verbose_name="Type d'opération"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_VISITE_CHOICES,
        default='TERMINE',
        verbose_name="Statut du passage"
    )
    date_visite = models.DateField(default=date.today, verbose_name="Date de la visite")
    heure_arrivee = models.TimeField(null=True, blank=True, verbose_name="Heure d'entrée")
    heure_depart = models.TimeField(null=True, blank=True, verbose_name="Heure de départ")
    duree_minutes = models.PositiveIntegerField(default=45, verbose_name="Durée constatée (minutes)")
    emargement_valide = models.BooleanField(default=True, verbose_name="Émargement & signature électronique validés")
    notes = models.TextField(blank=True, verbose_name="Remarques / Contrôle d'accès")

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Visite Chauffeur"
        verbose_name_plural = "Historique des Visites"
        ordering = ['-date_visite', '-id']

    def __str__(self):
        nom_ent = self.entrepot.nom if self.entrepot else "Site Logistique"
        return f"{self.chauffeur.nom_complet} @ {nom_ent} ({self.date_visite})"
