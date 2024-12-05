from django import forms
from django.forms.models import inlineformset_factory
from .models import Paciente, Sesion
from django import forms
from .models import Paciente
from .models import ArchivoPaciente

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'rut', 'observaciones', 'patologia']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control'}),
            'patologia': forms.Textarea(attrs={'class': 'form-control'}),
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

class ArchivoPacienteForm(forms.ModelForm):
    class Meta:
        model = ArchivoPaciente
        fields = ['archivo']