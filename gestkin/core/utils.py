# gestkin/core/utils.py


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def group_required(*group_names):
    """
    Decorador para restringir acceso a usuarios pertenecientes a ciertos grupos.
    Si el usuario no pertenece a los grupos permitidos, será redirigido.
    """
    def in_groups(user):
        # Asegúrate de que el usuario esté autenticado
        if not user.is_authenticated:
            return False
        # Verifica si el usuario pertenece a uno de los grupos permitidos
        if user.groups.filter(name__in=group_names).exists() or user.is_superuser:
            return True
        return False

    return user_passes_test(in_groups, login_url='/login/')  # Cambia el login_url si es necesario



