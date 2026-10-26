import re
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone


class Camion(models.Model):
    """
    Modèle central pour la gestion de la flotte de camions.
    Module sous la responsabilité de Rahma (CodeCraft / CargoLink).
    Gère les caractéristiques techniques, le transporteur affilié, l'état opérationnel et la traçabilité.
    """

    TYPE_CAMION_CHOICES = [
        ('SEMI_REMORQUE', 'Semi-remorque (38-44t)'),
        ('PORTEUR', 'Camion porteur (19-26t)'),
        ('FOURGON', 'Fourgon / VUL (< 3.5t)'),
        ('FRIGORIFIQUE', 'Camion frigorifique (T° dirigée)'),
        ('CITERNE', 'Citerne liquide / Vrac'),
        ('PLATEAU', 'Plateau porte-conteneur'),
    ]

    ETAT_CHOICES = [
        ('DISPONIBLE', 'Disponible / Prêt pour mission'),
        ('EN_TRANSIT', 'En transit / Sur la route'),
        ('A_QUAI', 'À quai (Chargement / Déchargement)'),
        ('EN_MAINTENANCE', 'En maintenance / Révision technique'),
        ('HORS_SERVICE', 'Hors service / Indisponible'),
    ]

    NORME_ANTI_POLLUTION_CHOICES = [
        ('EURO_6', 'Euro VI (Norme faible émission)'),
        ('EURO_5', 'Euro V'),
        ('EURO_4', 'Euro IV'),
        ('ELECTRIQUE', '100% Électrique (Zéro émission)'),
        ('HYBRIDE', 'Hybride / Biocarburant'),
    ]

    # Identification
    immatriculation = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Immatriculation du véhicule",
        help_text="Format libre (ex: 234 TUN 5678 ou AA-123-BB)"
    )
    marque = models.CharField(max_length=60, verbose_name="Marque (ex: Volvo, Scania, Mercedes-Benz, Renault)")
    modele = models.CharField(max_length=60, verbose_name="Modèle (ex: FH16, Actros, T-High, R450)")
    annee_fabrication = models.PositiveIntegerField(
        default=2021,
        verbose_name="Année de mise en circulation"
    )

    # Gabarit et capacité
    type_camion = models.CharField(
        max_length=30,
        choices=TYPE_CAMION_CHOICES,
        default='SEMI_REMORQUE',
        verbose_name="Type / Gabarit de camion"
    )
    capacite_tonnage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=24.00,
        verbose_name="Capacité de charge utile (Tonnes)",
        help_text="Poids maximal transportable en tonnes"
    )
    volume_m3 = models.PositiveIntegerField(
        default=85,
        verbose_name="Volume utile (m³)"
    )
    capacite_palettes = models.PositiveIntegerField(
        default=33,
        verbose_name="Capacité en palettes (Standard Euro 80x120)"
    )

    # État et exploitation
    etat = models.CharField(
        max_length=25,
        choices=ETAT_CHOICES,
        default='DISPONIBLE',
        verbose_name="État opérationnel du camion"
    )
    kilometrage = models.PositiveIntegerField(
        default=85000,
        verbose_name="Kilométrage total (km)"
    )
    norme_anti_pollution = models.CharField(
        max_length=30,
        choices=NORME_ANTI_POLLUTION_CHOICES,
        default='EURO_6',
        verbose_name="Norme environnementale / Émission"
    )

    # Transporteur et rattachement
    transporteur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='camions',
        verbose_name="Compte Transporteur affilié"
    )
    societe_transport = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nom de la société de transport",
        help_text="Ex: Express Logistics, TransMed, STAF..."
    )

    # Maintenance et conformité
    date_derniere_maintenance = models.DateField(
        null=True,
        blank=True,
        verbose_name="Dernière révision effectuée"
    )
    date_prochain_controle = models.DateField(
        null=True,
        blank=True,
        verbose_name="Prochain contrôle technique obligatoire"
    )

    # Audit & horodatage
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name = "Camion"
        verbose_name_plural = "Camions"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.immatriculation} - {self.marque} {self.modele} ({self.get_type_camion_display()})"

    def clean(self):
        super().clean()
        # Normalisation immatriculation en majuscules sans espaces superflus
        if self.immatriculation:
            self.immatriculation = self.immatriculation.strip().upper()
            if len(self.immatriculation) < 4:
                raise ValidationError({
                    'immatriculation': "L'immatriculation doit comporter au moins 4 caractères valides."
                })

        # Contrôle de cohérence de charge utile
        if self.capacite_tonnage is not None and self.capacite_tonnage <= 0:
            raise ValidationError({
                'capacite_tonnage': "La capacité de charge utile doit être strictement supérieure à 0 tonne."
            })

        # Contrôle de l'année de fabrication
        current_year = date.today().year
        if self.annee_fabrication and (self.annee_fabrication < 1980 or self.annee_fabrication > current_year + 1):
            raise ValidationError({
                'annee_fabrication': f"L'année de fabrication doit être comprise entre 1980 et {current_year + 1}."
            })

        # Cohérence des dates de maintenance
        if self.date_derniere_maintenance and self.date_prochain_controle:
            if self.date_prochain_controle < self.date_derniere_maintenance:
                raise ValidationError({
                    'date_prochain_controle': "La date du prochain contrôle technique doit être postérieure à la dernière révision."
                })

    def save(self, *args, **kwargs):
        self.clean()
        # Remplissage automatique du nom de la société si le compte transporteur a une entreprise
        if self.transporteur_id and not self.societe_transport:
            try:
                from accounts.models import UserProfile
                profile = UserProfile.objects.filter(user_id=self.transporteur_id).first()
                if profile and profile.entreprise:
                    self.societe_transport = profile.entreprise
            except Exception:
                pass
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('camions:camion_detail', kwargs={'pk': self.pk})

    @property
    def badge_status_class(self):
        """Classe CSS pour les puces lumineuses de statut."""
        mapping = {
            'DISPONIBLE': 'status-disponible',
            'EN_TRANSIT': 'status-transit',
            'A_QUAI': 'status-quai',
            'EN_MAINTENANCE': 'status-maintenance',
            'HORS_SERVICE': 'status-hors-service',
        }
        return mapping.get(self.etat, 'status-default')

    @property
    def controle_technique_urgent(self):
        """Indique si le contrôle technique est dépassé ou prévu dans moins de 15 jours."""
        if not self.date_prochain_controle:
            return False
        delta = (self.date_prochain_controle - date.today()).days
        return delta <= 15

    @property
    def total_passages(self):
        return self.passages.count()


