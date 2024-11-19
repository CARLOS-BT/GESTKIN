from django.urls import path
from gestkin.core import views


urlpatterns = [
    path('', views.login_view, name='login'),                # Página de inicio de sesión
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),  # Listado de pacientes
    path('historial/', views.historial_pacientes, name='historial_pacientes'),  # Historial de pacientes
    path('ingreso/', views.ingreso_paciente, name='ingreso_paciente'),  # Formulario de ingreso
    ##path('estadisticas/', views.estadisticas, name='estadisticas'),    # Estadísticas
    path('usuarios/', views.admin_usuarios, name='admin_usuarios'),    # Gestión de usuarios
]
