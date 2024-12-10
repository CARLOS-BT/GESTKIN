from django import forms
from django.forms.models import inlineformset_factory
from .models import Paciente, Sesion, ArchivoPaciente


class PacienteForm(forms.ModelForm):
    """Formulario para el modelo Paciente."""
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'rut', 'observaciones', 'patologia', 'cantidad_sesiones']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),  # Corregido
            'patologia': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),  # Corregido
            'cantidad_sesiones': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class SesionForm(forms.ModelForm):
    """Formulario para el modelo Sesion."""
    class Meta:
        model = Sesion
        fields = ['fecha', 'hora', 'asistencia', 'observaciones', 'comentario_asistencia']  # Incluye ambos campos
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'asistencia': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2 }),  # Corregido
            'comentario_asistencia': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),  # Corregido
        }


SesionFormSet = inlineformset_factory(
    Paciente,
    Sesion,
    form=SesionForm,
    extra=1,
    can_delete=True
)


class ArchivoPacienteForm(forms.ModelForm):
    """Formulario para el modelo ArchivoPaciente."""
    class Meta:
        model = ArchivoPaciente
        fields = ['archivo']
        widgets = {
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }