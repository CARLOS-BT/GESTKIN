from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestkin.core'  # Importa la aplicación con la ruta completa
