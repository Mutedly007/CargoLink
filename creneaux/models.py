import uuid
from datetime import datetime, date, time, timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from entrepots.models import Entrepot, Quai


class Creneau(models.Model):
    """
    Modèle central pour la gestion des créneaux de chargement et déchargement aux quais.
    Module sous la responsabilité de Kacem (CodeCraft / CargoLink).
    Gère la demande, planification, détection de conflits, contrôle horaire et suivi en temps réel.
    """

    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente de validation'),
        ('CONFIRME', 'Confirmé / Planifié'),
        ('ARRIVE', 'Camion arrivé sur site'),
        ('EN_COURS', 'À quai (Opération en cours)'),
        ('TERMINE', 'Opération terminée (Libéré)'),
        ('EN_RETARD', 'En retard'),
        ('ANNULE', 'Annulé'),
    ]

    TYPE_OPERATION_CHOICES = [
        ('DECHARGEMENT', 'Déchargement (Réception marchandise)'),
        ('CHARGEMENT', 'Chargement (Expédition marchandise)'),
    ]

    PRIORITE_CHOICES = [
        ('NORMALE', 'Normale'),
        ('URGENTE', 'Priorité Haute / Urgente'),
        ('FLEXIBLE', 'Flexible'),
    ]

    TYPE_CAMION_CHOICES = [
        ('SEMI_REMORQUE', 'Semi-remorque (38-44 tonnes)'),
        ('PORTEUR', 'Camion porteur (19-26 tonnes)'),
        ('FOURGON', 'Fourgon / VUL (< 3.5 tonnes)'),
        ('AUTRE', 'Autre gabarit spécial'),
    ]

    TYPE_MARCHANDISE_CHOICES = [
        ('STANDARD', 'Marchandise générale / Sec'),
        ('FRIGORIFIQUE', 'Température dirigée (Frais / Surgelé)'),
        ('ADR', 'Matières dangereuses (ADR)'),
        ('GROS_VOLUME', 'Gros volume / Hors gabarit'),
        ('PALETTES', 'Palettes standardisées'),
    ]

    # Identification
    reference = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name="Référence unique du créneau"
    )

    # Rattachement infrastructure
    entrepot = models.ForeignKey(
        Entrepot,
        on_delete=models.CASCADE,
        related_name='creneaux',
        verbose_name="Entrepôt"
    )
    quai = models.ForeignKey(
        Quai,
        on_delete=models.CASCADE,
        related_name='creneaux',
        verbose_name="Quai assigné"
    )
    demandeur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='creneaux_demandes',
        verbose_name="Demandeur / Planificateur"
    )

    # Paramètres temporels
    date_creneau = models.DateField(verbose_name="Date du créneau")
    heure_debut = models.TimeField(verbose_name="Heure de début prévue")
    heure_fin = models.TimeField(verbose_name="Heure de fin prévue")

    # Type et état
    type_operation = models.CharField(
        max_length=20,
        choices=TYPE_OPERATION_CHOICES,
        default='DECHARGEMENT',
        verbose_name="Type d'opération"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE',
        verbose_name="Statut du créneau"
    )
    priorite = models.CharField(
        max_length=20,
        choices=PRIORITE_CHOICES,
        default='NORMALE',
        verbose_name="Niveau de priorité"
    )

    # Informations Chauffeur & Camion
    transporteur_nom = models.CharField(max_length=150, verbose_name="Société de transport / Transporteur")
    immatriculation_camion = models.CharField(max_length=40, verbose_name="Immatriculation du véhicule")
    type_camion = models.CharField(
        max_length=30,
        choices=TYPE_CAMION_CHOICES,
        default='SEMI_REMORQUE',
        verbose_name="Type / Gabarit camion"
    )
    chauffeur_nom = models.CharField(max_length=150, verbose_name="Nom du chauffeur")
    chauffeur_telephone = models.CharField(max_length=40, blank=True, verbose_name="Téléphone chauffeur")

    # Informations Fret & Marchandise
    type_marchandise = models.CharField(
        max_length=30,
        choices=TYPE_MARCHANDISE_CHOICES,
        default='STANDARD',
        verbose_name="Type de marchandise"
    )
    nb_palettes = models.PositiveIntegerField(default=10, verbose_name="Nombre de palettes")
    poids_kg = models.PositiveIntegerField(blank=True, null=True, verbose_name="Poids estimé (kg)")
    numero_bl = models.CharField(max_length=80, blank=True, verbose_name="N° Bon de Livraison / Lettre de voiture (CMR)")
    consignes = models.TextField(blank=True, verbose_name="Consignes spécifiques d'exploitation")
    motif_annulation = models.TextField(blank=True, verbose_name="Motif d'annulation")

    # Horodatage opérationnel en temps réel
    heure_arrivee_reelle = models.DateTimeField(null=True, blank=True, verbose_name="Arrivée constatée")
    heure_debut_operation = models.DateTimeField(null=True, blank=True, verbose_name="Début effectif à quai")
    heure_fin_operation = models.DateTimeField(null=True, blank=True, verbose_name="Fin effective & départ")

    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Créneau horaire"
        verbose_name_plural = "Créneaux horaires"
        ordering = ['date_creneau', 'heure_debut']
        indexes = [
            models.Index(fields=['date_creneau', 'quai']),
            models.Index(fields=['statut']),
            models.Index(fields=['reference']),
        ]

    def __str__(self):
        return f"{self.reference or 'Créneau'} • {self.quai.numero} ({self.date_creneau} {self.heure_debut.strftime('%H:%M')}-{self.heure_fin.strftime('%H:%M')}) [{self.get_statut_display()}]"

    def get_absolute_url(self):
        return reverse('creneaux:creneau_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # Générer automatiquement une référence élégante si inexistante
        if not self.reference:
            prefix = "CRN"
            date_str = self.date_creneau.strftime("%Y%m%d") if self.date_creneau else datetime.now().strftime("%Y%m%d")
            uid = uuid.uuid4().hex[:5].upper()
            self.reference = f"{prefix}-{date_str}-{uid}"
        super().save(*args, **kwargs)

    def clean(self):
        """
        Vérification des disponibilités et prévention des conflits (Besoins fonctionnels Slide 8 & 9).
        1. Cohérence horaire (début < fin)
        2. Respect des horaires de fonctionnement de l'entrepôt
        3. Quai rattaché à l'entrepôt
        4. Compatibilité technique quai / marchandise
        5. Détection de conflits / chevauchements sur le même quai
        """
        super().clean()
        errors = {}

        if self.heure_debut and self.heure_fin:
            if self.heure_debut >= self.heure_fin:
                errors['heure_fin'] = "L'heure de fin doit être postérieure à l'heure de début."

        # Vérifier que le quai appartient bien à l'entrepôt
        if self.entrepot and self.quai:
            if self.quai.entrepot_id != self.entrepot.id:
                errors['quai'] = f"Le quai {self.quai.numero} n'appartient pas à l'entrepôt sélectionné ({self.entrepot.nom})."

        # Vérifier les horaires de l'entrepôt
        if self.entrepot and self.heure_debut and self.heure_fin:
            if self.entrepot.horaire_ouverture and self.heure_debut < self.entrepot.horaire_ouverture:
                errors['heure_debut'] = (
                    f"L'heure de début ({self.heure_debut.strftime('%H:%M')}) est antérieure à l'ouverture de "
                    f"l'entrepôt ({self.entrepot.horaire_ouverture.strftime('%H:%M')})."
                )
            if self.entrepot.horaire_fermeture and self.heure_fin > self.entrepot.horaire_fermeture:
                errors['heure_fin'] = (
                    f"L'heure de fin ({self.heure_fin.strftime('%H:%M')}) dépasse l'heure de fermeture de "
                    f"l'entrepôt ({self.entrepot.horaire_fermeture.strftime('%H:%M')})."
                )

        # Vérifier compatibilité marchandise / quai
        if self.quai and self.type_marchandise:
            if self.type_marchandise == 'FRIGORIFIQUE' and self.quai.type_quai != 'FRIGORIFIQUE':
                errors['type_marchandise'] = (
                    f"Le quai {self.quai.numero} n'est pas équipé pour la température dirigée (Type: {self.quai.get_type_quai_display()}). "
                    f"Veuillez choisir un quai frigorifique."
                )
            if self.type_marchandise == 'ADR' and self.quai.type_quai != 'ADR':
                errors['type_marchandise'] = (
                    f"Le quai {self.quai.numero} n'est pas habilité pour les matières dangereuses (ADR). "
                    f"Veuillez choisir un quai ADR."
                )

        # Prévention des conflits : aucun chevauchement sur le même quai pour la même date
        if self.quai and self.date_creneau and self.heure_debut and self.heure_fin:
            # Créneaux actifs pouvant entrer en conflit
            conflits = Creneau.objects.filter(
                quai=self.quai,
                date_creneau=self.date_creneau,
                heure_debut__lt=self.heure_fin,
                heure_fin__gt=self.heure_debut,
            ).exclude(statut__in=['ANNULE', 'TERMINE'])

            if self.pk:
                conflits = conflits.exclude(pk=self.pk)

            if conflits.exists():
                c = conflits.first()
                errors['heure_debut'] = (
                    f"Conflit de créneau détecté ! Le quai {self.quai.numero} est déjà occupé de "
                    f"{c.heure_debut.strftime('%H:%M')} à {c.heure_fin.strftime('%H:%M')} "
                    f"(Réf: {c.reference} - {c.transporteur_nom})."
                )

        if errors:
            raise ValidationError(errors)

    @property
    def duree_minutes(self):
        """Calcule la durée prévue du créneau en minutes."""
        if not self.heure_debut or not self.heure_fin:
            return 0
        t1 = timedelta(hours=self.heure_debut.hour, minutes=self.heure_debut.minute)
        t2 = timedelta(hours=self.heure_fin.hour, minutes=self.heure_fin.minute)
        return int((t2 - t1).total_seconds() // 60)

    @property
    def badge_statut_css(self):
        """Retourne la classe CSS du badge selon l'état."""
        mapping = {
            'EN_ATTENTE': 'badge-warning',
            'CONFIRME': 'badge-info',
            'ARRIVE': 'badge-primary',
            'EN_COURS': 'badge-success pulse',
            'TERMINE': 'badge-secondary',
            'EN_RETARD': 'badge-danger',
            'ANNULE': 'badge-muted',
        }
        return mapping.get(self.statut, 'badge-secondary')

    # Actions opérationnelles directes
    def confirmer(self, user=None):
        self.statut = 'CONFIRME'
        self.save()
        self._enregistrer_historique('CONFIRME', user, "Créneau confirmé et validé au planning.")

    def marquer_arrive(self, user=None):
        self.statut = 'ARRIVE'
        self.heure_arrivee_reelle = timezone.now()
        self.save()
        self._enregistrer_historique('ARRIVE', user, "Camion enregistré à l'accueil du site.")

    def mettre_a_quai(self, user=None):
        """Active l'opération et bloque le quai correspondant."""
        self.statut = 'EN_COURS'
        self.heure_debut_operation = timezone.now()
        self.save()
        # Occupe automatiquement le quai physique
        if self.quai:
            self.quai.occuper()
        self._enregistrer_historique('EN_COURS', user, "Véhicule mis à quai. Début du chargement/déchargement.")

    def terminer(self, user=None):
        """Clôture l'opération et libère le quai."""
        self.statut = 'TERMINE'
        self.heure_fin_operation = timezone.now()
        self.save()
        # Libère le quai physique
        if self.quai:
            self.quai.liberer()
        self._enregistrer_historique('TERMINE', user, "Opération terminée avec succès. Quai libéré.")

    def annuler(self, motif="", user=None):
        """Annule le créneau et libère le quai si nécessaire."""
        self.statut = 'ANNULE'
        self.motif_annulation = motif
        self.save()
        if self.quai and self.quai.statut == 'OCCUPE':
            self.quai.liberer()
        self._enregistrer_historique('ANNULE', user, f"Créneau annulé. Motif: {motif or 'Non précisé'}")

    def _enregistrer_historique(self, nouveau_statut, user, commentaire=""):
        HistoriqueStatutCreneau.objects.create(
            creneau=self,
            statut=nouveau_statut,
            auteur=user if (user and user.is_authenticated) else None,
            commentaire=commentaire
        )


class HistoriqueStatutCreneau(models.Model):
    """
    Traçabilité complète des changements de statut pour chaque créneau (Slide 11 : Traçabilité).
    """
    creneau = models.ForeignKey(Creneau, on_delete=models.CASCADE, related_name='historique')
    statut = models.CharField(max_length=20, choices=Creneau.STATUT_CHOICES)
    auteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_changement = models.DateTimeField(auto_now_add=True)
    commentaire = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Historique statut créneau"
        verbose_name_plural = "Historiques statuts créneaux"
        ordering = ['-date_changement']

    def __str__(self):
        return f"{self.creneau.reference} ➔ {self.get_statut_display()} ({self.date_changement.strftime('%d/%m/%Y %H:%M')})"
