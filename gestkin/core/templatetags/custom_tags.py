from django import template

register = template.Library()
@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    """
    Construye una cadena de consulta (querystring) manteniendo los parámetros existentes
    y actualizando solo los especificados en kwargs.
    """
    request = context['request']
    query = request.GET.copy()

    for key, value in kwargs.items():
        if value is None:  # Elimina el parámetro si el valor es None
            query.pop(key, None)
        else:
            query[key] = value

    return '?' + query.urlencode()
