from django.db import models
from django.core.exceptions import ValidationError
import re
from datetime import date

def validar_rut(value):
 #   if not re.match(r"^\d{7,8}-[0-9kK]$", value):
  #      raise ValidationError("El RUT ingresado no tiene un formato válido. Ejemplo: 12345678-9")
  pass

class Paciente(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Paciente")
    apellido = models.CharField(max_length=100, verbose_name="Apellido del Paciente")
    rut = models.CharField(
        max_length=12, unique=True, verbose_name="RUT", validators=[validar_rut]
    )
    cantidad_sesiones = models.IntegerField(verbose_name="Cantidad de Sesiones", default=0)
    patologia = models.TextField(verbose_name="Patología", blank=True, null=True)
    observaciones = models.TextField(verbose_name="Observaciones", blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        choices=[("En Proceso", "En Proceso"), ("Terminado", "Terminado")],
        default="En Proceso",  # Valor predeterminado
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['-created']

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rut})"


class Sesion(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='sesiones', verbose_name="Paciente")
    fecha = models.DateField(verbose_name="Fecha de la Sesión", default=date.today)
    hora = models.TimeField(verbose_name="Hora de la Sesión", default="00:00")
    asistencia = models.BooleanField(default=False, verbose_name="Asistencia")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    estado = models.CharField(
        max_length=20,
        choices=[
            ('En Proceso', 'En Proceso'),
            ('Terminado', 'Terminado'),
            ('No Terminado', 'No Terminado'),
        ],
        default='En Proceso',
    )

    class Meta:
        verbose_name = "Sesión"
        verbose_name_plural = "Sesiones"
        ordering = ['fecha', 'hora']

    def __str__(self):
        return f"Sesión de {self.paciente.nombre} el {self.fecha} a las {self.hora}"
