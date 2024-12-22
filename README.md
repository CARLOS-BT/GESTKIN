GESTKIN - Sistema de Gestión de Kinesiología
Descripción
GESTKIN es un sistema de gestión especializado para clínicas de kinesiología, desarrollado con Python y tecnologías web modernas. El sistema permite administrar pacientes, sesiones, y seguimiento de tratamientos kinesiológicos.

Características Principales
Gestión de pacientes y sus datos clínicos
Seguimiento de sesiones y asistencias
Registro de observaciones y evolución
Estadísticas y reportes de tratamientos
Interfaz intuitiva y responsive
Tecnologías Utilizadas
Python (96.7%)
HTML (1.1%)
JavaScript (0.9%)
CSS (0.6%)
Otras tecnologías de soporte
Requisitos del Sistema
Python 3.2 o superior
Dependencias listadas en requirements.txt
Navegador web moderno



Instalación
Clonar el repositorio:
git clone https://github.com/CARLOS-BT/GESTKIN.git

Crear y activar entorno virtual:
python -m venv venv
source venv/bin/activate # En Windows: venv\Scripts\activate

Instalar dependencias:
pip install -r requirements.txt
Configurar la base de datos:

Configuración Base de datos:
DATABASES = {
'default': {
'ENGINE': 'django.db.backends.mysql',
'NAME': 'gestkin',
'USER': 'root',
'PASSWORD': '',
'HOST': '127.0.0.1',
'PORT': '3306',
'OPTIONS': {
'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
},
}
}
Migrar a base de datos:
python manage.py makemigrations
python manage.py migrate

Iniciar el servidor:
python manage.py runserver

Uso
Acceder al sistema a través del navegador: http://localhost:8000
Iniciar sesión con las credenciales proporcionadas
Comenzar a gestionar pacientes y sesiones
Ver detalle del los pacientes y gestionarlos.
Crear estadisticas de los pacientes.

Estructura del Proyecto
/gestkin/ - Directorio principal de la aplicación

/venv/ - Entorno virtual de Python
manage.py - Script de gestión de Django
README.md - Documentación del proyecto

Crear una rama para su característica (git checkout -b feature/AmazingFeature)
Commit sus cambios (git commit -m 'Add some AmazingFeature')
Push a la rama (git push origin feature/AmazingFeature)
Abrir un Pull Request
