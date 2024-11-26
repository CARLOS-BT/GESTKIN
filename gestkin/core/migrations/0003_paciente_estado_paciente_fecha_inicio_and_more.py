# Generated by Django 4.2 on 2024-11-25 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_paciente_fecha_inicio_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='estado',
            field=models.CharField(choices=[('En Proceso', 'En Proceso'), ('Terminado', 'Terminado')], default='En Proceso', max_length=20, verbose_name='Estado'),
        ),
        migrations.AddField(
            model_name='paciente',
            name='fecha_inicio',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de Inicio'),
        ),
        migrations.AddField(
            model_name='paciente',
            name='fecha_termino',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de Término'),
        ),
        migrations.AlterField(
            model_name='paciente',
            name='observaciones',
            field=models.TextField(blank=True, null=True, verbose_name='Observaciones'),
        ),
        migrations.AlterField(
            model_name='paciente',
            name='patologia',
            field=models.TextField(blank=True, null=True, verbose_name='Patología'),
        ),
    ]
