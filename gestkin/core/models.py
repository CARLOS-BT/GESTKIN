from django.db import models

class Paciente(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Paciente")
    apellido = models.CharField(max_length=100, verbose_name="Apellido del Paciente")
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT")
    cantidad_sesiones = models.IntegerField(verbose_name="Cantidad de Sesiones")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_termino = models.DateField(verbose_name="Fecha de Término", blank=True, null=True)
    hora_cita = models.TimeField(verbose_name="Hora de la Cita")
    patologia = models.TextField(verbose_name="Patología", blank=True)
    observaciones = models.TextField(verbose_name="Observaciones", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['-created']

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.rut}"