from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('landing.urls')),
    path('', include('accounts.urls')),
    path('accounts/login/', RedirectView.as_view(pattern_name='login', permanent=False, query_string=True)),
    path('entrepots/', include('entrepots.urls')),
    path('creneaux/', include('creneaux.urls')),
    path('camions/', include('camions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

