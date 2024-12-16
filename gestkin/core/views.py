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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .models import Paciente
from django.http import JsonResponse
from .models import Paciente
import re
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

import re
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Paciente, Sesion
from .forms import PacienteForm
from django.contrib.auth.decorators import login_required
from gestkin.core.utils import group_required  # Ajusta la ruta según tu estructura
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
import re
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Paciente, Sesion
from .forms import PacienteForm
from django.contrib.auth.decorators import login_required
from gestkin.core.utils import group_required  # Ajusta la ruta según tu estructura



from datetime import datetime, timedelta
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Paciente, Sesion
from .forms import PacienteForm
from gestkin.core.utils import group_required  # Ajusta la ruta según tu proyecto


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from .models import Paciente, Sesion
from .forms import PacienteForm
import re

def group_required(*group_names):
    """Decorator to check if the user belongs to any of the specified groups."""
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)
            # Si el usuario no pertenece a ninguno de los grupos, mostrar mensaje de error
            messages.error(request, "No tienes permisos para acceder a esta sección.")
            return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirige a la página anterior
        return _wrapped_view
    return decorator

@login_required
@group_required('grupo_kine', 'grupo_asistente')  # Solo Kinesiologo y Asistente pueden acceder
def ingreso_pacientes(request):
    form = PacienteForm(request.POST or None)
    sesiones = []
    errores = {}

    if request.method == "POST":
        # Obtener los datos del formulario
        nombre = request.POST.get("nombre", "").strip()
        apellido = request.POST.get("apellido", "").strip()
        rut = request.POST.get("rut", "").strip()
        observaciones = request.POST.get("observaciones", "").strip()
        patologia = request.POST.get("patologia", "").strip()
        cantidad_sesiones = request.POST.get("cantidad_sesiones", "0").strip()

        # Validaciones de campos
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]{1,20}$", nombre):
            errores["nombre"] = "El nombre solo puede contener letras y espacios (máximo 20 caracteres)."
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]{1,20}$", apellido):
            errores["apellido"] = "El apellido solo puede contener letras y espacios (máximo 20 caracteres)."
        if not re.match(r"^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]{1,100}$", observaciones):
            errores["observaciones"] = "Las observaciones solo pueden contener letras, números y espacios (máximo 100 caracteres)."
        if not re.match(r"^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]{1,100}$", patologia):
            errores["patologia"] = "La patología solo puede contener letras, números y espacios (máximo 100 caracteres)."

        # Manejar botón "Actualizar" para sesiones dinámicas
        if "actualizar_sesiones" in request.POST:
            cantidad_sesiones = int(cantidad_sesiones) if cantidad_sesiones.isdigit() else 0
            fecha_inicial = datetime.now().date()
            for i in range(cantidad_sesiones):
                sesiones.append({
                    "index": i + 1,
                    "fecha": fecha_inicial + timedelta(days=i * 7),
                    "hora": "09:00",
                })
            return render(request, 'core/ingreso_pacientes.html', {
                'form': form,
                'sesiones': sesiones,
                'errores': errores,
                'nombre': nombre,
                'apellido': apellido,
                'rut': rut,
                'observaciones': observaciones,
                'patologia': patologia,
                'cantidad_sesiones': cantidad_sesiones,
            })

        # Si hay errores, retornar el formulario con los mensajes
        if errores:
            return render(request, 'core/ingreso_pacientes.html', {
                'form': form,
                'sesiones': sesiones,
                'errores': errores,
                'nombre': nombre,
                'apellido': apellido,
                'rut': rut,
                'observaciones': observaciones,
                'patologia': patologia,
                'cantidad_sesiones': cantidad_sesiones,
            })

        # Crear el paciente si no hay errores
        paciente = Paciente.objects.create(
            nombre=nombre,
            apellido=apellido,
            rut=rut,
            observaciones=observaciones,
            patologia=patologia,
        )

        # Crear sesiones automáticamente
        cantidad_sesiones = int(cantidad_sesiones) if cantidad_sesiones.isdigit() else 0
        fecha_inicial = datetime.now().date()
        for i in range(cantidad_sesiones):
            fecha = fecha_inicial + timedelta(days=i * 7)
            Sesion.objects.create(
                paciente=paciente,
                fecha=fecha,
                hora="09:00",
            )

        # Guardar la cantidad de sesiones en el paciente
        paciente.cantidad_sesiones = cantidad_sesiones
        paciente.save()

        messages.success(request, "Paciente y sesiones agregados correctamente.")
        return redirect('detalle_paciente', id=paciente.id)

    return render(request, 'core/ingreso_pacientes.html', {
        'form': form,
        'sesiones': sesiones,
    })


