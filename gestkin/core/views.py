from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from django.contrib import messages
from .models import Paciente, Sesion
from .forms import PacienteForm, SesionFormSet
from django.shortcuts import render, redirect

from datetime import datetime, timedelta

def ingreso_pacientes(request):
    if request.method == "POST":
        form = PacienteForm(request.POST)

        # Manejo del botón "Actualizar Sesiones"
        if 'actualizar_sesiones' in request.POST:
            cantidad_sesiones = int(request.POST.get("cantidad_sesiones", 0))

            # Genera las fechas y horas para las sesiones
            sesiones = []
            hoy = datetime.now().date()
            for i in range(1, cantidad_sesiones + 1):
                fecha = hoy + timedelta(days=(i - 1) * 7)  # Incremento semanal
                sesiones.append({'index': i, 'fecha': fecha, 'hora': '09:00'})

            # Mantiene el formulario con los datos actuales
            return render(request, 'core/ingreso_pacientes.html', {
                'form': form,
                'cantidad_sesiones': cantidad_sesiones,
                'sesiones': sesiones
            })

        # Guardar paciente y sus sesiones
        elif form.is_valid():
            paciente = form.save()

            # Crear las sesiones
            for i in range(paciente.cantidad_sesiones):
                Sesion.objects.create(paciente=paciente)
            
            return redirect('lista_pacientes')

    else:
        form = PacienteForm()

    # Caso inicial sin sesiones generadas
    return render(request, 'core/ingreso_pacientes.html', {
        'form': form,
        'cantidad_sesiones': 0,
        'sesiones': []
    })
def lista_pacientes(request):
    pacientes = Paciente.objects.all()
    return render(request, 'core/lista_pacientes.html', {'pacientes': pacientes})

def login_view(request):
    return render(request, 'core/login.html')  # Asegúrate de que el archivo login.html exista en templates/core/

# gestkin/core/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Paciente

def lista_pacientes(request):
    pacientes = Paciente.objects.all()
    return render(request, 'core/lista_pacientes.html', {
        'pacientes': pacientes
    })

def editar_paciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    if request.method == 'POST':
        paciente.nombre = request.POST['nombre']
        paciente.apellido = request.POST['apellido']
        paciente.rut = request.POST['rut']
        paciente.cantidad_sesiones = request.POST['cantidad_sesiones']
        paciente.fecha_inicio = request.POST['fecha_inicio']
        paciente.fecha_termino = request.POST.get('fecha_termino', None)
        paciente.hora_cita = request.POST['hora_cita']
        paciente.patologia = request.POST['patologia']
        paciente.observaciones = request.POST['observaciones']
        paciente.save()
        return redirect('lista_pacientes')

    return render(request, 'core/editar_paciente.html', {'paciente': paciente})

def historial_pacientes(request):
    # Puedes pasar datos a la plantilla si es necesario
    return render(request, 'core/historial_pacientes.html')

def admin_usuarios(request):
    return render(request, 'core/admin_usuarios.html')

def eliminar_paciente(request, paciente_id):
    # Obtén el paciente con el ID especificado o lanza un 404 si no existe
    paciente = get_object_or_404(Paciente, id=paciente_id)
    # Elimina el paciente
    paciente.delete()
    # Redirige a la lista de pacientes tras la eliminación
    return redirect('lista_pacientes')  # Ajusta 'lista_pacientes' si tu URL tiene otro nombre

def detalle_paciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    sesiones_formset = SesionFormSet(instance=paciente)

    if request.method == "POST":
        sesiones_formset = SesionFormSet(request.POST, instance=paciente)
        if sesiones_formset.is_valid():
            sesiones_formset.save()
            return redirect('detalle_paciente', id=paciente.id)

    return render(request, 'core/detalle_paciente.html', {
        'paciente': paciente,
        'sesiones_formset': sesiones_formset,
    })
