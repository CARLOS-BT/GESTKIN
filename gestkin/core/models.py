from django.db import models

class Paciente(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Paciente")
    apellido = models.CharField(max_length=100, verbose_name="Apellido del Paciente")
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT")
    cantidad_sesiones = models.IntegerField(verbose_name="Cantidad de Sesiones", default=0)
    patologia = models.TextField(verbose_name="Patología", blank=True, null=True)
    observaciones = models.TextField(verbose_name="Observaciones", blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        verbose_name="Estado",
        choices=[("En Proceso", "En Proceso"), ("Terminado", "Terminado")],
        default="En Proceso"
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
    paciente = models.ForeignKey(Paciente, related_name='sesiones', on_delete=models.CASCADE)
    fecha = models.DateField(verbose_name="Fecha de Sesión")
    hora = models.TimeField(verbose_name="Hora de Sesión")
    asistio = models.BooleanField(verbose_name="¿Asistió?", default=False)

    def __str__(self):
        return f"Sesión {self.fecha} - {self.paciente.nombre} {self.paciente.apellido}"