def validar_rut(value):
    """Valida si el RUT es válido."""
    value = value.strip().upper()  # Eliminar espacios y convertir a mayúsculas
    
    # Validar formato general del RUT
    if not re.match(r"^\d{7,8}-[0-9K]$", value):  # Formato: 7-8 dígitos y un dígito verificador
        return False

    # Separar el RUT y el dígito verificador
    rut, dv = value.split("-")
    
    try:
        rut = int(rut)  # Convertir la parte numérica del RUT a entero
    except ValueError:
        return False  # Si no es un número, el RUT no es válido

    # Comparar el dígito verificador calculado con el ingresado
    return dv == calcular_digito_verificador(rut)


def calcular_digito_verificador(rut_sin_dv):
    """Calcula el dígito verificador para un RUT dado."""
    suma = 0
    multiplicador = 2

    # Iterar sobre los dígitos desde el último al primero
    for digito in reversed(str(rut_sin_dv)):
        suma += int(digito) * multiplicador
        multiplicador = 9 if multiplicador == 7 else multiplicador + 1

    resto = suma % 11
    dv = 11 - resto

    # Retornar el dígito verificador correspondiente
    if dv == 11:
        return "0"
    elif dv == 10:
        return "K"
    else:
        return str(dv)



def group_required(*group_names):
    """Decorator to check if the user belongs to any of the specified groups."""
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)
            # Si el usuario no pertenece a ninguno de los grupos, mostrar mensaje de error
            messages.error(request, "No tienes permisos para acceder a esta sección.")
            return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirige a la página anterior
        return _wrapped_view
    return decorator

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
  
from django.shortcuts import redirect

def redirect_to_login(request):
    """Redirige a la página de inicio de sesión."""
    return redirect('login')  # nombre en tu URLconf


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
@group_required('grupo_kine', 'grupo_asistente')  # Solo Kinesiologo y Asistente pueden acceder
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


from django.shortcuts import redirect

@login_required  # Requiere que el usuario esté autenticado
@group_required('grupo_kine')  # Solo Kinesiologo puede acceder
def eliminar_paciente(request, paciente_id):
    if request.method == 'POST':  # Solo aceptar eliminación mediante POST
        paciente = get_object_or_404(Paciente, id=paciente_id)
        paciente.delete()
        messages.success(request, "El paciente fue eliminado exitosamente.")  # Mensaje de confirmación
    else:
        messages.error(request, "Método no permitido para eliminar pacientes.")  # Mensaje de error si no es POST
    return redirect('lista_pacientes')  # Redirige a la lista de pacientes

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
            comentario_asistencia = request.POST.get("comentario_asistencia", "").strip()  # Tomar el comentario y limpiar espacios

            # Si el comentario está vacío, establecer el valor predeterminado "Sin comentarios"
            if not comentario_asistencia:
                comentario_asistencia = "Sin comentarios"

            sesion = get_object_or_404(Sesion, id=sesion_id)

            # Validar campos antes de guardar
            if fecha and hora:
                sesion.fecha = fecha
                sesion.hora = hora
                sesion.asistencia = asistencia
                sesion.comentario_asistencia = comentario_asistencia  # Guardar el comentario
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
                        comentario_asistencia="Sin comentarios"  # Establecer "Sin comentarios" por defecto
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
@group_required('grupo_kine', 'grupo_asistente', 'grupo_jefe')  # todos pueden obtrener estadisticas
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

from django.core.paginator import Paginator