class HistoriquePassage(models.Model):
    """
    Modèle de traçabilité des passages de camions dans les entrepôts et quais CargoLink.
    Permet un suivi complet des arrivées, pesées, opérations et départs.
    """

    STATUT_CHOICES = [
        ('EN_COURS', 'Opération à quai en cours'),
        ('TERMINE', 'Passage terminé (Véhicule reparti)'),
        ('ANOMALIE', 'Anomalie / Déviation constatée'),
    ]

    TYPE_OPERATION_CHOICES = [
        ('DECHARGEMENT', 'Déchargement marchandise (Réception)'),
        ('CHARGEMENT', 'Chargement marchandise (Expédition)'),
        ('CONTROLE', 'Contrôle technique / Pesage seul'),
        ('TRANSBORDEMENT', 'Transbordement quai à quai (Cross-docking)'),
    ]

    camion = models.ForeignKey(
        Camion,
        on_delete=models.CASCADE,
        related_name='passages',
        verbose_name="Camion concerné"
    )
    entrepot = models.ForeignKey(
        'entrepots.Entrepot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='passages_camions',
        verbose_name="Site logistique / Entrepôt"
    )
    quai = models.ForeignKey(
        'entrepots.Quai',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='passages_camions',
        verbose_name="Quai d'accueil"
    )
    creneau = models.ForeignKey(
        'creneaux.Creneau',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='passages_camion',
        verbose_name="Créneau associé (si planifié)"
    )

    date_entree = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date et heure d'arrivée sur site"
    )
    date_sortie = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date et heure de sortie du site"
    )

    type_operation = models.CharField(
        max_length=25,
        choices=TYPE_OPERATION_CHOICES,
        default='DECHARGEMENT',
        verbose_name="Nature de l'opération"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_COURS',
        verbose_name="Statut du passage"
    )

    poids_mesure_kg = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Poids brut pesé au pont-bascule (kg)"
    )
    numero_bon_livraison = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="N° Bon de Livraison (BL) / CMR"
    )
    observations = models.TextField(
        blank=True,
        verbose_name="Observations / Émargement de quai"
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historique de passage"
        verbose_name_plural = "Historiques de passages"
        ordering = ['-date_entree']

    def __str__(self):
        site = self.entrepot.nom if self.entrepot else "Site externe"
        return f"Passage {self.camion.immatriculation} @ {site} le {self.date_entree.strftime('%d/%m/%Y %H:%M')}"

    @property
    def duree_minutes(self):
        """Calcule la durée de l'opération en minutes."""
        if self.date_sortie and self.date_entree:
            diff = self.date_sortie - self.date_entree
            return int(diff.total_seconds() / 60)
        return None
