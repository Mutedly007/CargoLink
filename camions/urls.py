from django.urls import path
from . import views

app_name = 'camions'

urlpatterns = [
    path('', views.CamionListView.as_view(), name='camion_list'),
    path('nouveau/', views.CamionCreateView.as_view(), name='camion_create'),
    path('<int:pk>/', views.CamionDetailView.as_view(), name='camion_detail'),
    path('<int:pk>/modifier/', views.CamionUpdateView.as_view(), name='camion_update'),
    path('<int:pk>/supprimer/', views.CamionDeleteView.as_view(), name='camion_delete'),
    path('<int:pk>/changer-statut/', views.CamionQuickStatusView.as_view(), name='camion_quick_status'),
    path('<int:pk>/passages/ajouter/', views.HistoriquePassageCreateView.as_view(), name='historique_passage_create'),
    path('<int:pk>/ai-diagnostic/', views.CamionAIDiagnosticView.as_view(), name='camion_ai_diagnostic'),
]
