"""
URL configuration for gestkin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from gestkin.core import views
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.login_view, name='login'),  # Página de inicio de sesión
    path('lista-pacientes/', views.lista_pacientes, name='lista_pacientes'),  # Lista para confirmar los datos
    path('historial/', views.historial_pacientes, name='historial_pacientes'),  # Historial de pacientes
    path('ingreso-pacientes/', views.ingreso_pacientes, name='ingreso_pacientes'),  # Ingreso de pacientes
    path('usuarios/', views.admin_usuarios, name='admin_usuarios'),  # Gestión de usuarios
    path('admin/', admin.site.urls),  # Admin panel
    path('inicio/', views.login_view, name='inicio'),  # Agregar la ruta /inicio
    path('logout/', LogoutView.as_view(), name='logout'),  # Ruta para cerrar sesión
    path('editar-paciente/<int:id>/', views.editar_paciente, name='editar_paciente'),
    path('eliminar-paciente/<int:paciente_id>/', views.eliminar_paciente, name='eliminar_paciente'),
    path('detalle-paciente/<int:id>/', views.detalle_paciente, name='detalle_paciente'),
    path("actualizar-estado-paciente/<int:paciente_id>/", views.actualizar_estado_paciente, name="actualizar_estado_paciente"),
]

# Agregar manejo de archivos de medios en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
