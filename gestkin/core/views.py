from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from django.contrib import messages
from .models import Paciente, Sesion
from .forms import PacienteForm, SesionFormSet
from django.shortcuts import render, redirect

def ingreso_pacientes(request):
    if request.method == 'POST':
        # Procesa el formulario del paciente
        paciente_form = PacienteForm(request.POST)
        if paciente_form.is_valid():
            paciente = paciente_form.save()

            # Guarda las sesiones relacionadas
            cantidad_sesiones = paciente.cantidad_sesiones
            for i in range(1, cantidad_sesiones + 1):
                fecha = request.POST.get(f'fecha_{i}')
                hora = request.POST.get(f'hora_{i}')
                if fecha and hora:  # Solo guardar si ambos valores están presentes
                    Sesion.objects.create(
                        paciente=paciente,
                        fecha=fecha,
                        hora=hora
                    )
            return redirect('lista_pacientes')  # Redirige a la lista de pacientes

    else:
        paciente_form = PacienteForm()

    # Maneja la cantidad de sesiones dinámica
    cantidad_sesiones = request.GET.get('cantidad_sesiones', 0)
    try:
        cantidad_sesiones = int(cantidad_sesiones)
    except ValueError:
        cantidad_sesiones = 0

    sesiones = range(1, cantidad_sesiones + 1)
    return render(request, 'core/ingreso_pacientes.html', {
        'form': paciente_form,
        'cantidad_sesiones': cantidad_sesiones,
        'sesiones': sesiones,
    })

def lista_pacientes(request):
    pacientes = Paciente.objects.all()  # Obtener todos los pacientes
    return render(request, 'core/lista_pacientes.html', {'pacientes': pacientes})

def lista_pacientes(request):
    pacientes = Paciente.objects.all()  # Obtener todos los pacientes
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
    sesiones = paciente.sesiones.all()  # Obtener las sesiones relacionadas
    return render(request, 'core/detalle_paciente.html', {
        'paciente': paciente,
        'sesiones': sesiones,
    })