from django.contrib import admin
from .models import Creneau, HistoriqueStatutCreneau


class HistoriqueInline(admin.TabularInline):
    model = HistoriqueStatutCreneau
    extra = 0
    readonly_fields = ('statut', 'auteur', 'date_changement', 'commentaire')
    can_delete = False


@admin.register(Creneau)
class CreneauAdmin(admin.ModelAdmin):
    list_display = (
        'reference', 'entrepot', 'quai', 'date_creneau',
        'heure_debut', 'heure_fin', 'type_operation', 'statut',
        'transporteur_nom', 'immatriculation_camion'
    )
    list_filter = ('statut', 'type_operation', 'date_creneau', 'entrepot', 'type_marchandise')
    search_fields = ('reference', 'transporteur_nom', 'immatriculation_camion', 'chauffeur_nom', 'numero_bl')
    ordering = ('-date_creneau', 'heure_debut')
    inlines = [HistoriqueInline]


@admin.register(HistoriqueStatutCreneau)
class HistoriqueStatutCreneauAdmin(admin.ModelAdmin):
    list_display = ('creneau', 'statut', 'auteur', 'date_changement', 'commentaire')
    list_filter = ('statut', 'date_changement')
    search_fields = ('creneau__reference', 'commentaire')
