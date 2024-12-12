# Librerías de Python estándar
from datetime import datetime, timedelta
import io
import base64
# Librerías de terceros
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template, render_to_string
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf import pisa  # Instala con: pip install xhtml2pdf
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.db.models import Avg, Count, Q
# Importaciones locales (modelos y formularios de la aplicación)
from .models import Paciente, Sesion, ArchivoPaciente
from .forms import PacienteForm
from django.views.decorators.http import require_POST
import matplotlib
matplotlib.use('Agg')  # Configurar backend no interactivo
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Paciente
import re
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from gestkin.core.utils import group_required  # Ajusta la ruta según tu estructura
from django.contrib.auth.forms import AuthenticationForm


@login_required  # Requiere que el usuario esté autenticado
@group_required('grupo_kine', 'grupo_asistente')  # Solo Kinesiologo y Asistente pueden acceder
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

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required  # Requiere que el usuario esté autenticado
@group_required('grupo_kine', 'grupo_asistente')  # Solo Kinesiologo y Asistente pueden acceder
def lista_pacientes(request):
    query = request.GET.get('q', '')  # Término de búsqueda
    sort_by = request.GET.get('sort_by', '-created')  # Orden por defecto: '-created'
    pacientes = Paciente.objects.all().order_by(sort_by)

    # Filtrar por el término de búsqueda
    if query:
        pacientes = pacientes.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(rut__icontains=query)
        )

    # Paginación
    paginator = Paginator(pacientes, 10)  # 10 pacientes por página
    page_number = request.GET.get('page')  # Número de página actual
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)  # Si no es un número, muestra la primera página
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)  # Si está fuera de rango, muestra la última

    context = {
        'query': query,
        'page_obj': page_obj,
        'sort_by': sort_by,
        'no_results': not pacientes.exists()  # Para mostrar mensaje si no hay resultados
    }
    return render(request, 'core/lista_pacientes.html', context)
  

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

""""
   Vista para la pantalla de inicio de sesión.
"""
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Valida los nombres reales de los grupos
            if user.groups.filter(name='grupo_jefe').exists():
                return redirect('estadisticas')
            elif user.groups.filter(name='grupo_kine').exists() or user.groups.filter(name='grupo_asistente').exists():
                return redirect('ingreso_pacientes')
            else:
                messages.error(request, "No tienes permiso para acceder a esta aplicación.")
                return redirect('login')
        else:
            messages.error(request, "Usuario o contraseña incorrectos. Inténtalo de nuevo.")
    else:
        form = AuthenticationForm()

    return render(request, 'core/login.html', {'form': form})

@login_required  # Requiere que el usuario esté autenticado
@group_required('kinesiologo', 'asistente')  # Solo Kinesiologo y Asistente pueden acceder
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


def admin_usuarios(request):
    """
    Vista para la administración de usuarios.
    """
    return render(request, 'core/admin_usuarios.html')


@login_required  # Requiere que el usuario esté autenticado
@group_required('kinesiologo', 'asistente')  # Solo Kinesiologo y Asistente pueden acceder
def eliminar_paciente(request, paciente_id):
    if request.method == 'POST':
        paciente = get_object_or_404(Paciente, id=paciente_id)
        paciente.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})


@login_required  # Requiere que el usuario esté autenticado
@group_required('grupo_kine', 'grupo_asistente')  # Solo Kinesiologo y Asistente pueden acceder
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
@login_required  # Requiere que el usuario esté autenticado
@group_required('grupo_kine', 'grupo_asistente')  # Solo Kinesiologo y Asistente pueden acceder
def eliminar_archivo(request, archivo_id):
    archivo = get_object_or_404(ArchivoPaciente, id=archivo_id)
    paciente_id = archivo.paciente.id  # Guardar el ID del paciente antes de borrar
    archivo.archivo.delete()  # Eliminar el archivo físico
    archivo.delete()  # Eliminar el registro de la base de datos
    messages.success(request, "El archivo se eliminó correctamente.")
    return redirect('detalle_paciente', id=paciente_id)


