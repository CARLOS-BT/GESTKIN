from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import formset_factory  # Se usa en algún formulario dinámico
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Avg  # Se usan para las consultas y estadísticas
from django.core.exceptions import ValidationError  # Se usa en la validación de RUT
from django.utils.timezone import now
from .forms import PacienteForm, SesionFormSet, ArchivoPacienteForm
from .models import Paciente, Sesion, ArchivoPaciente
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt  # Para generar el gráfico
import base64  # Para convertir el gráfico a base64
from io import BytesIO  # Manejo de datos en memoria
from PIL import Image  # Para procesar imágenes (gráfico en PDF)
from reportlab.lib.pagesizes import letter  # Tamaño de página para PDF
from reportlab.pdfgen import canvas  # Generar el PDF
from reportlab.platypus import Table, TableStyle  # Crear tablas en ReportLab
from reportlab.lib import colors  # Estilizar tablas en ReportLab
import re  # Para la validación del RUT
import io
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from PIL import Image
# Asegurarse de usar un backend no interactivo para Matplotlib
import matplotlib


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


def eliminar_paciente(request, paciente_id):
    # Obtener el paciente por ID o devolver un error 404 si no existe
    paciente = get_object_or_404(Paciente, id=paciente_id)

    # Eliminar el paciente
    paciente.delete()

    # Redirigir a la lista de pacientes con un mensaje opcional
    return redirect('lista_pacientes')

from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Paciente, Sesion, ArchivoPaciente
from .forms import PacienteForm

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
            comentario_asistencia = request.POST.get("comentario_asistencia", "").strip()  # Nuevo campo para comentarios

            sesion = get_object_or_404(Sesion, id=sesion_id)

            # Validar campos antes de guardar
            if fecha and hora:
                sesion.fecha = fecha
                sesion.hora = hora
                sesion.asistencia = asistencia
                sesion.comentario_asistencia = comentario_asistencia  # Guardar el comentario de asistencia
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



from django.core.exceptions import ValidationError

def calcular_digito_verificador(rut_sin_dv):
    suma = 0
    multiplicador = 2
    for digito in reversed(str(rut_sin_dv)):
        suma += int(digito) * multiplicador
        multiplicador = 9 if multiplicador == 7 else multiplicador + 1
    resto = suma % 11
    dv = 11 - resto
    return "0" if dv == 11 else "k" if dv == 10 else str(dv)

def validar_rut(value):
    # Validar formato general
    if not re.match(r"^\d{7,8}-[0-9kK]$", value):
        raise ValidationError("El RUT ingresado no tiene un formato válido. Ejemplo: 12345678-9")

    # Separar el RUT en número y dígito verificador
    rut, dv = value.split("-")
    if dv.lower() != calcular_digito_verificador(rut):
        raise ValidationError("El dígito verificador del RUT ingresado no es válido.")
    
    from django.db.models import Avg, Count, Q

def obtener_estadisticas():
    from .models import Paciente, Sesion

    total_pacientes = Paciente.objects.count()
    estados_distribucion = Paciente.objects.values("estado").annotate(total=Count("estado"))
    promedio_sesiones = Paciente.objects.aggregate(promedio=Avg("cantidad_sesiones"))["promedio"] or 0
    sesiones_totales = Sesion.objects.count()

    # Porcentaje de asistencia a sesiones
    asistencias = Sesion.objects.filter(asistencia="Asistió").count()
    porcentaje_asistencia = (asistencias / sesiones_totales) * 100 if sesiones_totales else 0

    # Top pacientes con más sesiones
    top_pacientes = Paciente.objects.order_by("-cantidad_sesiones")[:5]

    return {
        "total_pacientes": total_pacientes,
        "estados_distribucion": estados_distribucion,
        "promedio_sesiones": promedio_sesiones,
        "porcentaje_asistencia": porcentaje_asistencia,
        "top_pacientes": top_pacientes,
    }

