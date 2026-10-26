from django.contrib import admin
from .models import Camion, HistoriquePassage


class HistoriquePassageInline(admin.TabularInline):
    model = HistoriquePassage
    extra = 0
    fields = ('date_entree', 'date_sortie', 'entrepot', 'quai', 'type_operation', 'statut', 'poids_mesure_kg')
    readonly_fields = ('date_entree',)


@admin.register(Camion)
class CamionAdmin(admin.ModelAdmin):
    list_display = (
        'immatriculation',
        'marque',
        'modele',
        'type_camion',
        'capacite_tonnage',
        'etat',
        'societe_transport',
        'kilometrage',
        'date_prochain_controle'
    )
    list_filter = ('etat', 'type_camion', 'norme_anti_pollution')
    search_fields = ('immatriculation', 'marque', 'modele', 'societe_transport')
    inlines = [HistoriquePassageInline]


@admin.register(HistoriquePassage)
class HistoriquePassageAdmin(admin.ModelAdmin):
    list_display = (
        'camion',
        'entrepot',
        'quai',
        'date_entree',
        'date_sortie',
        'type_operation',
        'statut',
        'poids_mesure_kg'
    )
    list_filter = ('statut', 'type_operation', 'entrepot')
    search_fields = ('camion__immatriculation', 'numero_bon_livraison', 'observations')
