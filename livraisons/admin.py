from django.contrib import admin
from .models import IncidentLivraison, Livraison, SuiviLivraison


class SuiviLivraisonInline(admin.TabularInline):
    model = SuiviLivraison
    extra = 0
    fields = ('date', 'statut', 'auteur', 'commentaire', 'localisation', 'visible_public')
    readonly_fields = ('date',)


class IncidentLivraisonInline(admin.TabularInline):
    model = IncidentLivraison
    extra = 0
    fields = ('date', 'type_incident', 'gravite', 'description', 'resolu')
    readonly_fields = ('date',)


@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = (
        'reference',
        'type_livraison',
        'statut',
        'priorite',
        'entrepot_origine',
        'entrepot_destination',
        'camion',
        'chauffeur',
        'date_depart_prevue',
        'date_livraison_prevue',
        'est_en_retard',
    )
    list_filter = ('statut', 'type_livraison', 'priorite', 'type_marchandise', 'est_en_retard', 'entrepot_origine')
    search_fields = ('reference', 'code_suivi', 'numero_bl', 'destinataire_nom', 'camion__immatriculation', 'chauffeur__nom')
    readonly_fields = ('reference', 'code_suivi', 'date_creation', 'date_modification')
    inlines = [SuiviLivraisonInline, IncidentLivraisonInline]


@admin.register(IncidentLivraison)
class IncidentLivraisonAdmin(admin.ModelAdmin):
    list_display = ('livraison', 'type_incident', 'gravite', 'date', 'resolu')
    list_filter = ('type_incident', 'gravite', 'resolu')