def estadisticas(request):
    # Obtener filtros
    run = request.GET.get("run", "").strip()
    estado = request.GET.get("estado", "")
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")

    # Aplicar filtros
    pacientes = Paciente.objects.all()
    if run:
        pacientes = pacientes.filter(rut__icontains=run)
    if estado:
        pacientes = pacientes.filter(estado=estado)
    if fecha_inicio and fecha_fin:
        pacientes = pacientes.filter(created__date__range=[fecha_inicio, fecha_fin])

    # Calcular datos para la tabla
    total_pacientes = pacientes.count()
    estados_distribucion = pacientes.values("estado").annotate(total=Count("estado"))
    for estado in estados_distribucion:
        estado["porcentaje"] = (estado["total"] / total_pacientes * 100) if total_pacientes > 0 else 0

    # Ordenar los datos para garantizar el orden de colores
    estado_labels = ["En Proceso", "No Terminado", "Terminado"]
    colores = {"En Proceso": "#FFC107", "No Terminado": "#FF5722", "Terminado": "#4CAF50"}  # Amarillo, Rojo, Verde
    labels = []
    totals = []
    bar_colors = []

    for label in estado_labels:
        estado = next((e for e in estados_distribucion if e["estado"] == label), None)
        if estado:
            labels.append(label)
            totals.append(estado["total"])
            bar_colors.append(colores[label])

    # Generar gráfico con Matplotlib
    plt.figure(figsize=(6, 4))
    plt.bar(labels, totals, color=bar_colors)
    plt.title("Distribución de Pacientes")
    plt.xlabel("Estados")
    plt.ylabel("Total de Pacientes")
    plt.tight_layout()

    # Convertir gráfico a base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    buffer.close()

    # Contexto para la plantilla
    contexto = {
        "filtros": {
            "run": run,
            "estado": estado,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        },
        "estados_distribucion": estados_distribucion,
        "grafico_base64": grafico_base64,
    }
    return render(request, "core/estadisticas.html", contexto)

# Configurar Matplotlib para usar un backend no interactivo
matplotlib.use('Agg')


from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib

# Configurar Matplotlib para usar un backend no interactivo
matplotlib.use('Agg')

def descargar_informe(request):
    # Crear un buffer para el PDF
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)

    # Agregar título
    pdf.setTitle("Informe de Estadísticas")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(300, 770, "Informe de Estadísticas de Pacientes")

    # Texto introductorio
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 730, "Este informe incluye estadísticas de pacientes.")

    # Crear gráfico con Matplotlib
    plt.figure(figsize=(6, 4))
    labels = ["En Proceso", "No Terminado", "Terminado"]
    values = [7, 5, 5]
    colors = ["#FFC107", "#FF5722", "#4CAF50"]
    plt.bar(labels, values, color=colors)
    plt.title("Distribución de Pacientes")
    plt.xlabel("Estado")
    plt.ylabel("Cantidad")
    plt.tight_layout()

    # Guardar el gráfico en un buffer como PNG
    image_buffer = BytesIO()
    plt.savefig(image_buffer, format="PNG")
    plt.close()  # Cerrar la figura de Matplotlib
    image_buffer.seek(0)  # Mover el puntero al inicio del buffer

    # Convertir el buffer a una imagen que ReportLab pueda procesar
    pil_image = Image.open(image_buffer)  # Abrir la imagen en Pillow
    pil_image_rgb = pil_image.convert("RGB")  # Convertir a RGB para compatibilidad
    image_reader = ImageReader(pil_image_rgb)  # Crear un objeto ImageReader para ReportLab

    # Insertar la imagen en el PDF
    pdf.drawImage(image_reader, 100, 500, width=400, height=200)

    # Finalizar y guardar el PDF
    pdf.showPage()
    pdf.save()

    # Preparar respuesta HTTP con el PDF
    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="informe_estadisticas.pdf"'
    return response
