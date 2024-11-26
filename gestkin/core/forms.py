from django import forms
from .models import Paciente, Sesion
from django.forms import modelformset_factory

from django import forms
from .models import Paciente

from django import forms
from .models import Paciente, Sesion

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'rut', 'cantidad_sesiones', 'patologia', 'observaciones']

class SesionForm(forms.ModelForm):
    class Meta:
        model = Sesion
        fields = ['fecha', 'hora', 'asistio']


SesionFormSet = modelformset_factory(Sesion, form=SesionForm, extra=0)
