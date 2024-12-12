# gestkin/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Panel de administración
    path('', include('gestkin.core.urls')),  # Delegar manejo de rutas a la app 'core'
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Manejo de archivos de medios en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


