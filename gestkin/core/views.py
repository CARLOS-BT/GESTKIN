from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from django.contrib import messages
from .models import Paciente, Sesion
from .forms import PacienteForm, SesionFormSet
from datetime import datetime
from django.views.decorators.http import require_POST
from .models import Paciente, Sesion
from .forms import PacienteForm
from django.http import JsonResponse
from datetime import date
from .models import Paciente, ArchivoPaciente
from .forms import ArchivoPacienteForm

def ingreso_pacientes(request):
    form = PacienteForm(request.POST or None)
    cantidad_sesiones = 0
    sesiones = []

    if request.method == "POST":
        print("Datos recibidos en el formulario:", request.POST)

        # Si se presiona "Actualizar Sesiones"
        if "actualizar_sesiones" in request.POST:
            cantidad_sesiones = int(request.POST.get("cantidad_sesiones", 0))
            sesiones = [{"index": i + 1, "fecha": "", "hora": "09:00"} for i in range(cantidad_sesiones)]
            return render(request, 'core/ingreso_pacientes.html', {
                'form': form,
                'cantidad_sesiones': cantidad_sesiones,
                'sesiones': sesiones,
            })

        # Si se guarda el paciente
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.estado = "En Proceso"
            paciente.save()
            print("Paciente guardado:", paciente)

            cantidad_sesiones = int(request.POST.get("cantidad_sesiones", 0))
            for i in range(cantidad_sesiones):
                fecha = request.POST.get(f"fecha_{i + 1}")
                hora = request.POST.get(f"hora_{i + 1}", "09:00")
                if fecha:
                    Sesion.objects.create(
                        paciente=paciente,
                        fecha=fecha,
                        hora=hora
                    )

            # **Actualiza la cantidad de sesiones en el paciente**
            paciente.cantidad_sesiones = cantidad_sesiones
            paciente.save()  # Guarda el número actualizado de sesiones

            return redirect('lista_pacientes')

    return render(request, 'core/ingreso_pacientes.html', {
        'form': form,
        'cantidad_sesiones': cantidad_sesiones,
        'sesiones': sesiones,
    })


def lista_pacientes(request):
    """
    Vista para listar todos los pacientes.
    """
    pacientes = Paciente.objects.all()
    return render(request, 'core/lista_pacientes.html', {'pacientes': pacientes})


def login_view(request):
    """
    Vista para la pantalla de inicio de sesión.
    """
    return render(request, 'core/login.html')


def editar_paciente(request, id):
    """
    Vista para editar un paciente existente.
    """
    paciente = get_object_or_404(Paciente, id=id)
    form = PacienteForm(request.POST or None, instance=paciente)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('lista_pacientes')

    return render(request, 'core/editar_paciente.html', {'form': form, 'paciente': paciente})

def historial_pacientes(request):
    """
    Vista para mostrar el historial de pacientes.
    """
    return render(request, 'core/historial_pacientes.html')


def admin_usuarios(request):
    """
    Vista para la administración de usuarios.
    """
    return render(request, 'core/admin_usuarios.html')


def eliminar_paciente(request, paciente_id):
    """
    Vista para eliminar un paciente.
    """
    paciente = get_object_or_404(Paciente, id=paciente_id)
    paciente.delete()
    return redirect('lista_pacientes')


def detalle_paciente(request, id):
    """
    Vista para mostrar detalles del paciente y permitir la subida de archivos.
    """
    # Obtener el paciente y los archivos relacionados
    paciente = get_object_or_404(Paciente, id=id)
    archivos = paciente.archivos.all()  # Archivos relacionados con el paciente

    # Procesar el formulario de subida de archivos
    if request.method == "POST":
        form = ArchivoPacienteForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.save(commit=False)
            archivo.paciente = paciente  # Asociar el archivo al paciente
            archivo.save()
            return redirect('detalle_paciente', id=paciente.id)
    else:
        form = ArchivoPacienteForm()

    # Renderizar la plantilla
    return render(request, 'core/detalle_paciente.html', {
        'paciente': paciente,
        'archivos': archivos,
        'form': form,
    })

@require_POST
def actualizar_estado_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    nuevo_estado = request.POST.get("estado")
    estados_validos = ["En Proceso", "Terminado", "No Terminado"]
    if nuevo_estado in estados_validos:
        paciente.estado = nuevo_estado
        paciente.save()
    return redirect("lista_pacientes")
