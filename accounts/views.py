from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignUpForm, LoginForm, ProfileUpdateForm
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
            next_url = request.POST.get('next') or request.GET.get('next') or 'landing'
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


@login_required
def profile_view(request):
    """Consultation et modification du profil utilisateur et paramètres de sécurité."""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, user=user)
        if form.is_valid():
            user.first_name = form.cleaned_data.get('first_name', '')
            user.last_name = form.cleaned_data.get('last_name', '')
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']

            profile.role = form.cleaned_data['role']
            profile.entreprise = form.cleaned_data.get('entreprise', '')
            profile.telephone = form.cleaned_data.get('telephone', '')

            password_changed = False
            new_password = form.cleaned_data.get('new_password')
            if new_password:
                user.set_password(new_password)
                password_changed = True

            user.save()
            profile.save()

            if password_changed:
                update_session_auth_hash(request, user)
                messages.success(request, "Votre profil et vos identifiants de sécurité ont été mis à jour avec succès !")
            else:
                messages.success(request, "Votre profil a été mis à jour avec succès !")

            return redirect('profile')
    else:
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'role': profile.role,
            'entreprise': profile.entreprise,
            'telephone': profile.telephone,
        }
        form = ProfileUpdateForm(initial=initial_data, user=user)

    context = {
        'form': form,
        'profile': profile,
        'page_title': 'Mon Profil & Paramètres - CargoLink',
    }
    return render(request, 'accounts/profile.html', context)

