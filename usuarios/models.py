from django.contrib.auth.models import AbstractUser
from django.db import models
from core.fields import EncryptedCharField, EncryptedEmailField  # Importación corregida

class Usuario(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ('directivo', 'Directivo'),
        ('control_escolar', 'Control Escolar'),
        ('docente', 'Docente'),
        ('alumno', 'Alumno'),
    ]
    
    # Hacer que el username no sea obligatorio ya que usaremos email
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text='Opcional. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.'
    )
    
    tipo_usuario = models.CharField(
        max_length=20, 
        choices=TIPO_USUARIO_CHOICES,
        default='docente'
    )
    
    telefono = EncryptedCharField(max_length=15, blank=True)
    email = EncryptedEmailField(unique=True)  # Ahora está importado correctamente
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Configurar email como campo de autenticación principal
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # username ya no es requerido para login
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name() or self.email} - {self.get_tipo_usuario_display()}"
    
    def get_tipo_usuario_display(self):
        return dict(self.TIPO_USUARIO_CHOICES).get(self.tipo_usuario, self.tipo_usuario)
    
    def save(self, *args, **kwargs):
        # Si no hay username, usar parte del email antes del @
        if not self.username and self.email:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)