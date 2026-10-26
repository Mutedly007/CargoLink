from django.urls import path
from . import views

app_name = 'livraisons'

urlpatterns = [
    # Tableau de bord, recherche avancée & export
    path('', views.livraison_list, name='livraison_list'),
    path('export/csv/', views.livraison_export_csv, name='livraison_export_csv'),

    # CRUD
    path('nouvelle/', views.livraison_create, name='livraison_create'),
    path('<int:pk>/', views.livraison_detail, name='livraison_detail'),
    path('<int:pk>/modifier/', views.livraison_update, name='livraison_update'),

    # Cycle de vie (POST) : planifier, charger, partir, arriver, annuler, echouer, reaffecter, reserver_creneau
    path('<int:pk>/action/<str:action>/', views.livraison_action, name='livraison_action'),
    path('<int:pk>/preuve/', views.livraison_pod, name='livraison_pod'),
    path('<int:pk>/incident/', views.incident_create, name='incident_create'),
    path('incidents/<int:pk>/resoudre/', views.incident_resoudre, name='incident_resoudre'),
    path('<int:pk>/bon/', views.bon_livraison, name='bon_livraison'),

    # Espace chauffeur mobile
    path('mes-missions/', views.mes_missions, name='mes_missions'),

    # Suivi public (sans connexion)
    path('suivi/', views.suivi_recherche, name='suivi_recherche'),
    path('suivi/<str:code>/', views.suivi_public, name='suivi_public'),

    # API IA (DeepSeek) & aide à la saisie
    path('api/affectation-intelligente/', views.api_smart_assign, name='api_smart_assign'),
    path('api/recherche-ia/', views.api_recherche_ia, name='api_recherche_ia'),
    path('api/<int:pk>/analyse-risque/', views.api_analyse_risque, name='api_analyse_risque'),
    path('api/<int:pk>/message/', views.api_message_destinataire, name='api_message_destinataire'),
    path('api/creneaux/', views.api_creneaux, name='api_creneaux'),
    path('api/estimation/', views.api_estimation, name='api_estimation'),
]
