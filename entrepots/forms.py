import re
from django import forms
from .models import Entrepot, Quai


class EntrepotForm(forms.ModelForm):
    """
    Formulaire complet pour l'ajout et la modification d'un entrepôt logistique.
    Inclut des contrôles d'entité et de cohérence métier stricts.
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
            'ville': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Rades'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 2040'}),
            'telephone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: +216 71 000 000'}),
            'email_contact': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Ex: logistique@cargolink.tn'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'gestionnaire': forms.Select(attrs={'class': 'form-select'}),
            'horaire_ouverture': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'horaire_fermeture': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'jours_ouverture': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Lundi - Samedi (24h/24 possible)'}),
            'capacite_palettes': forms.NumberInput(attrs={'class': 'form-input', 'min': '1', 'placeholder': 'Ex: 2500'}),
            'superficie_m2': forms.NumberInput(attrs={'class': 'form-input', 'min': '20', 'placeholder': 'Ex: 8500'}),
        }

    def clean_nom(self):
        nom = self.cleaned_data.get('nom', '').strip()
        if not nom:
            raise forms.ValidationError("Le nom de l'entrepôt est obligatoire.")
        if len(nom) < 3:
            raise forms.ValidationError("Le nom de l'entrepôt doit comporter au moins 3 caractères.")
        if nom.isdigit():
            raise forms.ValidationError("Le nom de l'entrepôt ne peut pas être composé uniquement de chiffres.")
        return nom

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip().upper()
        if not code:
            raise forms.ValidationError("Le code d'identification est obligatoire.")
        if len(code) < 3:
            raise forms.ValidationError("Le code d'identification doit comporter au moins 3 caractères.")
        if not re.match(r'^[A-Z0-9_\-]+$', code):
            raise forms.ValidationError("Le code doit contenir uniquement des lettres majuscules, chiffres ou tirets (ex: ENT-RADES-01).")
        qs = Entrepot.objects.filter(code__iexact=code)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Le code d'identification '{code}' est déjà utilisé par un autre entrepôt.")
        return code

    def clean_adresse(self):
        adresse = self.cleaned_data.get('adresse', '').strip()
        if not adresse:
            raise forms.ValidationError("L'adresse postale est obligatoire.")
        if len(adresse) < 5:
            raise forms.ValidationError("L'adresse postale doit comporter au moins 5 caractères.")
        return adresse

    def clean_ville(self):
        ville = self.cleaned_data.get('ville', '').strip()
        if not ville:
            raise forms.ValidationError("Le nom de la ville est obligatoire.")
        if len(ville) < 2:
            raise forms.ValidationError("Le nom de la ville doit comporter au moins 2 caractères.")
        if any(char.isdigit() for char in ville):
            raise forms.ValidationError("Le nom de la ville ne peut pas contenir de chiffres.")
        return ville

    def clean_code_postal(self):
        code_postal = self.cleaned_data.get('code_postal', '').strip()
        if not code_postal:
            raise forms.ValidationError("Le code postal est obligatoire.")
        if len(code_postal) < 4:
            raise forms.ValidationError("Le code postal doit comporter au moins 4 caractères.")
        return code_postal

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone', '').strip()
        if telephone:
            digits_only = re.sub(r'\D', '', telephone)
            if len(digits_only) < 8:
                raise forms.ValidationError("Le numéro de téléphone doit contenir au moins 8 chiffres valides.")
        return telephone

    def clean_capacite_palettes(self):
        capacite = self.cleaned_data.get('capacite_palettes')
        if capacite is None or capacite <= 0:
            raise forms.ValidationError("La capacité de stockage doit être strictement supérieure à zéro.")
        if capacite > 500000:
            raise forms.ValidationError("La capacité de stockage ne peut pas dépasser 500 000 palettes.")
        return capacite

    def clean_superficie_m2(self):
        superficie = self.cleaned_data.get('superficie_m2')
        if superficie is not None:
            if superficie <= 0:
                raise forms.ValidationError("La superficie doit être un nombre strictement positif.")
            if superficie < 20:
                raise forms.ValidationError("La superficie d'un entrepôt doit être d'au moins 20 m².")
        return superficie

    def clean(self):
        cleaned_data = super().clean()
        ouverture = cleaned_data.get('horaire_ouverture')
        fermeture = cleaned_data.get('horaire_fermeture')

        if ouverture and fermeture:
            if ouverture == fermeture:
                self.add_error('horaire_fermeture', "L'heure de fermeture et l'heure d'ouverture ne peuvent pas être identiques.")
        return cleaned_data

    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            for field_name in self.errors:
                if field_name in self.fields:
                    current_classes = self.fields[field_name].widget.attrs.get('class', '')
                    if 'is-invalid' not in current_classes:
                        self.fields[field_name].widget.attrs['class'] = f"{current_classes} is-invalid".strip()
        return valid


class QuaiForm(forms.ModelForm):
    """
    Formulaire complet pour l'ajout et la modification d'un quai de chargement.
    Inclut des contrôles d'entité et de cohérence métier stricts.
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

    def clean_entrepot(self):
        entrepot = self.cleaned_data.get('entrepot')
        if not entrepot:
            raise forms.ValidationError("Veuillez sélectionner un entrepôt de rattachement.")
        return entrepot

    def clean_numero(self):
        numero = self.cleaned_data.get('numero', '').strip()
        if not numero:
            raise forms.ValidationError("Le numéro ou identifiant du quai est obligatoire.")
        if len(numero) < 2:
            raise forms.ValidationError("Le numéro de quai doit comporter au moins 2 caractères (ex: Quai A-01).")
        return numero

    def clean_capacite_camions_simultanes(self):
        camions = self.cleaned_data.get('capacite_camions_simultanes')
        if camions is None:
            return 1
        if camions < 1 or camions > 5:
            raise forms.ValidationError("Le nombre de camions simultanés doit être compris entre 1 et 5.")
        return camions

    def clean_capacite_palettes_heure(self):
        debit = self.cleaned_data.get('capacite_palettes_heure')
        if debit is None:
            return 33
        if debit <= 0:
            raise forms.ValidationError("Le débit horaire doit être strictement supérieur à zéro.")
        if debit > 300:
            raise forms.ValidationError("Le débit horaire ne peut pas dépasser 300 palettes / heure.")
        return debit

    def clean(self):
        cleaned_data = super().clean()
        entrepot = cleaned_data.get('entrepot')
        numero = cleaned_data.get('numero')

        if entrepot and numero:
            qs = Quai.objects.filter(entrepot=entrepot, numero__iexact=numero.strip())
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('numero', f"Le quai '{numero}' existe déjà au sein de cet entrepôt.")
        return cleaned_data

    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            for field_name in self.errors:
                if field_name in self.fields:
                    current_classes = self.fields[field_name].widget.attrs.get('class', '')
                    if 'is-invalid' not in current_classes:
                        self.fields[field_name].widget.attrs['class'] = f"{current_classes} is-invalid".strip()
        return valid
