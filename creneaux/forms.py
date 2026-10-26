import re
from datetime import date, datetime, timedelta
from django import forms
from .models import Creneau
from entrepots.models import Entrepot, Quai


class CreneauValidationMixin:
    """
    Mixin centralisant le contrôle de saisie et la validation métier stricte
    pour la demande et la planification des créneaux horaires (Module Kacem).
    Garantit la conformité des formats, des plages horaires et des équipements quai.
    """

    def clean_date_creneau(self):
        date_creneau = self.cleaned_data.get('date_creneau')
        if date_creneau:
            today = date.today()
            if date_creneau < today:
                raise forms.ValidationError(
                    "Date invalide : Vous ne pouvez pas sélectionner une date d'intervention antérieure à aujourd'hui."
                )
            if date_creneau > today + timedelta(days=180):
                raise forms.ValidationError(
                    "Horizon dépassé : La réservation d'un créneau ne peut pas excéder 6 mois (180 jours) à l'avance."
                )
        return date_creneau

    def clean_immatriculation_camion(self):
        immat = self.cleaned_data.get('immatriculation_camion', '')
        if immat:
            immat = immat.strip().upper()
            if len(immat) < 3:
                raise forms.ValidationError(
                    "L'immatriculation du véhicule doit comporter au moins 3 caractères."
                )
            # Accepte les formats internationaux, français (AA-123-BB), tunisiens (123-TN-4567, 123 TU 45) et alphanumériques
            if not re.match(r'^[A-Z0-9\s\-]{3,20}$', immat):
                raise forms.ValidationError(
                    "Format d'immatriculation invalide. Utilisez des lettres, chiffres et tirets (ex: 123-TN-4567, AA-123-BB, 1234 TU 185)."
                )
        return immat

    def clean_transporteur_nom(self):
        nom = self.cleaned_data.get('transporteur_nom', '')
        if nom:
            nom = nom.strip()
            if len(nom) < 2:
                raise forms.ValidationError(
                    "Le nom du transporteur doit comporter au moins 2 caractères."
                )
        return nom

    def clean_chauffeur_nom(self):
        nom = self.cleaned_data.get('chauffeur_nom', '')
        if nom:
            nom = nom.strip()
            if len(nom) < 2:
                raise forms.ValidationError(
                    "Le nom du chauffeur doit comporter au moins 2 caractères."
                )
            if not any(c.isalpha() for c in nom):
                raise forms.ValidationError(
                    "Le nom du chauffeur doit contenir des caractères alphabétiques valides."
                )
        return nom

    def clean_chauffeur_telephone(self):
        tel = self.cleaned_data.get('chauffeur_telephone', '')
        if tel:
            tel = tel.strip()
            # Valide les numéros internationaux et nationaux standard (+216 98 123 456, 06 12 34 56 78, etc.)
            if not re.match(r'^\+?[0-9\s\-\.\(\)]{8,20}$', tel):
                raise forms.ValidationError(
                    "Numéro de téléphone invalide (ex: +216 98 123 456 ou 06 12 34 56 78)."
                )
        return tel

    def clean_nb_palettes(self):
        nb = self.cleaned_data.get('nb_palettes')
        if nb is not None:
            if nb < 1:
                raise forms.ValidationError(
                    "Le volume estimé doit être d'au moins 1 palette."
                )
            if nb > 120:
                raise forms.ValidationError(
                    "Le volume estimé ne peut pas dépasser 120 palettes par créneau unitaire (capacité max semi-remorque double plancher)."
                )
        return nb

    def clean_poids_kg(self):
        poids = self.cleaned_data.get('poids_kg')
        if poids is not None:
            if poids <= 0:
                raise forms.ValidationError(
                    "Le poids doit être strictement supérieur à 0 kg."
                )
            if poids > 35000:
                raise forms.ValidationError(
                    "Le poids total estimé ne peut pas excéder 35 000 kg (35 tonnes - limite fret routier standard)."
                )
        return poids

    def clean_numero_bl(self):
        bl = self.cleaned_data.get('numero_bl', '')
        if bl:
            bl = bl.strip().upper()
        return bl

    def clean(self):
        cleaned_data = super().clean()
        entrepot = cleaned_data.get('entrepot')
        quai = cleaned_data.get('quai')
        date_creneau = cleaned_data.get('date_creneau')
        heure_debut = cleaned_data.get('heure_debut')
        heure_fin = cleaned_data.get('heure_fin')
        type_marchandise = cleaned_data.get('type_marchandise')

        # 1. Cohérence chronologique des heures (Début < Fin)
        if heure_debut and heure_fin:
            if heure_debut >= heure_fin:
                self.add_error(
                    'heure_fin',
                    "Incohérence horaire : L'heure de fin estimée doit être strictement postérieure à l'heure de début."
                )
            else:
                delta = datetime.combine(date.min, heure_fin) - datetime.combine(date.min, heure_debut)
                if delta < timedelta(minutes=15):
                    self.add_error(
                        'heure_fin',
                        "Durée insuffisante : Un créneau d'opération sur quai doit durer au minimum 15 minutes."
                    )
                elif delta > timedelta(hours=8):
                    self.add_error(
                        'heure_fin',
                        "Durée excessive : Un créneau d'intervention ne peut pas excéder 8 heures consécutives."
                    )

        # 2. Vérification d'appartenance du quai à l'entrepôt
        if entrepot and quai:
            if quai.entrepot_id != entrepot.id:
                self.add_error(
                    'quai',
                    f"Incompatibilité site : Le quai {quai.numero} n'appartient pas à l'entrepôt sélectionné ({entrepot.nom})."
                )
            elif quai.statut in ('MAINTENANCE', 'INACTIF'):
                self.add_error(
                    'quai',
                    f"Quai indisponible : Le quai {quai.numero} est actuellement hors service (Statut : {quai.get_statut_display()})."
                )

        # 3. Respect des plages d'ouverture de l'entrepôt
        if entrepot and heure_debut and heure_fin:
            if entrepot.horaire_ouverture and heure_debut < entrepot.horaire_ouverture:
                self.add_error(
                    'heure_debut',
                    f"Site fermé : L'heure de début ({heure_debut.strftime('%H:%M')}) précède l'ouverture de l'entrepôt ({entrepot.horaire_ouverture.strftime('%H:%M')})."
                )
            if entrepot.horaire_fermeture and heure_fin > entrepot.horaire_fermeture:
                self.add_error(
                    'heure_fin',
                    f"Site fermé : L'heure de fin ({heure_fin.strftime('%H:%M')}) dépasse la fermeture de l'entrepôt ({entrepot.horaire_fermeture.strftime('%H:%M')})."
                )

        # 4. Compatibilité technique quai / marchandise (Frigorifique, ADR)
        if quai and type_marchandise:
            if type_marchandise == 'FRIGORIFIQUE' and quai.type_quai != 'FRIGORIFIQUE':
                self.add_error(
                    'type_marchandise',
                    f"Équipement inadapté : Le quai {quai.numero} ({quai.get_type_quai_display()}) n'est pas équipé pour la marchandise sous température dirigée (Frigorifique)."
                )
            elif type_marchandise == 'ADR' and quai.type_quai != 'ADR':
                self.add_error(
                    'type_marchandise',
                    f"Non habilité : Le quai {quai.numero} ({quai.get_type_quai_display()}) n'est pas certifié pour les matières dangereuses (ADR)."
                )

        # 5. Détection de chevauchement et prévention des conflits sur le même quai
        if quai and date_creneau and heure_debut and heure_fin and heure_debut < heure_fin:
            conflits = Creneau.objects.filter(
                quai=quai,
                date_creneau=date_creneau,
                heure_debut__lt=heure_fin,
                heure_fin__gt=heure_debut,
            ).exclude(statut__in=['ANNULE', 'TERMINE'])

            if self.instance and self.instance.pk:
                conflits = conflits.exclude(pk=self.instance.pk)

            if conflits.exists():
                c = conflits.first()
                self.add_error(
                    'heure_debut',
                    f"Conflit quai détecté : Le quai {quai.numero} est déjà réservé de {c.heure_debut.strftime('%H:%M')} à {c.heure_fin.strftime('%H:%M')} (Réf: {c.reference} - {c.transporteur_nom})."
                )

        return cleaned_data


