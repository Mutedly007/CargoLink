from django.urls import path
from . import views

app_name = 'chauffeurs'

urlpatterns = [
    # Dashboard & Liste des chauffeurs
    path('', views.chauffeur_list, name='chauffeur_list'),
    
    # CRUD Chauffeur
    path('nouveau/', views.chauffeur_create, name='chauffeur_create'),
    path('<int:pk>/', views.chauffeur_detail, name='chauffeur_detail'),
    path('<int:pk>/modifier/', views.chauffeur_update, name='chauffeur_update'),
    path('<int:pk>/supprimer/', views.chauffeur_delete, name='chauffeur_delete'),
    
    # Actions rapides & Statut
    path('<int:pk>/statut/', views.chauffeur_statut_update, name='chauffeur_statut_update'),
    
    # Affectation Mission Opérationnelle (Camion dispo + Créneau dispo + Quai dispo)
    path('<int:pk>/affecter-mission/', views.chauffeur_affecter_mission, name='chauffeur_affecter_mission'),
    path('<int:pk>/liberer-mission/', views.chauffeur_liberer_mission, name='chauffeur_liberer_mission'),
    
    # Historique des visites / passages
    path('<int:chauffeur_pk>/visites/nouveau/', views.visite_create, name='visite_create'),
    
    # Portail Mobile Chauffeur (Slide 9 - Responsive smartphone)
    path('portail-mobile/', views.chauffeur_portal_mobile, name='chauffeur_portal_mobile'),
    
    # Assistant IA Conversationnel (Option 4 - Recherche en langage naturel & Support Trilingue FR/AR/EN)
    path('assistant-ia/', views.chauffeur_ai_assistant, name='chauffeur_ai_assistant'),
    path('api/chat/', views.chauffeur_ai_chat_api, name='chauffeur_ai_chat_api'),

    # Export CSV
    path('export/', views.chauffeurs_export, name='chauffeurs_export'),
]

