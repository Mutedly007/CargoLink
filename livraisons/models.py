import secrets
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from . import geo, regles


def generer_code_suivi():
    """Code public de suivi : 8 caractères sans caractères ambigus (0/O, 1/I)."""
    alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(secrets.choice(alphabet) for _ in range(8))


class Livraison(models.Model):
    """
    Modèle central du module Gestion des Livraisons (Module Eya - CodeCraft / CargoLink).
    Une livraison relie un camion (Rahma), un chauffeur (Khalil), des créneaux de quai (Kacem)
    et des entrepôts (Aziz), du chargement jusqu'à la preuve de livraison.
    """

    STATUT_CHOICES = [
        ('BROUILLON', 'Brouillon (en préparation)'),
        ('PLANIFIEE', 'Planifiée (camion & chauffeur affectés)'),
        ('EN_CHARGEMENT', 'En chargement à quai'),
        ('EN_TRANSIT', 'En transit / Sur la route'),
        ('ARRIVEE', 'Arrivée à destination'),
        ('LIVREE', 'Livrée (preuve validée)'),
        ('ECHEC', 'Échec de livraison'),
        ('ANNULEE', 'Annulée'),
    ]

    TYPE_LIVRAISON_CHOICES = [
        ('INTER_ENTREPOT', 'Transfert inter-entrepôts'),
        ('CLIENT', 'Livraison client final'),
    ]

    PRIORITE_CHOICES = [
        ('NORMALE', 'Normale'),
        ('URGENTE', 'Priorité Haute / Urgente'),
        ('FLEXIBLE', 'Flexible'),
    ]

    # Même référentiel que le module Créneaux (Kacem)
    TYPE_MARCHANDISE_CHOICES = [
        ('STANDARD', 'Marchandise générale / Sec'),
        ('FRIGORIFIQUE', 'Température dirigée (Frais / Surgelé)'),
        ('ADR', 'Matières dangereuses (ADR)'),
        ('GROS_VOLUME', 'Gros volume / Hors gabarit'),
        ('PALETTES', 'Palettes standardisées'),
    ]

    # Identification
    reference = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Référence de livraison")
    code_suivi = models.CharField(
        max_length=12, unique=True, blank=True, verbose_name="Code de suivi public",
        help_text="Code communiqué au destinataire pour suivre sa livraison sans compte"
    )
    type_livraison = models.CharField(
        max_length=20, choices=TYPE_LIVRAISON_CHOICES, default='INTER_ENTREPOT', verbose_name="Type de livraison"
    )
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='BROUILLON', verbose_name="Statut")
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='NORMALE', verbose_name="Priorité")

    # Trajet
    entrepot_origine = models.ForeignKey(
        'entrepots.Entrepot', on_delete=models.PROTECT, related_name='livraisons_sortantes',
        verbose_name="Entrepôt de départ"
    )
    entrepot_destination = models.ForeignKey(
        'entrepots.Entrepot', on_delete=models.PROTECT, null=True, blank=True,
        related_name='livraisons_entrantes', verbose_name="Entrepôt de destination"
    )
    destinataire_nom = models.CharField(max_length=150, blank=True, verbose_name="Destinataire / Client")
    destinataire_telephone = models.CharField(max_length=40, blank=True, verbose_name="Téléphone du destinataire")
    destinataire_email = models.EmailField(blank=True, verbose_name="Email du destinataire")
    adresse_livraison = models.CharField(max_length=255, blank=True, verbose_name="Adresse de livraison")
    ville_livraison = models.CharField(max_length=100, blank=True, verbose_name="Ville de livraison")

    # Affectation (FK réelles vers les modules de l'équipe)
    camion = models.ForeignKey(
        'camions.Camion', on_delete=models.PROTECT, null=True, blank=True,
        related_name='livraisons', verbose_name="Camion affecté"
    )
    chauffeur = models.ForeignKey(
        'chauffeurs.Chauffeur', on_delete=models.PROTECT, null=True, blank=True,
        related_name='livraisons', verbose_name="Chauffeur affecté"
    )
    creneau_chargement = models.ForeignKey(
        'creneaux.Creneau', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='livraisons_chargement', verbose_name="Créneau de chargement (départ)"
    )
    creneau_dechargement = models.ForeignKey(
        'creneaux.Creneau', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='livraisons_dechargement', verbose_name="Créneau de déchargement (arrivée)"
    )

    # Marchandise
    type_marchandise = models.CharField(
        max_length=30, choices=TYPE_MARCHANDISE_CHOICES, default='STANDARD', verbose_name="Type de marchandise"
    )
    description_marchandise = models.CharField(max_length=255, blank=True, verbose_name="Description de la marchandise")
    nb_palettes = models.PositiveIntegerField(default=10, verbose_name="Nombre de palettes")
    poids_kg = models.PositiveIntegerField(null=True, blank=True, verbose_name="Poids total (kg)")
    numero_bl = models.CharField(max_length=80, blank=True, verbose_name="N° Bon de Livraison / CMR")
    consignes = models.TextField(blank=True, verbose_name="Consignes de transport")

    # Planification & réalisation
    date_depart_prevue = models.DateTimeField(verbose_name="Départ prévu")
    date_livraison_prevue = models.DateTimeField(verbose_name="Livraison prévue (échéance)")
    date_depart_reelle = models.DateTimeField(null=True, blank=True, verbose_name="Départ réel")
    date_arrivee_reelle = models.DateTimeField(null=True, blank=True, verbose_name="Arrivée réelle")
    date_livraison_reelle = models.DateTimeField(null=True, blank=True, verbose_name="Livraison réelle")
    est_en_retard = models.BooleanField(default=False, verbose_name="Signalée en retard")

    # Preuve de livraison (POD)
    receptionnaire_nom = models.CharField(max_length=150, blank=True, verbose_name="Nom du réceptionnaire")
    signature = models.ImageField(upload_to='livraisons/signatures/', blank=True, null=True, verbose_name="Signature")
    photo_preuve = models.ImageField(upload_to='livraisons/preuves/', blank=True, null=True, verbose_name="Photo de preuve")
    reserves = models.TextField(blank=True, verbose_name="Réserves à la réception")
    livraison_conforme = models.BooleanField(default=True, verbose_name="Livraison conforme")
    note_satisfaction = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Note du destinataire (1-5)")

    motif_echec = models.TextField(blank=True, verbose_name="Motif d'échec")
    motif_annulation = models.TextField(blank=True, verbose_name="Motif d'annulation")

    createur = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='livraisons_creees', verbose_name="Créée par"
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Livraison"
        verbose_name_plural = "Livraisons"
        ordering = ['-date_depart_prevue']
        indexes = [
            models.Index(fields=['statut']),
            models.Index(fields=['date_depart_prevue']),
            models.Index(fields=['code_suivi']),
        ]

    def __str__(self):
        return f"{self.reference or 'Livraison'} • {self.ville_depart} → {self.ville_arrivee} [{self.get_statut_display()}]"

    def get_absolute_url(self):
        return reverse('livraisons:livraison_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # Référence au format des créneaux de Kacem : LIV-AAAAMMJJ-XXXXX
        if not self.reference:
            jour = self.date_depart_prevue or timezone.now()
            self.reference = f"LIV-{jour.strftime('%Y%m%d')}-{uuid.uuid4().hex[:5].upper()}"
        if not self.code_suivi:
            code = generer_code_suivi()
            while Livraison.objects.filter(code_suivi=code).exists():
                code = generer_code_suivi()
            self.code_suivi = code
        super().save(*args, **kwargs)

    # ------------------------------------------------------------------
    # Validation (règles R1 à R10 - voir regles.py)
    # ------------------------------------------------------------------
    def clean(self):
        super().clean()
        erreurs = {}

        # R10 : champs obligatoires selon le type
        if self.type_livraison == 'INTER_ENTREPOT':
            if not self.entrepot_destination_id:
                erreurs['entrepot_destination'] = "L'entrepôt de destination est obligatoire pour un transfert."
            elif self.entrepot_destination_id == self.entrepot_origine_id:
                erreurs['entrepot_destination'] = "La destination doit être différente de l'entrepôt de départ."
        else:
            if not self.destinataire_nom:
                erreurs['destinataire_nom'] = "Le nom du destinataire est obligatoire pour une livraison client."
            if not self.adresse_livraison:
                erreurs['adresse_livraison'] = "L'adresse de livraison est obligatoire."
            if not self.ville_livraison:
                erreurs['ville_livraison'] = "La ville de livraison est obligatoire."

        # R9 : cohérence des dates
        if self.date_depart_prevue and self.date_livraison_prevue:
            if self.date_livraison_prevue <= self.date_depart_prevue:
                erreurs['date_livraison_prevue'] = "L'échéance de livraison doit être postérieure au départ prévu."

        # R8 : cohérence des créneaux avec les entrepôts (module Kacem)
        erreurs.update(self._verifier_creneaux())

        # R1 à R7 : uniquement tant que la livraison n'est pas clôturée
        if self.statut not in ('LIVREE', 'ECHEC', 'ANNULEE'):
            camion = self.camion if self.camion_id else None
            chauffeur = self.chauffeur if self.chauffeur_id else None
            for cle, msg in regles.verifier_camion(camion, self.poids_kg, self.nb_palettes, self.type_marchandise).items():
                erreurs.setdefault(cle, msg)
            for cle, msg in regles.verifier_chauffeur(chauffeur, camion, self.type_marchandise, self.date_livraison_prevue).items():
                erreurs.setdefault(cle, msg)
            for cle, msg in regles.conflits_planning(
                self.date_depart_prevue, self.date_livraison_prevue, camion, chauffeur, exclure_pk=self.pk
            ).items():
                erreurs.setdefault(cle, msg)

        if erreurs:
            raise ValidationError(erreurs)

    def _verifier_creneaux(self):
        erreurs = {}
        actives = Livraison.objects.exclude(statut__in=['ANNULEE', 'ECHEC'])
        if self.pk:
            actives = actives.exclude(pk=self.pk)

        cr = self.creneau_chargement if self.creneau_chargement_id else None
        if cr:
            if cr.type_operation != 'CHARGEMENT':
                erreurs['creneau_chargement'] = f"Le créneau {cr.reference} est un créneau de déchargement."
            elif cr.entrepot_id != self.entrepot_origine_id:
                erreurs['creneau_chargement'] = f"Le créneau {cr.reference} n'est pas situé dans l'entrepôt de départ."
            elif cr.statut == 'ANNULE':
                erreurs['creneau_chargement'] = f"Le créneau {cr.reference} est annulé."
            elif actives.filter(models.Q(creneau_chargement=cr) | models.Q(creneau_dechargement=cr)).exists():
                erreurs['creneau_chargement'] = f"Le créneau {cr.reference} est déjà lié à une autre livraison."

        cr = self.creneau_dechargement if self.creneau_dechargement_id else None
        if cr:
            if self.type_livraison != 'INTER_ENTREPOT':
                erreurs['creneau_dechargement'] = "Une livraison client ne passe pas par un quai de déchargement CargoLink."
            elif cr.type_operation != 'DECHARGEMENT':
                erreurs['creneau_dechargement'] = f"Le créneau {cr.reference} est un créneau de chargement."
            elif cr.entrepot_id != self.entrepot_destination_id:
                erreurs['creneau_dechargement'] = f"Le créneau {cr.reference} n'est pas situé dans l'entrepôt de destination."
            elif cr.statut == 'ANNULE':
                erreurs['creneau_dechargement'] = f"Le créneau {cr.reference} est annulé."
            elif actives.filter(models.Q(creneau_chargement=cr) | models.Q(creneau_dechargement=cr)).exists():
                erreurs['creneau_dechargement'] = f"Le créneau {cr.reference} est déjà lié à une autre livraison."
        return erreurs

    # ------------------------------------------------------------------
    # Propriétés calculées
    # ------------------------------------------------------------------
    @property
    def ville_depart(self):
        return self.entrepot_origine.ville if self.entrepot_origine_id else ''

    @property
    def ville_arrivee(self):
        if self.type_livraison == 'INTER_ENTREPOT' and self.entrepot_destination_id:
            return self.entrepot_destination.ville
        return self.ville_livraison

    @property
    def libelle_destination(self):
        if self.type_livraison == 'INTER_ENTREPOT' and self.entrepot_destination_id:
            return self.entrepot_destination.nom
        return self.destinataire_nom or self.ville_livraison

    @property
    def est_active(self):
        return self.statut in regles.STATUTS_ACTIFS

    @property
    def est_cloturee(self):
        return self.statut in ('LIVREE', 'ECHEC', 'ANNULEE')

    @property
    def distance_km(self):
        return geo.distance_km(self.ville_depart, self.ville_arrivee)

    @property
    def duree_estimee(self):
        type_camion = self.camion.type_camion if self.camion_id else 'SEMI_REMORQUE'
        return geo.duree_trajet(self.distance_km, type_camion)

    @property
    def duree_estimee_texte(self):
        duree = self.duree_estimee
        if not duree:
            return ''
        minutes = int(duree.total_seconds() // 60)
        return f"{minutes // 60} h {minutes % 60:02d}" if minutes >= 60 else f"{minutes} min"

    @property
    def co2_estime_kg(self):
        if not self.camion_id:
            return geo.co2_kg(self.distance_km)
        return geo.co2_kg(self.distance_km, self.camion.norme_anti_pollution, self.camion.type_camion)

    @property
    def eta(self):
        """Heure d'arrivée estimée : départ réel (ou prévu) + durée de trajet estimée."""
        if self.date_arrivee_reelle:
            return self.date_arrivee_reelle
        duree = self.duree_estimee
        depart = self.date_depart_reelle or self.date_depart_prevue
        if not duree or not depart:
            return self.date_livraison_prevue
        return depart + duree

    @property
    def retard_minutes(self):
        """Retard (minutes) par rapport à l'échéance : réel si livrée, sinon projeté sur l'ETA."""
        if self.statut in ('ANNULEE', 'BROUILLON'):
            return 0
        reference = self.date_livraison_reelle
        if reference is None:
            reference = max(timezone.now(), self.eta) if self.statut != 'ECHEC' else None
        if reference is None or not self.date_livraison_prevue:
            return 0
        return max(0, int((reference - self.date_livraison_prevue).total_seconds() // 60))

    @property
    def livree_a_l_heure(self):
        if self.statut != 'LIVREE' or not self.date_livraison_reelle:
            return None
        return self.date_livraison_reelle <= self.date_livraison_prevue

    @property
    def utilisation_capacite(self):
        """Taux de remplissage du camion (%), sur le critère le plus contraignant."""
        if not self.camion_id:
            return None
        taux = []
        if self.poids_kg and self.camion.capacite_tonnage:
            taux.append(self.poids_kg / float(self.camion.capacite_tonnage * 1000))
        if self.nb_palettes and self.camion.capacite_palettes:
            taux.append(self.nb_palettes / self.camion.capacite_palettes)
        return round(max(taux) * 100) if taux else None

    @property
    def nb_incidents_ouverts(self):
        return self.incidents.filter(resolu=False).count()

    @property
    def badge_statut_css(self):
        mapping = {
            'BROUILLON': 'badge-muted',
            'PLANIFIEE': 'badge-info',
            'EN_CHARGEMENT': 'badge-primary',
            'EN_TRANSIT': 'badge-warning',
            'ARRIVEE': 'badge-primary',
            'LIVREE': 'badge-success',
            'ECHEC': 'badge-danger',
            'ANNULEE': 'badge-muted',
        }
        return mapping.get(self.statut, 'badge-muted')

    @property
    def statut_court(self):
        return {
            'BROUILLON': 'Brouillon', 'PLANIFIEE': 'Planifiée', 'EN_CHARGEMENT': 'Chargement',
            'EN_TRANSIT': 'En route', 'ARRIVEE': 'Arrivée', 'LIVREE': 'Livrée',
            'ECHEC': 'Échec', 'ANNULEE': 'Annulée',
        }.get(self.statut, self.statut)

    ETAPES = [
        ('BROUILLON', 'Préparée'),
        ('PLANIFIEE', 'Planifiée'),
        ('EN_CHARGEMENT', 'Chargement'),
        ('EN_TRANSIT', 'En route'),
        ('ARRIVEE', 'Arrivée'),
        ('LIVREE', 'Livrée'),
    ]

    @property
    def etapes(self):
        """Étapes du suivi visuel avec leur état (fait / en cours / à venir)."""
        codes = [code for code, _ in self.ETAPES]
        position = codes.index(self.statut) if self.statut in codes else -1
        if self.statut == 'ECHEC':
            position = codes.index('ARRIVEE')
        resultat = []
        for i, (code, libelle) in enumerate(self.ETAPES):
            if self.statut == 'LIVREE' or i < position:
                etat = 'fait'
            elif i == position:
                etat = 'en_cours'
            else:
                etat = 'a_venir'
            resultat.append({'code': code, 'libelle': libelle, 'etat': etat})
        return resultat


class SuiviLivraison(models.Model):
    """Historique horodaté des changements d'état d'une livraison (traçabilité - Slide 11)."""
    livraison = models.ForeignKey(Livraison, on_delete=models.CASCADE, related_name='suivis')
    statut = models.CharField(max_length=20, choices=Livraison.STATUT_CHOICES)
    auteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    commentaire = models.CharField(max_length=255, blank=True)
    localisation = models.CharField(max_length=120, blank=True, verbose_name="Localisation déclarée")
    visible_public = models.BooleanField(default=True, verbose_name="Visible sur la page de suivi publique")

    class Meta:
        verbose_name = "Suivi de livraison"
        verbose_name_plural = "Suivis de livraison"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.livraison.reference} ➔ {self.get_statut_display()} ({self.date:%d/%m/%Y %H:%M})"


class IncidentLivraison(models.Model):
    """Incident déclaré pendant une livraison (panne, accident, dommage, refus...)."""
    TYPE_CHOICES = [
        ('RETARD', 'Retard / Trafic'),
        ('PANNE', 'Panne du véhicule'),
        ('ACCIDENT', 'Accident'),
        ('DOMMAGE', 'Marchandise endommagée'),
        ('REFUS_CLIENT', 'Refus du destinataire'),
        ('ADRESSE_INTROUVABLE', 'Adresse introuvable / Destinataire absent'),
        ('AUTRE', 'Autre'),
    ]
    GRAVITE_CHOICES = [
        ('FAIBLE', 'Faible'),
        ('MOYENNE', 'Moyenne'),
        ('CRITIQUE', 'Critique'),
    ]

    livraison = models.ForeignKey(Livraison, on_delete=models.CASCADE, related_name='incidents')
    type_incident = models.CharField(max_length=30, choices=TYPE_CHOICES, default='RETARD', verbose_name="Type d'incident")
    gravite = models.CharField(max_length=10, choices=GRAVITE_CHOICES, default='MOYENNE', verbose_name="Gravité")
    description = models.TextField(verbose_name="Description")
    photo = models.ImageField(upload_to='livraisons/incidents/', blank=True, null=True, verbose_name="Photo")
    declare_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    resolu = models.BooleanField(default=False, verbose_name="Résolu")
    resolution = models.TextField(blank=True, verbose_name="Résolution apportée")
    date_resolution = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Incident de livraison"
        verbose_name_plural = "Incidents de livraison"
        ordering = ['resolu', '-date']

    def __str__(self):
        return f"{self.get_type_incident_display()} • {self.livraison.reference}"
