from django.shortcuts import render
from entrepots.models import Entrepot, Quai


def landing_page(request):
    """Page d'accueil principale de CargoLink avec monitoring en direct."""
    quais_preview = Quai.objects.select_related('entrepot').all()[:3]
    total_quais = Quai.objects.count()
    quais_disponibles = Quai.objects.filter(statut='DISPONIBLE').count()
    total_entrepots = Entrepot.objects.count()

    context = {
        'quais_preview': quais_preview,
        'total_quais': total_quais,
        'quais_disponibles': quais_disponibles,
        'total_entrepots': total_entrepots,
    }
    return render(request, 'landing/landing.html', context)


def custom_404_view(request, exception=None):
    """Page d'erreur 404 personnalisée."""
    return render(request, '404.html', status=404)


def custom_500_view(request):
    """Page d'erreur 500 personnalisée."""
    return render(request, '500.html', status=500)


def custom_403_view(request, exception=None):
    """Page d'erreur 403 personnalisée."""
    return render(request, '403.html', status=403)


