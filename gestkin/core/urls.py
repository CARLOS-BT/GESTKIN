# gestkin/core/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.redirect_to_login),  # Redirige a '/'
    path('login/', views.login_view, name='login'),  # Inicio de sesión personalizado
    path('logout/', LogoutView.as_view(), name='logout'),  # Cerrar sesión
    path('lista-pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('ingreso-pacientes/', views.ingreso_pacientes, name='ingreso_pacientes'),
    path('usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('editar-paciente/<int:id>/', views.editar_paciente, name='editar_paciente'),
    path('eliminar-paciente/<int:paciente_id>/', views.eliminar_paciente, name='eliminar_paciente'),
    path('detalle-paciente/<int:id>/', views.detalle_paciente, name='detalle_paciente'),
    path("actualizar-estado-paciente/<int:paciente_id>/", views.actualizar_estado_paciente, name="actualizar_estado_paciente"),
    path('eliminar-archivo/<int:archivo_id>/', views.eliminar_archivo, name='eliminar_archivo'),
    path("actualizar-asistencia/<int:sesion_id>/", views.actualizar_asistencia, name="actualizar_asistencia"),
    path('guardar-asistencias/<int:paciente_id>/', views.guardar_asistencias, name='guardar_asistencias'),
    path("eliminar-sesion/<int:sesion_id>/", views.eliminar_sesion, name="eliminar_sesion"),
    path("estadisticas/", views.estadisticas, name="estadisticas"),
    path('estadisticas/reporte_pdf/', views.generar_reporte_pdf, name='generar_reporte_pdf'),
        
]
