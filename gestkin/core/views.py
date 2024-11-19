from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Paciente
from datetime import datetime, timedelta
from django.http import HttpResponse

@login_required
def ingreso_pacientes(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        rut = request.POST.get('rut')
        cantidad_sesiones = request.POST.get('cantidad_sesiones')
        fecha_inicio = request.POST.get('fecha_inicio')
        hora_cita = request.POST.get('hora_cita')
        patologia = request.POST.get('patologia')
        observaciones = request.POST.get('observaciones')

        try:
            # Calcular fecha de término (días hábiles)
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            dias_habiles = int(cantidad_sesiones) - 1  # -1 porque el primer día cuenta como sesión
            fecha_actual = fecha_inicio_obj
            dias_agregados = 0
            
            while dias_agregados < dias_habiles:
                fecha_actual += timedelta(days=1)
                if fecha_actual.weekday() < 5:  # 0-4 son días de semana
                    dias_agregados += 1
            
            # Crear nuevo paciente
            paciente = Paciente.objects.create(
                nombre=nombre,
                apellido=apellido,
                rut=rut,
                cantidad_sesiones=cantidad_sesiones,
                fecha_inicio=fecha_inicio,
                fecha_termino=fecha_actual,
                hora_cita=hora_cita,
                patologia=patologia,
                observaciones=observaciones
            )
            messages.success(request, 'Paciente agregado exitosamente.')
            return redirect('lista_pacientes')
        except Exception as e:
            messages.error(request, f'Error al guardar el paciente: {str(e)}')
    
    context = {
        'medico': 'Dra. Laura Rodríguez',
        'asistente': 'Daniela Sanhueza'
    }
    return render(request, 'core/ingreso_pacientes.html', context)

def login_view(request):
    return render(request, 'core/login.html')  # Asegúrate de que el archivo login.html exista en templates/core/

def lista_pacientes(request):
    # Puedes pasar datos a la plantilla si es necesario
    return render(request, 'core/lista_pacientes.html')

def historial_pacientes(request):
    # Puedes pasar datos a la plantilla si es necesario
    return render(request, 'core/historial_pacientes.html')

def admin_usuarios(request):
    return render(request, 'core/admin_usuarios.html')