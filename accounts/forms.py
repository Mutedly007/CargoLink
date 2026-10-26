from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile


class SignUpForm(forms.Form):
    ROLE_CHOICES = [
        ('ENTREPOT', "Gestionnaire d'Entrepôt", "Supervisez les quais, les stocks et les opérations d'entrepôt."),
        ('TRANSPORTEUR', "Transporteur / Chauffeur", "Gérez votre flotte de camions et vos missions de fret."),
        ('PLANIFICATEUR', "Planificateur de Créneaux", "Réservez et optimisez les créneaux d'arrivée aux quais."),
    ]

    first_name = forms.CharField(
        max_length=50,
        label="Prénom",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Mohamed Aziz'})
    )
    last_name = forms.CharField(
        max_length=50,
        label="Nom",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Hammami'})
    )
    username = forms.CharField(
        max_length=50,
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'aziz_logistique'})
    )
    email = forms.EmailField(
        label="Adresse Email",
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'aziz@cargolink.tn'})
    )
    role = forms.ChoiceField(
        choices=[(r[0], r[1]) for r in ROLE_CHOICES],
        label="Votre Rôle Principal",
        widget=forms.RadioSelect(attrs={'class': 'role-radio'}),
        initial='ENTREPOT'
    )
    entreprise = forms.CharField(
        max_length=150,
        required=False,
        label="Entreprise / Organisation",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: CargoLink Logistics'})
    )
    telephone = forms.CharField(
        max_length=30,
        required=False,
        label="Numéro de Téléphone",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+216 -- --- ---'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '••••••••'})
    )
    password_confirm = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '••••••••'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Une compte avec cette adresse email existe déjà.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Les deux mots de passe ne correspondent pas.")
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur ou Email",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': "Entrez votre nom d'utilisateur ou email"})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '••••••••'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Allow login with either username or email
            user = authenticate(username=username, password=password)
            if not user and '@' in username:
                try:
                    user_obj = User.objects.get(email__iexact=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if not user:
                raise forms.ValidationError("Identifiants incorrects. Veuillez vérifier vos accès.")
            self.user = user
        return cleaned_data


class ProfileUpdateForm(forms.Form):
    ROLE_CHOICES = [
        ('ENTREPOT', "Gestionnaire d'Entrepôt", "Supervisez les quais, les stocks et les opérations d'entrepôt.", "🏢"),
        ('TRANSPORTEUR', "Transporteur / Chauffeur", "Gérez votre flotte de camions et vos missions de fret.", "🚚"),
        ('PLANIFICATEUR', "Planificateur de Créneaux", "Réservez et optimisez les créneaux d'arrivée aux quais.", "⏱️"),
    ]

    first_name = forms.CharField(
        max_length=50,
        required=False,
        label="Prénom",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Mohamed Aziz'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        label="Nom",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Hammami'})
    )
    username = forms.CharField(
        max_length=50,
        required=True,
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'aziz_logistique'})
    )
    email = forms.EmailField(
        required=True,
        label="Adresse Email",
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'aziz@cargolink.tn'})
    )
    role = forms.ChoiceField(
        choices=[(r[0], r[1]) for r in ROLE_CHOICES],
        label="Rôle Plateforme",
        widget=forms.RadioSelect(attrs={'class': 'role-radio'}),
        required=True
    )
    entreprise = forms.CharField(
        max_length=150,
        required=False,
        label="Société / Organisation",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: CargoLink Logistics'})
    )
    telephone = forms.CharField(
        max_length=30,
        required=False,
        label="Numéro de Téléphone",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+216 -- --- ---'})
    )
    avatar = forms.ImageField(
        required=False,
        label="Photo de Profil",
        widget=forms.FileInput(attrs={'class': 'avatar-file-input', 'accept': 'image/png,image/jpeg,image/webp,image/gif'})
    )
    delete_avatar = forms.BooleanField(
        required=False,
        widget=forms.HiddenInput()
    )

    # Sécurité / Modification du mot de passe
    old_password = forms.CharField(
        required=False,
        label="Mot de passe actuel",
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '••••••••', 'autocomplete': 'current-password'})
    )
    new_password = forms.CharField(
        required=False,
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '••••••••', 'autocomplete': 'new-password'})
    )
    confirm_new_password = forms.CharField(
        required=False,
        label="Confirmer le nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '••••••••', 'autocomplete': 'new-password'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            # Si l'utilisateur est administrateur, ajouter l'option ADMIN
            if hasattr(user, 'profile') and (user.profile.role == 'ADMIN' or user.is_superuser):
                self.fields['role'].choices = [
                    ('ENTREPOT', "Gestionnaire d'Entrepôt"),
                    ('TRANSPORTEUR', "Transporteur / Chauffeur"),
                    ('PLANIFICATEUR', "Planificateur de Créneaux"),
                    ('ADMIN', "Administrateur Plateforme"),
                ]

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("Le nom d'utilisateur est obligatoire.")
        qs = User.objects.filter(username__iexact=username)
        if self.user:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé par un autre compte.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("L'adresse email est obligatoire.")
        qs = User.objects.filter(email__iexact=email)
        if self.user:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError("Cette adresse email est déjà associée à un autre compte.")
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError("La taille de l'image ne doit pas dépasser 5 Mo.")
        return avatar

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        # Si l'un des champs de mot de passe est renseigné
        if old_password or new_password or confirm_new_password:
            if not old_password:
                self.add_error('old_password', "Veuillez saisir votre mot de passe actuel pour valider la modification.")
            elif self.user and not self.user.check_password(old_password):
                self.add_error('old_password', "Le mot de passe actuel saisi est incorrect.")

            if not new_password:
                self.add_error('new_password', "Veuillez renseigner votre nouveau mot de passe.")
            elif len(new_password) < 6:
                self.add_error('new_password', "Le mot de passe doit comporter au moins 6 caractères.")

            if not confirm_new_password:
                self.add_error('confirm_new_password', "Veuillez confirmer votre nouveau mot de passe.")
            elif new_password and confirm_new_password and new_password != confirm_new_password:
                self.add_error('confirm_new_password', "Les deux nouveaux mots de passe ne correspondent pas.")

        return cleaned_data

