from django.http import HttpResponse
from django.shortcuts import render


# Agrega la vista admin_usuarios
def admin_usuarios(request):
    return render(request, 'core/admin_usuarios.html')

def login_view(request):
    return render(request, 'core/login.html')

def lista_pacientes(request):
    return render(request, 'core/lista_pacientes.html')

def historial_pacientes(request):
    return render(request, 'core/historial_pacientes.html')

def ingreso_paciente(request):
    return render(request, 'core/ingreso_paciente.html')