class CreneauForm(CreneauValidationMixin, forms.ModelForm):
    """
    Formulaire complet de gestion et planification de créneaux
    (utilisé par les gestionnaires de site et planificateurs logistiques).
    """
    date_creneau = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-input',
            'min': date.today().strftime('%Y-%m-%d')
        }),
        label="Date d'opération"
    )
    heure_debut = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
        label="Heure de début"
    )
    heure_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
        label="Heure de fin estimée"
    )

    class Meta:
        model = Creneau
        fields = [
            'entrepot', 'quai', 'type_operation', 'priorite',
            'date_creneau', 'heure_debut', 'heure_fin',
            'transporteur_nom', 'immatriculation_camion', 'type_camion',
            'chauffeur_nom', 'chauffeur_telephone',
            'type_marchandise', 'nb_palettes', 'poids_kg', 'numero_bl',
            'consignes'
        ]
        widgets = {
            'entrepot': forms.Select(attrs={'class': 'form-select', 'id': 'id_entrepot'}),
            'quai': forms.Select(attrs={'class': 'form-select', 'id': 'id_quai'}),
            'type_operation': forms.Select(attrs={'class': 'form-select'}),
            'priorite': forms.Select(attrs={'class': 'form-select'}),
            'transporteur_nom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Transports Express Sud'}),
            'immatriculation_camion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 123-TN-4567'}),
            'type_camion': forms.Select(attrs={'class': 'form-select'}),
            'chauffeur_nom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Karim Ben Salem'}),
            'chauffeur_telephone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: +216 98 123 456'}),
            'type_marchandise': forms.Select(attrs={'class': 'form-select'}),
            'nb_palettes': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 120}),
            'poids_kg': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 35000, 'placeholder': 'Ex: 12500'}),
            'numero_bl': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'N° BL / CMR'}),
            'consignes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Consignes de déchargement, précautions particulières...'}),
        }

    def __init__(self, *args, **kwargs):
        entrepot_id = kwargs.pop('entrepot_id', None)
        super().__init__(*args, **kwargs)

        # Si un entrepôt est déjà spécifié ou sélectionné, filtrer les quais associés
        if entrepot_id:
            self.fields['entrepot'].initial = entrepot_id
            self.fields['quai'].queryset = Quai.objects.filter(entrepot_id=entrepot_id)
        elif self.instance and self.instance.pk and self.instance.entrepot_id:
            self.fields['quai'].queryset = Quai.objects.filter(entrepot_id=self.instance.entrepot_id)


