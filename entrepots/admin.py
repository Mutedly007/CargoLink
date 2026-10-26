from django.contrib import admin
from .models import Entrepot, Quai


class QuaiInline(admin.TabularInline):
    model = Quai
    extra = 1
    fields = ('numero', 'type_quai', 'statut', 'capacite_palettes_heure', 'type_camion_accepte', 'a_niveleur', 'a_sas_isotherme')


@admin.register(Entrepot)
class EntrepotAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code', 'ville', 'statut', 'capacite_palettes', 'get_nb_quais', 'horaire_ouverture', 'horaire_fermeture')
    list_filter = ('statut', 'ville')
    search_fields = ('nom', 'code', 'ville', 'adresse', 'telephone')
    inlines = [QuaiInline]

    def get_nb_quais(self, obj):
        return obj.nb_quais
    get_nb_quais.short_description = "Nombre de quais"


@admin.register(Quai)
class QuaiAdmin(admin.ModelAdmin):
    list_display = ('numero', 'entrepot', 'type_quai', 'statut', 'capacite_palettes_heure', 'type_camion_accepte')
    list_filter = ('statut', 'type_quai', 'entrepot')
    search_fields = ('numero', 'entrepot__nom', 'entrepot__code')
