from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ('directivo', 'Directivo'),
        ('control_escolar', 'Control Escolar'),
        ('docente', 'Docente'),
        ('alumno', 'Alumno'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=20, 
        choices=TIPO_USUARIO_CHOICES,
        default='docente'
    )
    telefono = models.CharField(max_length=15, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.get_tipo_usuario_display()}"
    
    def get_tipo_usuario_display(self):
        return dict(self.TIPO_USUARIO_CHOICES).get(self.tipo_usuario, self.tipo_usuario)