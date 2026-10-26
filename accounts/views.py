from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignUpForm, LoginForm
from .models import UserProfile




def signup_view(request):
    """Inscription utilisateur avec sélection interactive du rôle logistique."""
    if request.user.is_authenticated:
        return redirect('landing')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Création de l'utilisateur Django
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )

            # Mise à jour du profil étendu avec le rôle choisi
            profile = user.profile
            profile.role = form.cleaned_data['role']
            profile.entreprise = form.cleaned_data.get('entreprise', '')
            profile.telephone = form.cleaned_data.get('telephone', '')
            profile.save()

            # Connexion automatique
            login(request, user)
            messages.success(
                request,
                f"Bienvenue sur CargoLink, {user.first_name or user.username} ! "
                f"Votre compte en tant que « {profile.get_role_display()} » a été créé avec succès."
            )
            return redirect('landing')
    else:
        initial_role = request.GET.get('role', 'ENTREPOT')
        form = SignUpForm(initial={'role': initial_role})

    return render(request, 'accounts/signup.html', {'form': form, 'page_title': 'Inscription - CargoLink'})


def login_view(request):
    """Connexion utilisateur avec prise en charge du nom d'utilisateur ou de l'email."""
    if request.user.is_authenticated:
        return redirect('landing')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            if user.is_superuser or user.is_staff:
                role_label = 'Administrateur'
            elif hasattr(user, 'profile'):
                role_label = user.profile.get_role_display()
            else:
                role_label = 'Membre'
            display_name = user.get_full_name() or user.username
            messages.success(
                request,
                f"Ravi de vous revoir, {display_name} ! Connecté en tant que {role_label}."
            )
            next_url = request.GET.get('next', 'landing')
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'page_title': 'Connexion - CargoLink'})


def logout_view(request):
    """Déconnexion de l'utilisateur."""
    if request.user.is_authenticated:
        messages.info(request, "Vous avez été déconnecté avec succès. À bientôt sur CargoLink !")
        logout(request)
    return redirect('landing')
