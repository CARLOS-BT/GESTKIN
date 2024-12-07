from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from django.contrib import messages
from .models import Paciente
from .forms import PacienteForm, SesionFormSet
from datetime import datetime
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from datetime import date
from .models import Paciente, ArchivoPaciente
from .forms import ArchivoPacienteForm
from django.utils.timezone import now
from datetime import datetime, timedelta
from .models import Sesion

def ingreso_pacientes(request):
    form = PacienteForm(request.POST or None)
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

            # Crear sesiones automáticamente
            cantidad_sesiones = int(request.POST.get("cantidad_sesiones", 0))
            fecha_inicial = datetime.now().date()
            hora_inicial = "09:00"

            for i in range(cantidad_sesiones):
                fecha = request.POST.get(f"fecha_{i + 1}", fecha_inicial + timedelta(days=i * 7))
                hora = request.POST.get(f"hora_{i + 1}", hora_inicial)
                Sesion.objects.create(
                    paciente=paciente,
                    fecha=fecha,
                    hora=hora,
                )
            paciente.cantidad_sesiones = cantidad_sesiones
            paciente.save()  # Guardar el número actualizado de sesiones

            messages.success(request, "Paciente y sesiones agregados correctamente.")
            return redirect('detalle_paciente', id=paciente.id)

    return render(request, 'core/ingreso_pacientes.html', {
        'form': form,
        'sesiones': sesiones,
    })


from django.db.models import Q

def lista_pacientes(request):
    query = request.GET.get('q', '')  # Término de búsqueda
    if query:
        pacientes = Paciente.objects.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(rut__icontains=query)
        ).order_by('-created')
    else:
        pacientes = Paciente.objects.all().order_by('-created')
    return render(request, 'core/lista_pacientes.html', {'pacientes': pacientes, 'query': query})

def login_view(request):
    """
    Vista para la pantalla de inicio de sesión.
    """
    return render(request, 'core/login.html')

def editar_paciente(request, id):
    # Obtener el paciente desde la base de datos
    paciente = get_object_or_404(Paciente, id=id)
    form = PacienteForm(request.POST or None, instance=paciente)

    if request.method == "POST":
        if form.is_valid():
            # Guardar cambios en el paciente
            paciente = form.save(commit=False)

            # Actualizar sesiones dinámicas
            nueva_cantidad = int(request.POST.get("cantidad_sesiones", paciente.cantidad_sesiones))
            sesiones_actuales = Sesion.objects.filter(paciente=paciente).order_by("fecha")
            cantidad_actual = sesiones_actuales.count()

            if nueva_cantidad > cantidad_actual:
                # Agregar nuevas sesiones
                ultima_fecha = sesiones_actuales.last().fecha if sesiones_actuales.exists() else datetime.now().date()
                for i in range(nueva_cantidad - cantidad_actual):
                    nueva_fecha = ultima_fecha + timedelta(days=7 * (i + 1))
                    Sesion.objects.create(
                        paciente=paciente,
                        fecha=nueva_fecha,
                        hora="09:00",  # Hora predeterminada
                        asistencia=False,
                    )
            elif nueva_cantidad < cantidad_actual:
                # Eliminar sesiones sobrantes (solo las que no tienen asistencia)
                sesiones_a_eliminar = sesiones_actuales.filter(asistencia=False)[:cantidad_actual - nueva_cantidad]
                for sesion in sesiones_a_eliminar:
                    sesion.delete()

            # Actualizar la cantidad de sesiones
            paciente.cantidad_sesiones = nueva_cantidad
            paciente.save()

            messages.success(request, "Paciente actualizado correctamente.")
            return redirect('detalle_paciente', id=paciente.id)
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")

    # Renderizar el formulario para la edición
    return render(request, 'core/editar_paciente.html', {
        "form": form,
        "paciente": paciente,
        "sesiones": Sesion.objects.filter(paciente=paciente),
    })

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


def eliminar_paciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    paciente.delete()
    messages.success(request, "Paciente eliminado correctamente.")
    return redirect('lista_pacientes')


from django.core.exceptions import ValidationError

