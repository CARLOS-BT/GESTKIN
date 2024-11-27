# gestkin/core/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    """
    Agrega una clase CSS a un campo de formulario.
    """
    return value.as_widget(attrs={"class": css_class})
