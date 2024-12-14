from datetime import datetime

def global_context(request):
    """
    Agrega la fecha, hora actual y nombres de roles al contexto.
    """
    now = datetime.now()
    formatted_date = now.strftime("%A, %d de %B de %Y, %H:%M:%S")  # Formato personalizado
    return {
        'current_datetime': formatted_date,
        'medico': "Laura Rodríguez",
        'asistente': "Daniela Cifuentes",
    }
