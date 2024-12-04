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
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ejemplo: 12345678-9'}),
            'cantidad_sesiones': forms.NumberInput(attrs={'class': 'form-control'}),
            'patologia': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
                        
        }

class SesionForm(forms.ModelForm):
    class Meta:
        model = Sesion
        fields = ['fecha', 'hora', 'asistencia', 'observaciones']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'asistencia': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            
        }
SesionFormSet = inlineformset_factory(
    Paciente,
    Sesion,
    form=SesionForm,
    extra=1,
    can_delete=True
)
