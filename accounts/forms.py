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
