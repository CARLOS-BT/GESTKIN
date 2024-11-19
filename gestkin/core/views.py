from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Paciente
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import PacienteForm

def ingreso_pacientes(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()  # Guardar el paciente en la base de datos
            return redirect('lista_pacientes')  # Redirigir a la lista de pacientes
    else:
        form = PacienteForm()
    return render(request, 'core/ingreso_pacientes.html', {'form': form})

def login_view(request):
    return render(request, 'core/login.html')  # Asegúrate de que el archivo login.html exista en templates/core/

def lista_pacientes(request):
    pacientes = Paciente.objects.all()
    return render(request, 'core/lista_pacientes.html', {'pacientes': pacientes})

def historial_pacientes(request):
    # Puedes pasar datos a la plantilla si es necesario
    return render(request, 'core/historial_pacientes.html')

def admin_usuarios(request):
    return render(request, 'core/admin_usuarios.html')