@login_required  # Requiere que el usuario esté autenticado
@group_required('grupo_kine', 'grupo_asistente')  # Solo Kinesiologo y Asistente pueden acceder
def actualizar_estado_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    nuevo_estado = request.POST.get("estado")
    estados_validos = ["En Proceso", "Terminado", "No Terminado"]
    if nuevo_estado in estados_validos:
        paciente.estado = nuevo_estado
        paciente.save()
    return redirect("lista_pacientes")

@login_required  # Requiere que el usuario esté autenticado
@group_required('grupo_kine', 'grupo_asistente')  # Solo Kinesiologo y Asistente pueden acceder
def eliminar_sesion(request, sesion_id):
    sesion = get_object_or_404(Sesion, id=sesion_id)
    paciente_id = sesion.paciente.id  # Guardar el ID del paciente antes de borrar
    sesion.delete()

    # Actualizar la cantidad de sesiones del paciente
    sesion.paciente.cantidad_sesiones -= 1
    sesion.paciente.save()

    messages.success(request, "Sesión eliminada correctamente.")
    return redirect("detalle_paciente", id=paciente_id)

@login_required  # Requiere que el usuario esté autenticado
@group_required('grupo_kine', 'grupo_asistente')  # Solo Kinesiologo y Asistente pueden acceder
def actualizar_asistencia(request, sesion_id):
    if request.method == "POST":
        sesion = get_object_or_404(Sesion, id=sesion_id)
        asistencia = request.POST.get("asistencia") == "True"
        sesion.asistencia = asistencia
        sesion.save()
        messages.success(request, "La asistencia se actualizó correctamente.")
    return redirect("detalle_paciente", id=sesion.paciente.id)

@login_required  # Requiere que el usuario esté autenticado
@group_required('grupo_kine', 'grupo_asistente')  # Solo Kinesiologo y Asistente pueden acceder
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


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages  # Para mostrar mensajes de error o éxito
from .models import Sesion

@login_required  # Requiere que el usuario esté autenticado
@group_required('grupo_kine', 'grupo_asistente')  # Solo Kinesiologo y Asistente pueden acceder
def editar_sesion(request, sesion_id):
    sesion = get_object_or_404(Sesion, id=sesion_id)

    if request.method == 'POST':
        # Obtener datos del formulario
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        comentario = request.POST.get('comentario')
        asistencia = request.POST.get('asistencia')

        # Validaciones
        errores = {}
        if not fecha:
            errores['fecha'] = "La fecha es obligatoria."
        if not hora:
            errores['hora'] = "La hora es obligatoria."
        if not comentario:
            errores['comentario'] = "El comentario es obligatorio."
        if asistencia not in ['0', '1']:
            errores['asistencia'] = "Selecciona una opción válida para asistencia."

        # Si hay errores, renderizar la página con el modal abierto
        if errores:
            return render(request, 'core/detalle_paciente.html', {
                'paciente': sesion.paciente,
                'sesiones': Sesion.objects.filter(paciente=sesion.paciente),
                'errores': errores,
                'sesion_id': sesion.id  # Para mantener el modal abierto en el frontend
            })

        # Guardar los datos si todo es válido
        sesion.fecha = fecha
        sesion.hora = hora
        sesion.comentario_asistencia = comentario
        sesion.asistencia = asistencia == '1'  # Convierte "1" a True y "0" a False
        sesion.save()

        messages.success(request, "Sesión actualizada exitosamente.")
        return redirect('detalle_paciente', paciente_id=sesion.paciente.id)

    return render(request, 'core/detalle_paciente.html', {'paciente': sesion.paciente})

      # return redirect('detalle_paciente', id=sesion.paciente.id)  # Ajusta esta redirección según tu proyecto 

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
    

def obtener_estadisticas():
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

