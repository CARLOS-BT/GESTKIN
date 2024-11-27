from django import forms
from django.forms.models import inlineformset_factory
from .models import Paciente, Sesion


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'rut', 'cantidad_sesiones', 'patologia', 'observaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad_sesiones': forms.NumberInput(attrs={'class': 'form-control'}),
            'patologia': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

# Inline formset para manejar las sesiones relacionadas
SesionFormSet = inlineformset_factory(
    Paciente,  # Modelo principal
    Sesion,    # Modelo relacionado
    fields=['fecha', 'hora', 'asistio', 'observaciones'],
    extra=0,   # No agregar formularios vacíos automáticamente
    can_delete=False,  # No permitir eliminar sesiones directamente
    widgets={
        'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
    }
)
