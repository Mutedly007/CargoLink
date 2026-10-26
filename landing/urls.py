from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('404/', views.custom_404_view, name='preview_404'),
    path('500/', views.custom_500_view, name='preview_500'),
    path('403/', views.custom_403_view, name='preview_403'),
]