@login_required  # Requiere que el usuario esté autenticado
@group_required('grupo_kine', 'grupo_asistente', 'grupo_jefe')  # Solo Kinesiologo,Asistente y jefe pueden acceder
def estadisticas(request):
    run = request.GET.get('run', '')
    nombre = request.GET.get('nombre', '')
    estado = request.GET.get('estado', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    # Filtrar pacientes según los criterios de búsqueda
    pacientes = Paciente.objects.all()
    if run:
        pacientes = pacientes.filter(rut__icontains=run)
    if nombre:
        pacientes = pacientes.filter(nombre__icontains=nombre)
    if estado and estado != 'Todas':
        pacientes = pacientes.filter(estado=estado)
    if fecha_inicio and fecha_fin:
        pacientes = pacientes.filter(sesiones__fecha__range=[fecha_inicio, fecha_fin]).distinct()

    # Obtener sesiones asociadas
    sesiones = Sesion.objects.filter(paciente__in=pacientes).order_by('fecha')

    # Calcular estadísticas
    estadisticas_estado = pacientes.values('estado').annotate(total=Count('id'))
    total_pacientes = pacientes.count()
    asistencia_data = {
        "asistieron": sesiones.filter(asistencia=True).count(),
        "no_asistieron": sesiones.filter(asistencia=False).count(),
    }

    # Generar gráfico en base64
    grafico_base64 = generar_grafico(estadisticas_estado)

    # Renderizar plantilla con contexto
    return render(request, 'core/estadisticas.html', {
        "pacientes": pacientes,
        "sesiones": sesiones,
        "estadisticas_estado": estadisticas_estado,
        "asistencia_data": asistencia_data,
        "grafico_base64": grafico_base64,
        "run": run,
        "nombre": nombre,
        "estado": estado,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    })

def generate_chart(estadisticas_estado):
    """
    Genera un gráfico de barras basado en las estadísticas de estado de los pacientes.
    Convierte el gráfico en formato base64 para usarlo en la plantilla HTML.
    """
    labels = [item['estado'] for item in estadisticas_estado]
    values = [item['total'] for item in estadisticas_estado]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, values, color=['#4CAF50', '#FFC107', '#FF5722'])  # Verde, amarillo, rojo
    plt.xlabel('Estado')
    plt.ylabel('Cantidad de Pacientes')
    plt.title('Distribución de Pacientes por Estado')
    plt.tight_layout()

    # Convertir el gráfico a base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    plt.close()

    return image_base64


def generar_grafico(estadisticas_estado):
    """
    Genera un gráfico de barras armonioso y elegante basado en las estadísticas de estado.
    Convierte el gráfico en formato base64 para incrustarlo en una página HTML.
    """
    # Extraer datos de las estadísticas
    estados = [item['estado'] for item in estadisticas_estado]
    totales = [item['total'] for item in estadisticas_estado]

    # Crear la figura y el eje
    fig, ax = plt.subplots(figsize=(8, 5))  # Ajustar tamaño del gráfico

    # Colores armoniosos y grosor de las barras
    color_map = {
        'En Proceso': '#ffc107',  # Amarillo
        'No Terminado': '#dc3545',  # Rojo
        'Terminado': '#28a745'  # Verde
    }
    colors = [color_map[estado] for estado in estados]

    ax.bar(estados, totales, color=colors, width=0.4, edgecolor='black')  # Bordes negros

    # Configuración del diseño
    ax.set_title('Distribución de Pacientes por Estado', fontsize=16, weight='bold')
    ax.set_xlabel('Estado', fontsize=12)
    ax.set_ylabel('Cantidad de Pacientes', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)  # Líneas de guía horizontales sutiles
    ax.tick_params(axis='x', labelsize=10)  # Tamaño de texto en el eje x
    ax.tick_params(axis='y', labelsize=10)  # Tamaño de texto en el eje y

    # Ajustar diseño para evitar cortes
    plt.tight_layout()

    # Convertir el gráfico a base64 para incrustar en HTML
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    plt.close()

    return grafico_base64

def buscar_paciente(request):
    query = request.GET.get('query', '')
    pacientes = Paciente.objects.filter(Q(rut__icontains=query) | Q(nombre__icontains=query))

    # Retornar los datos en formato JSON
    results = [
        {"rut": paciente.rut, "nombre": f"{paciente.nombre} {paciente.apellido}"}
        for paciente in pacientes
    ]
    return JsonResponse(results, safe=False)


