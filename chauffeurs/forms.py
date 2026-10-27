from datetime import date, timedelta
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            if not self.initial.get('date_embauche'):
                self.initial['date_embauche'] = date.today()
            if not self.initial.get('ville_residence'):
                self.initial['ville_residence'] = 'Tunis'
            if not self.initial.get('capacite_camion_tonnes'):
                self.initial['capacite_camion_tonnes'] = 24.0
            if not self.initial.get('entreprise_transport'):
                self.initial['entreprise_transport'] = 'Express Cargo Tunisie'
            if not self.initial.get('type_camion'):
                self.initial['type_camion'] = 'SEMI_REMORQUE'
        if 'capacite_camion_tonnes' in self.fields:
            self.fields['capacite_camion_tonnes'].required = False
        if 'type_camion' in self.fields:
            self.fields['type_camion'].required = False

    def clean_type_camion(self):
        val = self.cleaned_data.get('type_camion')
        return val or 'SEMI_REMORQUE'

    def clean_prenom(self):
        prenom = self.cleaned_data.get('prenom', '').strip()
        if len(prenom) < 2:
            raise forms.ValidationError("Le prénom doit comporter au moins 2 caractères.")
        import re
        if not re.match(r"^[\w\s\-\'\.À-ÿ]+$", prenom, re.UNICODE):
            raise forms.ValidationError("Le prénom contient des caractères non valides.")
        return prenom

    def clean_nom(self):
        nom = self.cleaned_data.get('nom', '').strip()
        if len(nom) < 2:
            raise forms.ValidationError("Le nom de famille doit comporter au moins 2 caractères.")
        import re
        if not re.match(r"^[\w\s\-\'\.À-ÿ]+$", nom, re.UNICODE):
            raise forms.ValidationError("Le nom contient des caractères non valides.")
        return nom

    def clean_cin(self):
        cin = self.cleaned_data.get('cin', '').strip().upper()
        if cin:
            import re
            if not re.match(r"^[A-Z0-9\-\s]{6,20}$", cin):
                raise forms.ValidationError("Le numéro CIN ou passeport doit comporter entre 6 et 20 caractères alphanumériques.")
        return cin

    def clean_telephone(self):
        tel = self.cleaned_data.get('telephone', '').strip()
        if not tel:
            raise forms.ValidationError("Le numéro de téléphone principal est obligatoire.")
        import re
        cleaned_tel = re.sub(r'[\s\-\.]', '', tel)
        if not re.match(r"^\+?[0-9]{8,15}$", cleaned_tel):
            raise forms.ValidationError("Numéro de téléphone invalide (au moins 8 chiffres requis, ex: +216 98 123 456).")
        return tel

    def clean_telephone_urgence(self):
        tel_urg = self.cleaned_data.get('telephone_urgence', '').strip()
        if tel_urg:
            import re
            cleaned_tel = re.sub(r'[\s\-\.]', '', tel_urg)
            if not re.match(r"^\+?[0-9]{8,15}$", cleaned_tel):
                raise forms.ValidationError("Numéro de téléphone d'urgence invalide (au moins 8 chiffres requis).")
        return tel_urg

    def clean_date_naissance(self):
        naissance = self.cleaned_data.get('date_naissance')
        if naissance:
            today = date.today()
            if naissance >= today:
                raise forms.ValidationError("La date de naissance ne peut pas être dans le futur.")
            age = (today - naissance).days // 365
            if age < 18:
                raise forms.ValidationError("Le chauffeur doit être majeur (au moins 18 ans révolus).")
            if age > 75:
                raise forms.ValidationError("Veuillez vérifier l'année de naissance (âge maximum fixé à 75 ans).")
        return naissance

    def clean_date_embauche(self):
        embauche = self.cleaned_data.get('date_embauche')
        if embauche:
            today = date.today()
            if embauche > today + timedelta(days=60):
                raise forms.ValidationError("La date d'embauche ne peut pas être fixée à plus de 60 jours dans le futur.")
        return embauche

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and hasattr(photo, 'size'):
            # Limite à 5 Mo
            max_size = 5 * 1024 * 1024
            if photo.size > max_size:
                raise forms.ValidationError("La taille de la photo ne doit pas dépasser 5 Mo.")
            # Extension valide
            filename = photo.name.lower()
            valid_exts = ('.jpg', '.jpeg', '.png', '.webp')
            if not any(filename.endswith(ext) for ext in valid_exts):
                raise forms.ValidationError("Format d'image non supporté. Formats acceptés : JPG, JPEG, PNG, WEBP.")
        return photo

    def clean_numero_permis(self):
        permis = self.cleaned_data.get('numero_permis', '').strip().upper()
        if len(permis) < 4:
            raise forms.ValidationError("Le numéro de permis doit comporter au moins 4 caractères.")
        # Unicité du permis (en ignorant l'instance actuelle lors de l'édition)
        qs = Chauffeur.objects.filter(numero_permis__iexact=permis)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Ce numéro de permis « {permis} » est déjà enregistré pour un autre chauffeur.")
        return permis

    def clean_capacite_camion_tonnes(self):
        cap = self.cleaned_data.get('capacite_camion_tonnes')
        if cap is not None:
            if cap <= 0:
                raise forms.ValidationError("La capacité du camion doit être supérieure à 0.")
            if cap > 60:
                raise forms.ValidationError("La capacité maximale d'un ensemble routier est limitée à 60 tonnes.")
        return cap

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
        naissance = cleaned_data.get('date_naissance')
        embauche = cleaned_data.get('date_embauche')
        tel = (cleaned_data.get('telephone') or '').strip()
        tel_urg = (cleaned_data.get('telephone_urgence') or '').strip()
        today = date.today()

        # Délivrance dans le futur
        if delivrance and delivrance > today:
            self.add_error('date_delivrance_permis', "La date de délivrance du permis ne peut pas être située dans le futur.")

        # Expiration après délivrance
        if delivrance and expiration and expiration <= delivrance:
            self.add_error('date_expiration_permis', "La date d'expiration doit être strictement postérieure à la date de délivrance.")

        # Âge à la délivrance du permis (au moins 18 ans)
        if naissance and delivrance:
            age_at_license = (delivrance - naissance).days // 365
            if age_at_license < 18:
                self.add_error('date_delivrance_permis', "Le chauffeur ne pouvait pas détenir un permis de conduire avant ses 18 ans.")

        # Date d'embauche vs Date de naissance
        if naissance and embauche:
            if embauche < naissance:
                self.add_error('date_embauche', "La date d'embauche ne peut pas précéder la date de naissance.")
            elif (embauche - naissance).days // 365 < 18:
                self.add_error('date_embauche', "Le chauffeur devait être majeur (au moins 18 ans) à la date de début d'activité.")

        # Téléphone d'urgence différent du téléphone principal
        if tel and tel_urg:
            import re
            c_tel = re.sub(r'[\s\-\.]', '', tel)
            c_urg = re.sub(r'[\s\-\.]', '', tel_urg)
            if c_tel == c_urg:
                self.add_error('telephone_urgence', "Le contact d'urgence doit être différent du numéro de téléphone principal.")

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
