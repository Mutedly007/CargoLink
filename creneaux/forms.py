from datetime import date
from django import forms
from .models import Creneau
from entrepots.models import Entrepot, Quai


class CreneauForm(forms.ModelForm):
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
            'nb_palettes': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'poids_kg': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'placeholder': 'Optionnel'}),
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


class DemandeCreneauForm(forms.ModelForm):
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
            'immatriculation_camion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Immatriculation du véhicule'}),
            'type_camion': forms.Select(attrs={'class': 'form-select'}),
            'chauffeur_nom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nom du chauffeur affecté'}),
            'chauffeur_telephone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Numéro de contact'}),
            'type_marchandise': forms.Select(attrs={'class': 'form-select'}),
            'nb_palettes': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'numero_bl': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Référence BL / Bon transport'}),
            'consignes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Consignes ou contraintes spécifiques...'}),
        }


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