def generar_reporte_pdf(request):
    # Obtener filtros desde el request
    run = request.GET.get('run', '')
    nombre = request.GET.get('nombre', '')
    estado = request.GET.get('estado', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    # Filtrar pacientes
    pacientes = Paciente.objects.all()
    if run:
        pacientes = pacientes.filter(rut__icontains=run)
    if nombre:
        pacientes = pacientes.filter(nombre__icontains=nombre)
    if estado and estado != 'Todas':
        pacientes = pacientes.filter(estado=estado)
    if fecha_inicio and fecha_fin:
        pacientes = pacientes.filter(sesiones__fecha__range=[fecha_inicio, fecha_fin]).distinct()

    # Calcular estadísticas generales
    estadisticas_estado = pacientes.values('estado').annotate(total=Count('id'))
    sesiones = Sesion.objects.filter(paciente__in=pacientes)
    asistencia_data = {
        "asistieron": sesiones.filter(asistencia=True).count(),
        "no_asistieron": sesiones.filter(asistencia=False).count(),
    }

    # Crear PDF usando plantilla
    template = get_template('core/reporte_pdf.html')
    context = {
        "estadisticas_estado": estadisticas_estado,
        "asistencia_data": asistencia_data,
        "total_pacientes": pacientes.count(),
        "run": run,
        "nombre": nombre,
        "estado": estado,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }
    html = template.render(context)

    # Generar el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_estadisticas.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Hubo un error al generar el PDF', status=500)
    return response

def descargar_informe(request):
    pacientes = Paciente.objects.all()
    sesiones = Sesion.objects.all()

    # Preparar datos para el informe
    context = {
        'pacientes': pacientes,
        'sesiones': sesiones,
    }

    # Renderizar la plantilla del PDF
    template = render_to_string('core/informe.html', context)

    # Crear el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_pacientes.pdf"'

    pisa_status = pisa.CreatePDF(
        template, dest=response
    )

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    return response


# Función para validar el RUT
def agregar_paciente(request):
    sesiones = []  # Sesiones dinámicas a mostrar en el formulario
    errores = {}   # Errores específicos de los campos

    if request.method == "POST":
        if "actualizar_sesiones" in request.POST:
            # Lógica para actualizar sesiones dinámicas
            cantidad_sesiones = int(request.POST.get("cantidad_sesiones", 0))
            for i in range(cantidad_sesiones):
                sesiones.append({
                    "index": i + 1,
                    "fecha": "",
                    "hora": "",
                })
            
            # Devolver todos los campos previamente ingresados
            return render(request, "core/ingreso_pacientes.html", {
                "sesiones": sesiones,
                "cantidad_sesiones": cantidad_sesiones,
                "nombre": request.POST.get("nombre"),
                "apellido": request.POST.get("apellido"),
                "rut": request.POST.get("rut"),
                "patologia": request.POST.get("patologia"),
                "observaciones": request.POST.get("observaciones"),
            })

        # Datos del formulario
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        rut = request.POST.get("rut")
        cantidad_sesiones = request.POST.get("cantidad_sesiones")
        patologia = request.POST.get("patologia")
        observaciones = request.POST.get("observaciones")

        # Validación de nombre
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nombre):
            errores["nombre"] = "El nombre solo puede contener letras."

        # Validación de apellido
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", apellido):
            errores["apellido"] = "El apellido solo puede contener letras."

        # Validación del RUT
        if not validar_rut(rut):
            errores["rut"] = "El RUN ingresado no es válido. Ejemplo: 12345678-K."

        # Si hay errores, renderizar la página con mensajes de error
        if errores:
            return render(request, "core/ingreso_pacientes.html", {
                "sesiones": sesiones,
                "cantidad_sesiones": cantidad_sesiones,
                "errores": errores,
                "nombre": nombre,
                "apellido": apellido,
                "rut": rut,
                "patologia": patologia,
                "observaciones": observaciones,
            })

        # Crear el paciente
        paciente = Paciente.objects.create(
            nombre=nombre,
            apellido=apellido,
            rut=rut,
            cantidad_sesiones=cantidad_sesiones,
            patologia=patologia,
            observaciones=observaciones,
        )

        # Crear las sesiones si hay datos dinámicos
        for i in range(int(cantidad_sesiones)):
            fecha = request.POST.get(f"fecha_{i + 1}")
            hora = request.POST.get(f"hora_{i + 1}")
            if fecha and hora:
                Sesion.objects.create(
                    paciente=paciente,
                    fecha=fecha,
                    hora=hora
                )

        messages.success(request, "Paciente agregado correctamente.")
        return redirect("detalle_paciente", id=paciente.id)

    return render(request, "core/ingreso_pacientes.html")
