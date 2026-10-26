from django.shortcuts import render


class AdminAccessControlMiddleware:
    """
    Middleware de sécurité contrôlant l'accès à l'interface Django Admin (/admin/).
    Empêche les utilisateurs non autorisés (non connectés ou sans rôle Administrateur)
    d'accéder à l'écran de login natif Django Admin.
    Affiche une page 'Page Non Accessible' (403) dédiée CargoLink.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Vérifie si la requête cible l'interface d'administration
        if request.path.startswith('/admin'):
            user = getattr(request, 'user', None)
            is_admin = False

            if user and user.is_authenticated:
                if user.is_superuser or user.is_staff:
                    is_admin = True
                elif hasattr(user, 'profile') and user.profile.is_admin:
                    is_admin = True

            if not is_admin:
                context = {
                    'page_title': 'Page Non Accessible • CargoLink',
                    'current_user': user if (user and user.is_authenticated) else None,
                }
                return render(request, 'accounts/admin_access_denied.html', context, status=403)

        return self.get_response(request)
