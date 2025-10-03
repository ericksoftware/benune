from django.db import models
from core.fields import EncryptedCharField, EncryptedEmailField

class Alumno(models.Model):
    SEXO_CHOICES = [
        ('hombre', 'Hombre'),
        ('mujer', 'Mujer'),
        ('otro', 'Otro'),
    ]
    
    TURNO_CHOICES = [
        ('matutino', 'Matutino'),
        ('vespertino', 'Vespertino'),
    ]
    
    SI_NO_CHOICES = [
        ('si', 'Sí'),
        ('no', 'No'),
        ('na', 'N/A'),
    ]
    
    # Información básica
    matricula = models.CharField(max_length=20, unique=True)
    curp = EncryptedCharField(max_length=500, default='N/A')  # 500 para cifrado
    rfc = EncryptedCharField(max_length=500, default='N/A')   # 500 para cifrado
    nombre = models.CharField(max_length=200)
    apellido_paterno = models.CharField(max_length=200, default='N/A')
    apellido_materno = models.CharField(max_length=200, default='N/A')
    
    # Información personal
    municipio_nacimiento = models.CharField(max_length=100, default='N/A')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, default='N/A')
    
    # Información académica previa
    institucion_procedencia = models.CharField(max_length=200, default='N/A')
    municipio_institucion = models.CharField(max_length=100, default='N/A')
    clave_escuela = models.CharField(max_length=50, default='N/A')
    fecha_terminacion_prepa = models.DateField(null=True, blank=True)
    promedio_prepa = models.FloatField(null=True, blank=True)
    constancia_terminacion = models.CharField(max_length=2, choices=SI_NO_CHOICES, default='na')
    
    # Información académica actual
    licenciatura = models.CharField(max_length=100, default='N/A')
    promedio_semestre_anterior = models.FloatField(null=True, blank=True)
    semestre_actual = models.PositiveIntegerField(default=1)
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES, default='matutino')
    plan = models.PositiveIntegerField(default=2023)
    
    # Información de contacto
    email_institucional = EncryptedEmailField(default='N/A')
    email_personal = EncryptedEmailField(default='N/A')
    telefono = EncryptedCharField(max_length=500, default='N/A')  # 500 para cifrado
    
    # Metadata
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'
        ordering = ['matricula']
    
    def __str__(self):
        return f"{self.matricula} - {self.nombre}"
    
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"