from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Entrepot(models.Model):
    """
    Modèle représentant un entrepôt logistique dans le réseau CargoLink.
    Module sous la responsabilité de Mohamed Aziz Hammami.
    """
    STATUT_CHOICES = [
        ('ACTIF', 'Opérationnel / Actif'),
        ('MAINTENANCE', 'En maintenance technique'),
        ('FERME', 'Fermé temporairement'),
    ]

    nom = models.CharField(max_length=150, verbose_name="Nom de l'entrepôt")
    code = models.CharField(max_length=30, unique=True, verbose_name="Code d'identification (ex: ENT-RADES)")
    adresse = models.CharField(max_length=255, verbose_name="Adresse")
    ville = models.CharField(max_length=100, verbose_name="Ville")
    code_postal = models.CharField(max_length=20, verbose_name="Code postal")
    telephone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone de contact")
    email_contact = models.EmailField(blank=True, verbose_name="Email de contact")
    
    # Horaires de fonctionnement
    horaire_ouverture = models.TimeField(default="06:00", verbose_name="Heure d'ouverture")
    horaire_fermeture = models.TimeField(default="22:00", verbose_name="Heure de fermeture")
    jours_ouverture = models.CharField(max_length=100, default="Lundi - Samedi", verbose_name="Jours d'ouverture")
    
    # Capacités
    capacite_palettes = models.PositiveIntegerField(default=1000, verbose_name="Capacité de stockage (Palettes)")
    superficie_m2 = models.PositiveIntegerField(default=5000, blank=True, null=True, verbose_name="Superficie (m²)")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF', verbose_name="Statut")
    
    # Responsable
    gestionnaire = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entrepots_geres',
        verbose_name="Responsable du site"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Entrepôt"
        verbose_name_plural = "Entrepôts"
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.code}) - {self.ville}"

    def get_absolute_url(self):
        return reverse('entrepots:entrepot_detail', kwargs={'pk': self.pk})

    @property
    def nb_quais(self):
        """Nombre total de quais associés à cet entrepôt."""
        return self.quais.count()

    @property
    def nb_quais_disponibles(self):
        """Nombre de quais actuellement libres."""
        return self.quais.filter(statut='DISPONIBLE').count()

    @property
    def nb_quais_occupes(self):
        """Nombre de quais actuellement en cours d'opération."""
        return self.quais.filter(statut='OCCUPE').count()

    @property
    def taux_disponibilite(self):
        """Taux de quais disponibles en pourcentage."""
        total = self.nb_quais
        if total == 0:
            return 0
        return round((self.nb_quais_disponibles / total) * 100)


class Quai(models.Model):
    """
    Modèle représentant un quai de chargement / déchargement associé à un entrepôt.
    """
    STATUT_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('OCCUPE', 'En cours d\'opération (Occupé)'),
        ('RESERVE', 'Réservé (Créneau planifié)'),
        ('MAINTENANCE', 'En maintenance technique'),
    ]

    TYPE_QUAI_CHOICES = [
        ('STANDARD', 'Standard (Sec / Marchandise Générale)'),
        ('FRIGORIFIQUE', 'Frigorifique (Température dirigée)'),
        ('ADR', 'Matières Dangereuses (ADR)'),
        ('GROS_VOLUME', 'Gros Volume / Hors-gabarit'),
        ('VRAC', 'Vrac & Palettes'),
    ]

    TYPE_CAMION_CHOICES = [
        ('TOUS', 'Tous types de véhicules'),
        ('SEMI_REMORQUE', 'Semi-remorques (38-44 tonnes)'),
        ('PORTEUR', 'Camions porteurs (19-26 tonnes)'),
        ('FOURGON', 'Fourgons / VUL (< 3.5 tonnes)'),
    ]

    entrepot = models.ForeignKey(
        Entrepot,
        on_delete=models.CASCADE,
        related_name='quais',
        verbose_name="Entrepôt rattaché"
    )
    numero = models.CharField(max_length=80, verbose_name="Numéro / Identifiant du quai (ex: Quai A-01)")
    type_quai = models.CharField(max_length=30, choices=TYPE_QUAI_CHOICES, default='STANDARD', verbose_name="Type de quai")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='DISPONIBLE', verbose_name="Statut actuel")
    
    # Spécifications opérationnelles
    capacite_camions_simultanes = models.PositiveIntegerField(default=1, verbose_name="Nombre max de camions simultanés")
    capacite_palettes_heure = models.PositiveIntegerField(default=33, verbose_name="Débit moyen (palettes / heure)")
    type_camion_accepte = models.CharField(max_length=30, choices=TYPE_CAMION_CHOICES, default='TOUS', verbose_name="Gabarit camion accepté")
    
    # Équipements techniques
    a_niveleur = models.BooleanField(default=True, verbose_name="Niveleur de quai hydraulique")
    a_sas_isotherme = models.BooleanField(default=True, verbose_name="Sas d'étanchéité isotherme")
    remarques = models.TextField(blank=True, verbose_name="Consignes d'accès & Notes d'exploitation")

    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name = "Quai de chargement"
        verbose_name_plural = "Quais de chargement"
        unique_together = ('entrepot', 'numero')
        ordering = ['entrepot', 'numero']

    def __str__(self):
        return f"{self.numero} • {self.entrepot.nom} [{self.get_statut_display()}]"

    def get_absolute_url(self):
        return reverse('entrepots:quai_detail', kwargs={'pk': self.pk})

    def occuper(self):
        """Action rapide : bascule le quai à l'état OCCUPE."""
        self.statut = 'OCCUPE'
        self.save(update_fields=['statut', 'date_modification'])

    def liberer(self):
        """Action rapide : libère le quai à l'état DISPONIBLE."""
        self.statut = 'DISPONIBLE'
        self.save(update_fields=['statut', 'date_modification'])
