from django.contrib import admin
from .models import Chauffeur, VisiteChauffeur


class VisiteChauffeurInline(admin.TabularInline):
    model = VisiteChauffeur
    extra = 0
    fields = ('date_visite', 'entrepot', 'quai_numero', 'numero_bl', 'type_operation', 'statut', 'heure_arrivee', 'heure_depart')
    ordering = ('-date_visite',)


@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = (
        'nom_complet', 'telephone', 'numero_permis', 'categorie_permis',
        'date_expiration_permis', 'entreprise_transport', 'immatriculation_camion',
        'statut', 'badge_acces_portuaire', 'get_nb_visites'
    )
    list_filter = ('statut', 'categorie_permis', 'entreprise_transport', 'badge_acces_portuaire')
    search_fields = (
        'nom', 'prenom', 'numero_permis', 'cin', 'telephone',
        'entreprise_transport', 'immatriculation_camion', 'ville_residence'
    )
    inlines = [VisiteChauffeurInline]

    def get_nb_visites(self, obj):
        return obj.nb_visites
    get_nb_visites.short_description = "Visites Réalisées"


@admin.register(VisiteChauffeur)
class VisiteChauffeurAdmin(admin.ModelAdmin):
    list_display = ('chauffeur', 'entrepot', 'quai_numero', 'numero_bl', 'type_operation', 'statut', 'date_visite', 'emargement_valide')
    list_filter = ('statut', 'type_operation', 'entrepot', 'date_visite')
    search_fields = ('chauffeur__nom', 'chauffeur__prenom', 'numero_bl', 'quai_numero', 'notes')
