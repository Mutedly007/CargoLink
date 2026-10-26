from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Camion, HistoriquePassage
from entrepots.models import Entrepot, Quai


class CamionForm(forms.ModelForm):
    """
    Formulaire complet pour l'ajout et l'édition d'un camion.
    Intègre les validations métier côté serveur et les attributs ARIA/accessibilité.
    """

    class Meta:
        model = Camion
        fields = [
            'immatriculation',
            'marque',
            'modele',
            'annee_fabrication',
            'type_camion',
            'capacite_tonnage',
            'volume_m3',
            'capacite_palettes',
            'etat',
            'kilometrage',
            'norme_anti_pollution',
            'societe_transport',
            'date_derniere_maintenance',
            'date_prochain_controle',
        ]
        widgets = {
            'immatriculation': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex: 234 TUN 5678 ou AA-123-BB',
                'aria-describedby': 'id_immatriculation_help',
                'autocomplete': 'off',
                'style': 'text-transform: uppercase;',
            }),
            'marque': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex: Volvo, Scania, Mercedes-Benz, Renault Trucks',
            }),
            'modele': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex: FH 500, Actros 1845, T-High 480',
            }),
            'annee_fabrication': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '2022',
                'min': '1980',
                'max': '2030',
            }),
            'type_camion': forms.Select(attrs={'class': 'form-select'}),
            'capacite_tonnage': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '24.00',
                'step': '0.1',
                'min': '0.5',
            }),
            'volume_m3': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '85',
                'min': '5',
            }),
            'capacite_palettes': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '33',
                'min': '1',
            }),
            'etat': forms.Select(attrs={'class': 'form-select'}),
            'kilometrage': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '120000',
                'min': '0',
            }),
            'norme_anti_pollution': forms.Select(attrs={'class': 'form-select'}),
            'societe_transport': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex: Express Fret International, STAF Logistics...',
            }),
            'date_derniere_maintenance': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'date_prochain_controle': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
        }

    def clean_immatriculation(self):
        immat = self.cleaned_data.get('immatriculation', '').strip().upper()
        if len(immat) < 4:
            raise ValidationError("L'immatriculation doit comporter au moins 4 caractères.")
        
        # Vérification unicité en excluant l'instance courante lors de la mise à jour
        query = Camion.objects.filter(immatriculation__iexact=immat)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise ValidationError("Un camion avec cette immatriculation est déjà enregistré sur la plateforme.")
        return immat

    def clean_capacite_tonnage(self):
        capacite = self.cleaned_data.get('capacite_tonnage')
        if capacite is not None and capacite <= 0:
            raise ValidationError("La charge utile doit être supérieure à 0 tonne.")
        return capacite


class HistoriquePassageForm(forms.ModelForm):
    """
    Formulaire pour enregistrer un nouveau passage de quai pour un camion.
    """

    class Meta:
        model = HistoriquePassage
        fields = [
            'entrepot',
            'quai',
            'type_operation',
            'statut',
            'poids_mesure_kg',
            'numero_bon_livraison',
            'date_sortie',
            'observations',
        ]
        widgets = {
            'entrepot': forms.Select(attrs={'class': 'form-select'}),
            'quai': forms.Select(attrs={'class': 'form-select'}),
            'type_operation': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'poids_mesure_kg': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex: 24500 kg',
                'min': '0',
            }),
            'numero_bon_livraison': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex: BL-2026-8891 ou CMR-FR-774',
            }),
            'date_sortie': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local',
            }),
            'observations': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Observations de quai, état de la marchandise, anomalies...',
            }),
        }
