from django.urls import path
from . import views

app_name = 'entrepots'

urlpatterns = [
    # CRUD Entrepôts
    path('', views.entrepot_list, name='entrepot_list'),
    path('nouveau/', views.entrepot_create, name='entrepot_create'),
    path('<int:pk>/', views.entrepot_detail, name='entrepot_detail'),
    path('<int:pk>/modifier/', views.entrepot_update, name='entrepot_update'),
    path('<int:pk>/supprimer/', views.entrepot_delete, name='entrepot_delete'),

    # CRUD Quais
    path('quais/', views.quai_list, name='quai_list'),
    path('quais/nouveau/', views.quai_create, name='quai_create'),
    path('<int:entrepot_pk>/quais/nouveau/', views.quai_create, name='quai_create_for_entrepot'),
    path('quais/<int:pk>/', views.quai_detail, name='quai_detail'),
    path('quais/<int:pk>/modifier/', views.quai_update, name='quai_update'),
    path('quais/<int:pk>/supprimer/', views.quai_delete, name='quai_delete'),
    path('quais/<int:pk>/toggle/', views.quai_toggle_status, name='quai_toggle_status'),

    # Smart Capacity Optimizer AI (Strict Scope: Entrepot & Quai)
    path('optimizer/', views.capacity_optimizer_dashboard, name='capacity_optimizer'),
    path('optimizer/simulate/', views.capacity_optimizer_simulate_api, name='capacity_optimizer_simulate'),
    path('optimizer/action/', views.capacity_optimizer_action_api, name='capacity_optimizer_action'),
    path('optimizer/refresh/', views.capacity_optimizer_refresh_api, name='capacity_optimizer_refresh'),
]
