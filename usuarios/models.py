from django.contrib.auth.models import AbstractUser
from django.db import models
from core.fields import EncryptedCharField, EncryptedEmailField

class Usuario(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ('directivo', 'Directivo'),
        ('control_escolar', 'Control Escolar'),
        ('docente', 'Docente'),
    ]
    
    TURNO_CHOICES = [
        ('matutino', 'Matutino'),
        ('vespertino', 'Vespertino'),
    ]
    
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
    
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES, default='matutino')
    
    # Campos cifrados con tamaño seguro
    telefono = EncryptedCharField(max_length=500, blank=True, default='N/A')
    email = EncryptedEmailField(unique=True)
    email_personal = EncryptedEmailField(blank=True, default='N/A')
    
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name() or self.email} - {self.get_tipo_usuario_display()}"
    
    def get_tipo_usuario_display(self):
        return dict(self.TIPO_USUARIO_CHOICES).get(self.tipo_usuario, self.tipo_usuario)
    
    def save(self, *args, **kwargs):
        if not self.username and self.email:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)