from django import forms
from .models import Entrepot, Quai


class EntrepotForm(forms.ModelForm):
    """
    Formulaire complet pour l'ajout et la modification d'un entrepôt logistique.
    Inclut des contrôles de cohérence métier (horaires, capacités).
    """
    class Meta:
        model = Entrepot
        fields = [
            'nom', 'code', 'adresse', 'ville', 'code_postal',
            'telephone', 'email_contact', 'statut', 'gestionnaire',
            'horaire_ouverture', 'horaire_fermeture', 'jours_ouverture',
            'capacite_palettes', 'superficie_m2'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Hub Logistique Rades Port'}),
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: ENT-RADES-01'}),
            'adresse': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Zone Portuaire, Terminal 3'}),
            'ville': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Rades / Tunis'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 2040'}),
            'telephone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: +216 71 000 000'}),
            'email_contact': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Ex: logistique@cargolink.tn'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'gestionnaire': forms.Select(attrs={'class': 'form-select'}),
            'horaire_ouverture': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'horaire_fermeture': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'jours_ouverture': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Lundi - Samedi (24h/24 possible)'}),
            'capacite_palettes': forms.NumberInput(attrs={'class': 'form-input', 'min': '1', 'placeholder': 'Ex: 2500'}),
            'superficie_m2': forms.NumberInput(attrs={'class': 'form-input', 'min': '50', 'placeholder': 'Ex: 8500'}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip().upper()
        if len(code) < 3:
            raise forms.ValidationError("Le code d'identification doit comporter au moins 3 caractères.")
        return code

    def clean_capacite_palettes(self):
        capacite = self.cleaned_data.get('capacite_palettes')
        if capacite is not None and capacite <= 0:
            raise forms.ValidationError("La capacité de stockage doit être supérieure à zéro.")
        return capacite

    def clean(self):
        cleaned_data = super().clean()
        ouverture = cleaned_data.get('horaire_ouverture')
        fermeture = cleaned_data.get('horaire_fermeture')

        if ouverture and fermeture:
            if ouverture == fermeture:
                raise forms.ValidationError(
                    "L'heure d'ouverture et l'heure de fermeture ne peuvent pas être identiques."
                )
        return cleaned_data


class QuaiForm(forms.ModelForm):
    """
    Formulaire complet pour l'ajout et la modification d'un quai de chargement.
    """
    capacite_camions_simultanes = forms.IntegerField(
        initial=1,
        required=False,
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'min': '1', 'max': '5', 'placeholder': '1'}),
        label="Nombre max de camions simultanés"
    )

    class Meta:
        model = Quai
        fields = [
            'entrepot', 'numero', 'type_quai', 'statut',
            'capacite_camions_simultanes', 'capacite_palettes_heure',
            'type_camion_accepte', 'a_niveleur', 'a_sas_isotherme', 'remarques'
        ]
        widgets = {
            'entrepot': forms.Select(attrs={'class': 'form-select'}),
            'numero': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Quai A-01 (Réception Nord)'}),
            'type_quai': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'capacite_palettes_heure': forms.NumberInput(attrs={'class': 'form-input', 'min': '1', 'placeholder': 'Ex: 33'}),
            'type_camion_accepte': forms.Select(attrs={'class': 'form-select'}),
            'a_niveleur': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'a_sas_isotherme': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'remarques': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Consignes particulières d\'amarrage, hauteur de rampe, restrictions...'}),
        }

    def clean_numero(self):
        numero = self.cleaned_data.get('numero', '').strip()
        if not numero:
            raise forms.ValidationError("Le numéro ou identifiant du quai est obligatoire.")
        return numero

    def clean_capacite_camions_simultanes(self):
        camions = self.cleaned_data.get('capacite_camions_simultanes')
        if not camions:
            return 1
        return camions

    def clean_capacite_palettes_heure(self):
        debit = self.cleaned_data.get('capacite_palettes_heure')
        if not debit:
            return 33
        if debit <= 0:
            raise forms.ValidationError("Le débit horaire doit être strictement supérieur à zéro.")
        return debit