def detalle_paciente(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    sesiones = Sesion.objects.filter(paciente=paciente).order_by("fecha", "hora")
    archivos = paciente.archivos.all()  # Obtener archivos adjuntos del paciente

    if request.method == "POST":
        # Editar sesión
        if "editar_sesion" in request.POST:
            sesion_id = request.POST.get("sesion_id")
            fecha = request.POST.get("fecha")
            hora = request.POST.get("hora")
            asistencia = request.POST.get("asistencia") == "Sí"

            sesion = get_object_or_404(Sesion, id=sesion_id)

            # Validar campos antes de guardar
            if fecha and hora:
                sesion.fecha = fecha
                sesion.hora = hora
                sesion.asistencia = asistencia
                try:
                    sesion.full_clean()  # Validar el modelo antes de guardar
                    sesion.save()
                    messages.success(request, "Sesión actualizada correctamente.")
                except ValidationError as e:
                    messages.error(request, f"Error al actualizar la sesión: {e}")
            else:
                messages.error(request, "La fecha y la hora son obligatorias.")
            
            return redirect("detalle_paciente", id=id)

        # Agregar nuevas sesiones
        elif "agregar_sesiones" in request.POST:
            cantidad_nueva = int(request.POST.get("cantidad_nueva", 0))
            if cantidad_nueva > 0:
                ultima_fecha = sesiones.last().fecha if sesiones.exists() else datetime.now().date()
                for i in range(cantidad_nueva):
                    nueva_fecha = ultima_fecha + timedelta(days=7 * (i + 1))
                    Sesion.objects.create(
                        paciente=paciente,
                        fecha=nueva_fecha,
                        hora="09:00",
                        asistencia=False,
                    )

                # Actualizar la cantidad de sesiones del paciente
                paciente.cantidad_sesiones += cantidad_nueva
                paciente.save()

                messages.success(request, f"{cantidad_nueva} sesión(es) agregadas correctamente.")
                return redirect("detalle_paciente", id=id)

        # Subir archivo
        elif "subir_archivo" in request.POST and "archivo" in request.FILES:
            archivo = request.FILES["archivo"]
            ArchivoPaciente.objects.create(paciente=paciente, archivo=archivo)
            messages.success(request, "Archivo subido correctamente.")
            return redirect("detalle_paciente", id=id)

    # Preparar formulario para editar datos del paciente
    form = PacienteForm(instance=paciente)

    return render(request, "core/detalle_paciente.html", {
        "paciente": paciente,
        "sesiones": sesiones,
        "archivos": archivos,
        "form": form,
    })


def eliminar_archivo(request, archivo_id):
    archivo = get_object_or_404(ArchivoPaciente, id=archivo_id)
    paciente_id = archivo.paciente.id  # Guardar el ID del paciente antes de borrar
    archivo.archivo.delete()  # Eliminar el archivo físico
    archivo.delete()  # Eliminar el registro de la base de datos
    messages.success(request, "El archivo se eliminó correctamente.")
    return redirect('detalle_paciente', id=paciente_id)


@require_POST
def actualizar_estado_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    nuevo_estado = request.POST.get("estado")
    estados_validos = ["En Proceso", "Terminado", "No Terminado"]
    if nuevo_estado in estados_validos:
        paciente.estado = nuevo_estado
        paciente.save()
    return redirect("lista_pacientes")

def eliminar_sesion(request, sesion_id):
    sesion = get_object_or_404(Sesion, id=sesion_id)
    paciente_id = sesion.paciente.id  # Guardar el ID del paciente antes de borrar
    sesion.delete()

    # Actualizar la cantidad de sesiones del paciente
    sesion.paciente.cantidad_sesiones -= 1
    sesion.paciente.save()

    messages.success(request, "Sesión eliminada correctamente.")
    return redirect("detalle_paciente", id=paciente_id)

def actualizar_asistencia(request, sesion_id):
    if request.method == "POST":
        sesion = get_object_or_404(Sesion, id=sesion_id)
        asistencia = request.POST.get("asistencia") == "True"
        sesion.asistencia = asistencia
        sesion.save()
        messages.success(request, "La asistencia se actualizó correctamente.")
    return redirect("detalle_paciente", id=sesion.paciente.id)

def guardar_asistencias(request, paciente_id):
    if request.method == "POST":
        paciente = get_object_or_404(Paciente, id=paciente_id)
        sesiones = Sesion.objects.filter(paciente=paciente)
        for sesion in sesiones:
            asistencia = request.POST.get(f"asistencia_{sesion.id}") == "True"
            sesion.asistencia = asistencia
            sesion.save()
        messages.success(request, "Las asistencias se actualizaron correctamente.")
    return redirect("detalle_paciente", id=paciente_id)