class DemandeCreneauForm(CreneauValidationMixin, forms.ModelForm):
    """
    Formulaire de Demande de Créneau (Module Kacem - Slide 16).
    Permet à un transporteur ou partenaire de solliciter un créneau horaire sur un quai.
    La demande sera ensuite soumise à vérification des disponibilités et confirmation.
    """
    date_creneau = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-input',
            'min': date.today().strftime('%Y-%m-%d')
        }),
        label="Date d'intervention souhaitée"
    )
    heure_debut = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
        label="Heure de début souhaitée"
    )
    heure_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
        label="Heure de fin estimée"
    )

    class Meta:
        model = Creneau
        fields = [
            'entrepot', 'quai', 'type_operation',
            'date_creneau', 'heure_debut', 'heure_fin',
            'transporteur_nom', 'immatriculation_camion', 'type_camion',
            'chauffeur_nom', 'chauffeur_telephone',
            'type_marchandise', 'nb_palettes', 'numero_bl', 'consignes'
        ]
        widgets = {
            'entrepot': forms.Select(attrs={'class': 'form-select', 'id': 'id_demande_entrepot'}),
            'quai': forms.Select(attrs={'class': 'form-select', 'id': 'id_demande_quai'}),
            'type_operation': forms.Select(attrs={'class': 'form-select'}),
            'transporteur_nom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Société de transport demanderesse'}),
            'immatriculation_camion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Immatriculation du véhicule (ex: 123-TN-4567)'}),
            'type_camion': forms.Select(attrs={'class': 'form-select'}),
            'chauffeur_nom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nom du chauffeur affecté'}),
            'chauffeur_telephone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Numéro de contact (ex: +216 98 123 456)'}),
            'type_marchandise': forms.Select(attrs={'class': 'form-select'}),
            'nb_palettes': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 120}),
            'numero_bl': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Référence BL / Bon transport'}),
            'consignes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Consignes ou contraintes spécifiques...'}),
        }

    def __init__(self, *args, **kwargs):
        entrepot_id = kwargs.pop('entrepot_id', None)
        super().__init__(*args, **kwargs)

        if entrepot_id:
            self.fields['entrepot'].initial = entrepot_id
            self.fields['quai'].queryset = Quai.objects.filter(entrepot_id=entrepot_id)
        elif self.instance and self.instance.pk and self.instance.entrepot_id:
            self.fields['quai'].queryset = Quai.objects.filter(entrepot_id=self.instance.entrepot_id)


class AnnulationCreneauForm(forms.Form):
    """Formulaire d'annulation avec motif obligatoire."""
    motif_annulation = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 3,
            'placeholder': 'Veuillez préciser la raison de l\'annulation (ex: Panne camion, retard imprévu, report de livraison...)'
        }),
        label="Motif d'annulation",
        required=True
    )
