from django.urls import path
from . import views

app_name = 'creneaux'

urlpatterns = [
    # Dashboard & Planning
    path('', views.creneau_list, name='creneau_list'),
    path('planning/', views.creneau_planning, name='creneau_planning'),

    # 1. Création & Demande de créneau (Module Kacem)
    path('nouveau/', views.creneau_create, name='creneau_create'),
    path('demande/', views.demande_creneau, name='demande_creneau'),

    # 2. Consultation, Modification & Annulation
    path('<int:pk>/', views.creneau_detail, name='creneau_detail'),
    path('<int:pk>/modifier/', views.creneau_update, name='creneau_update'),
    path('<int:pk>/annuler/', views.creneau_cancel, name='creneau_cancel'),

    # 3. Confirmation de créneau (Module Kacem)
    path('<int:pk>/confirmer/', views.creneau_confirm, name='creneau_confirm'),
    path('<int:pk>/action/<str:action>/', views.creneau_action_statut, name='creneau_action_statut'),

    # Export & Rapports
    path('export/csv/', views.creneau_export_csv, name='creneau_export_csv'),

    # 4. Assistant IA Google Gemini (Périmètre Créneaux Strict)
    path('assistant/', views.assistant_creneaux, name='assistant_creneaux'),
    path('api/gemini-chat/', views.api_gemini_chat, name='api_gemini_chat'),

    # Helper AJAX & IA
    path('api/quais/<int:entrepot_id>/', views.api_quais_by_entrepot, name='api_quais_by_entrepot'),
    path('api/ai-recommend-dock/', views.api_ai_recommend_dock, name='api_ai_recommend_dock'),
]
