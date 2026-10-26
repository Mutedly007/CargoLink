from django.shortcuts import render


def landing_page(request):
    """Page d'accueil principale de CargoLink."""
    return render(request, 'landing/landing.html')
