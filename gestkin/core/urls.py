from gestkin.core import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', views.login_view, name='login'),                # Página de inicio de sesión
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),  # Listado de pacientes
    path('historial/', views.historial_pacientes, name='historial_pacientes'),  # Historial de pacientes
    path('ingreso-pacientes/', views.ingreso_pacientes, name='ingreso_pacientes'),  # Formulario de ingreso
    # path('estadisticas/', views.estadisticas, name='estadisticas'),  # Estadísticas (comentar si no existe)
    path('usuarios/', views.admin_usuarios, name='admin_usuarios'),    # Gestión de usuarios
    path('admin/', admin.site.urls),                                  # Admin de Django
    path('editar-paciente/<int:id>/', views.editar_paciente, name='editar_paciente'),
    path('eliminar-paciente/<int:paciente_id>/', views.eliminar_paciente, name='eliminar_paciente'),
    path('detalle-paciente/<int:id>/', views.detalle_paciente, name='detalle_paciente'),
    path('lista-pacientes/', views.lista_pacientes, name='lista_pacientes'),
]
