# usuarios/models.py - ACTUALIZADO CON VALIDACIONES
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from core.fields import EncryptedCharField, EncryptedEmailField

class Usuario(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ('directivo', 'Directivo'),
        ('control_escolar', 'Control Escolar'),
        ('docente', 'Docente'),
        ('alumno', 'Alumno'), 
    ]
    
    SEXO_CHOICES = [
        ('hombre', 'Hombre'),
        ('mujer', 'Mujer'),
        ('otro', 'Otro'),
        ('N/A', 'No especificado'),
    ]
    
    TURNO_CHOICES = [
        ('matutino', 'Matutino'),
        ('vespertino', 'Vespertino'),
        ('ambos turnos', 'Ambos turnos'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text='Opcional. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.'
    )
    
    # Información personal adicional
    curp = EncryptedCharField(max_length=500, blank=True, default='N/A')
    rfc = EncryptedCharField(max_length=500, blank=True, default='N/A')
    municipio_nacimiento = models.CharField(max_length=100, blank=True, default='N/A')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, default='N/A')
    
    # Información de usuario
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
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.get_full_name() or self.email} - {self.get_tipo_usuario_display()}"
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip() if full_name.strip() else self.email
    
    def get_apellido_paterno(self):
        """Retorna el apellido paterno"""
        if self.last_name:
            partes = self.last_name.split()
            return partes[0] if len(partes) > 0 else 'N/A'
        return 'N/A'
    
    def get_apellido_materno(self):
        """Retorna el apellido materno"""
        if self.last_name:
            partes = self.last_name.split()
            return partes[1] if len(partes) > 1 else 'N/A'
        return 'N/A'
    
    def get_tipo_usuario_display(self):
        return dict(self.TIPO_USUARIO_CHOICES).get(self.tipo_usuario, self.tipo_usuario)
    
    def get_estado_display(self):
        return "Activo" if self.is_active else "Inactivo"
    
    def clean(self):
        """Validación adicional del modelo - CORREGIDA"""
        from django.core.exceptions import ValidationError
        
        print(f"🔍 EJECUTANDO CLEAN() USUARIO - Email: {self.email}, CURP: {self.curp}, RFC: {self.rfc}")
        
        # Validar que email sea único (excepto cuando es 'N/A' o 'Pendiente')
        if self.email and self.email not in ['N/A', 'Pendiente']:
            # Buscar en TODOS los usuarios para comparar emails descifrados
            for usuario_existente in Usuario.objects.exclude(pk=self.pk):
                if usuario_existente.email == self.email:
                    raise ValidationError({
                        'email': f'El correo institucional "{self.email}" ya le pertenece al usuario: {usuario_existente.get_full_name()}'
                    })
        
        # Validar que CURP sea único (excepto cuando es 'N/A')
        if self.curp and self.curp != 'N/A':
            # Buscar en TODOS los usuarios para comparar CURPs descifradas
            for usuario_existente in Usuario.objects.exclude(pk=self.pk):
                if usuario_existente.curp == self.curp:
                    raise ValidationError({
                        'curp': f'La CURP "{self.curp}" ya le pertenece al usuario: {usuario_existente.get_full_name()}'
                    })
        
        # Validar que RFC sea único (excepto cuando es 'N/A')
        if self.rfc and self.rfc != 'N/A':
            # Buscar en TODOS los usuarios para comparar RFCs descifrados
            for usuario_existente in Usuario.objects.exclude(pk=self.pk):
                if usuario_existente.rfc == self.rfc:
                    raise ValidationError({
                        'rfc': f'El RFC "{self.rfc}" ya le pertenece al usuario: {usuario_existente.get_full_name()}'
                    })
        
        print("✅ CLEAN() USUARIO COMPLETADO SIN ERRORES")
    
    def save(self, *args, **kwargs):
        if not self.username and self.email:
            # Generar username del email si no existe
            self.username = self.email.split('@')[0]
        
        # Asegurar que el email esté en minúsculas
        if self.email:
            self.email = self.email.lower()
        
        # Ejecutar validaciones antes de guardar
        self.full_clean()
            
        super().save(*args, **kwargs)