@login_required
@group_required('grupo_kine', 'grupo_asistente', 'grupo_jefe')
def estadisticas(request):
    # Obtener parámetros de filtro
    run = request.GET.get('run', '')
    nombre = request.GET.get('nombre', '')
    estado = request.GET.get('estado', 'Todas')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    # Filtrar pacientes
    pacientes = Paciente.objects.all()
    if run:
        pacientes = pacientes.filter(rut__icontains=run)
    if nombre:
        pacientes = pacientes.filter(Q(nombre__icontains=nombre) | Q(apellido__icontains=nombre))
    if estado and estado != 'Todas':
        pacientes = pacientes.filter(estado=estado)
    if fecha_inicio and fecha_fin:
        pacientes = pacientes.filter(sesiones__fecha__range=[fecha_inicio, fecha_fin]).distinct()

    # Paginación de pacientes
    paciente_paginator = Paginator(pacientes, 30)
    page_number_pacientes = request.GET.get('page_pacientes')
    pacientes_page = paciente_paginator.get_page(page_number_pacientes)

    # Filtrar y paginar sesiones
    sesiones = Sesion.objects.filter(paciente__in=pacientes).order_by('fecha')
    sesion_paginator = Paginator(sesiones, 30)
    page_number_sesiones = request.GET.get('page_sesiones')
    sesiones_page = sesion_paginator.get_page(page_number_sesiones)

    # Calcular estadísticas
    estadisticas_estado = pacientes.values('estado').annotate(total=Count('id'))
    asistencia_data = {
        "asistieron": sesiones.filter(asistencia=True).count(),
        "no_asistieron": sesiones.filter(asistencia=False).count(),
    }

    # Generar gráfico
    grafico_base64 = generate_chart(estadisticas_estado)
    print(f"Base64 del gráfico: {grafico_base64}")  # Depuración

    # Contexto para la plantilla
    context = {
        "pacientes": pacientes_page,  # Pacientes paginados
        "sesiones": sesiones_page,  # Sesiones paginadas
        "estadisticas_estado": estadisticas_estado,
        "asistencia_data": asistencia_data,
        "grafico_base64": grafico_base64,
        "run": run,
        "nombre": nombre,
        "estado": estado,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }

    return render(request, 'core/estadisticas.html', context)


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

def generar_reporte_pdf(request):
    """
    Genera un PDF con el reporte de estadísticas basado en los filtros proporcionados.
    """
    # Obtener filtros desde el request
    run = request.GET.get('run', '')
    nombre = request.GET.get('nombre', '')
    estado = request.GET.get('estado', 'Todas')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    # Filtrar pacientes
    pacientes = Paciente.objects.all()
    if run:
        pacientes = pacientes.filter(rut__icontains=run)
    if nombre:
        pacientes = pacientes.filter(Q(nombre__icontains=nombre) | Q(apellido__icontains=nombre))
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

    # Generar gráfico solo si hay datos en `estadisticas_estado`
    if estadisticas_estado.exists():
        grafico_base64 = generate_chart(estadisticas_estado)
    else:
        grafico_base64 = None

    # Crear PDF usando plantilla
    template = get_template('core/reporte_pdf.html')
    context = {
        "estadisticas_estado": estadisticas_estado,
        "asistencia_data": asistencia_data,
        "total_pacientes": pacientes.count(),
        "sesiones": sesiones,
        "pacientes": pacientes,
        "grafico_base64": grafico_base64,
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


def generate_chart(estadisticas_estado):
    """
    Genera un gráfico de barras basado en las estadísticas de estado de los pacientes.
    Convierte el gráfico en formato base64 para usarlo en el reporte PDF.
    """
    import matplotlib.pyplot as plt
    import io
    import base64

    # Extraer estados y totales
    estados = [item['estado'] for item in estadisticas_estado]
    totales = [item['total'] for item in estadisticas_estado]

    # Configuración del gráfico
    plt.figure(figsize=(8, 5))  # Tamaño del gráfico
    color_map = {
        'En Proceso': '#FFC107',  # Amarillo
        'No Terminado': '#FF5722',  # Rojo
        'Terminado': '#4CAF50'     # Verde
    }
    colores = [color_map.get(estado, '#000000') for estado in estados]  # Color por estado

    # Definir el ancho de las barras para hacerlas más delgadas
    bar_width = 0.4

    # Crear el gráfico de barras con barras delgadas
    plt.bar(estados, totales, color=colores, edgecolor="black", width=bar_width)

    # Etiquetas y título del gráfico
    plt.xlabel('Estado', fontsize=12)
    plt.ylabel('Cantidad de Pacientes', fontsize=12)
    plt.title('Distribución de Pacientes por Estado', fontsize=16, weight='bold')

    # Ajustar el diseño para evitar que los textos se solapen
    plt.tight_layout()

    # Convertir el gráfico a base64 para incrustarlo en HTML o PDF
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    plt.close()

    return image_base64
