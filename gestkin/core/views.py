from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Paciente
from datetime import datetime, timedelta
from django.http import HttpResponse
from .forms import PacienteForm

def ingreso_pacientes(request):
    form = PacienteForm(request.POST or None)
    pacientes = Paciente.objects.all()  # Obtiene todos los pacientes desde la base de datos

    if form.is_valid():
        form.save()
        return redirect('lista_pacientes')

    # Renderiza la plantilla con el formulario y la lista de pacientes
    return render(request, 'core/ingreso_pacientes.html', {
        'form': form,
        'pacientes': pacientes  # Pasa los pacientes al template
    })

def login_view(request):
    return render(request, 'core/login.html')  # Asegúrate de que el archivo login.html exista en templates/core/

# gestkin/core/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Paciente

def lista_pacientes(request):
    pacientes = Paciente.objects.all()
    return render(request, 'core/lista_pacientes.html', {'pacientes': pacientes})

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


