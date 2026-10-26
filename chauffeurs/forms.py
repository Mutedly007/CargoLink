from datetime import date
from django import forms
from .models import Chauffeur, VisiteChauffeur


class ChauffeurForm(forms.ModelForm):
    """
    Formulaire complet pour l'ajout et l'édition d'un chauffeur.
    Module sous la responsabilité de Khalil Hlila (CodeCraft / CargoLink).
    """

    class Meta:
        model = Chauffeur
        fields = [
            'prenom', 'nom', 'cin', 'email', 'telephone', 'telephone_urgence',
            'photo', 'date_naissance', 'date_embauche', 'ville_residence',
            'numero_permis', 'categorie_permis', 'date_delivrance_permis', 'date_expiration_permis',
            'entreprise_transport', 'transporteur_user',
            'immatriculation_camion', 'marque_camion', 'type_camion', 'capacite_camion_tonnes',
            'statut', 'badge_acces_portuaire', 'observations'
        ]
        widgets = {
            'prenom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Khalil'}),
            'nom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Hlila'}),
            'cin': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 08492011'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Ex: khalil.chauffeur@cargolink.tn'}),
            'telephone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: +216 98 123 456'}),
            'telephone_urgence': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: +216 50 999 888'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'ville_residence': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Tunis / Rades / Sfax'}),
            
            'numero_permis': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: PERM-TN-9812'}),
            'categorie_permis': forms.Select(attrs={'class': 'form-select'}),
            'date_delivrance_permis': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'date_expiration_permis': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            
            'entreprise_transport': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Express Fret Logistique'}),
            'transporteur_user': forms.Select(attrs={'class': 'form-select'}),
            
            'immatriculation_camion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 198-TN-4509'}),
            'marque_camion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Volvo FH 500 / Scania R450'}),
            'type_camion': forms.Select(attrs={'class': 'form-select'}),
            'capacite_camion_tonnes': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.5', 'min': '1', 'max': '50'}),
            
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'badge_acces_portuaire': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'observations': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Instructions spécifiques, habilitations matières dangereuses...'}),
        }

    def clean_numero_permis(self):
        permis = self.cleaned_data.get('numero_permis', '').strip().upper()
        if len(permis) < 4:
            raise forms.ValidationError("Le numéro de permis doit comporter au moins 4 caractères.")
        return permis

    def clean_immatriculation_camion(self):
        immat = self.cleaned_data.get('immatriculation_camion', '').strip().upper()
        if immat:
            from camions.models import Camion
            camion = Camion.objects.filter(immatriculation__iexact=immat).first()
            if camion:
                current_immat = (getattr(self.instance, 'immatriculation_camion', '') or '').strip().upper()
                # Si c'est un camion différent ou une nouvelle affectation, vérifier qu'il est DISPONIBLE
                if immat != current_immat and camion.etat != 'DISPONIBLE':
                    raise forms.ValidationError(
                        f"Le camion « {immat} » ({camion.marque} {camion.modele}) n'est pas disponible actuellement "
                        f"(État actuel : {camion.get_etat_display()}). Seul un camion disponible peut être affecté."
                    )
        return immat

    def clean(self):
        cleaned_data = super().clean()
        delivrance = cleaned_data.get('date_delivrance_permis')
        expiration = cleaned_data.get('date_expiration_permis')

        if delivrance and expiration and expiration <= delivrance:
            self.add_error('date_expiration_permis', "La date d'expiration doit être postérieure à la date de délivrance.")

        return cleaned_data


class VisiteChauffeurForm(forms.ModelForm):
    """
    Formulaire pour enregistrer un nouveau passage ou contrôle de visite en entrepôt.
    """

    class Meta:
        model = VisiteChauffeur
        fields = [
            'entrepot', 'quai_numero', 'numero_bl', 'type_operation', 'statut',
            'date_visite', 'heure_arrivee', 'heure_depart', 'duree_minutes',
            'emargement_valide', 'notes'
        ]
        widgets = {
            'entrepot': forms.Select(attrs={'class': 'form-select'}),
            'quai_numero': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Quai A-01'}),
            'numero_bl': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: BL-2026-8849'}),
            'type_operation': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'date_visite': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'heure_arrivee': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'heure_depart': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'duree_minutes': forms.NumberInput(attrs={'class': 'form-input', 'min': '5'}),
            'emargement_valide': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Contrôle effectué sans anomalie...'}),
        }
