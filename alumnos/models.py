from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.fields import EncryptedCharField, EncryptedEmailField, EncryptedTextField

class Alumno(models.Model):
    SEXO_CHOICES = [
        ('HOMBRE', 'Hombre'),
        ('MUJER', 'Mujer'),
    ]
    
    TURNO_CHOICES = [
        ('MATUTINO', 'Matutino'),
        ('VESPERTINO', 'Vespertino'),
    ]
    
    LICENCIATURA_CHOICES = [
        ('EDUCACION_ESPECIAL', 'Licenciatura en Educación Especial'),
        ('INCLUSION_EDUCATIVA', 'Licenciatura en Inclusión Educativa'),
    ]
    
    # Información personal (CIFRADA)
    curp = EncryptedCharField(max_length=255, unique=True, verbose_name='CURP')  # ⬅ 18 → 255
    nombre = EncryptedCharField(max_length=255)  # ⬅ 100 → 255
    apellido_paterno = EncryptedCharField(max_length=255)  # ⬅ 100 → 255
    apellido_materno = EncryptedCharField(max_length=255)  # ⬅ 100 → 255
    municipio_estado_nacimiento = EncryptedCharField(max_length=255)  # ⬅ 100 → 255
    
    # Información personal (NO CIFRADA - menos sensible)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES)
    fecha_nacimiento = models.DateField()
    
    # Información académica (NO CIFRADA - datos públicos)
    matricula = models.CharField(max_length=20, unique=True, blank=True, null=True)
    licenciatura = models.CharField(max_length=50, choices=LICENCIATURA_CHOICES)
    semestre_actual = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES)
    promedio_prepa = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    
    # Información de contacto (CIFRADA)
    institucion_procedencia = EncryptedCharField(max_length=500)  # ⬅ 200 → 500
    correo_particular = EncryptedEmailField(blank=True, null=True)  # ✅ 254 is good (kept from parent)
    numero_celular = EncryptedCharField(max_length=255, blank=True, null=True)  # ⬅ 15 → 255
    
    # Metadatos (NO CIFRADOS)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'
        ordering = ['apellido_paterno', 'apellido_materno', 'nombre']
    
    def __str__(self):
        return f"{self.nombre_completo} - {self.matricula}"
    
    @property
    def nombre_completo(self):
        return f"{self.apellido_paterno} {self.apellido_materno} {self.nombre}"
    
    def save(self, *args, **kwargs):
        # Generar matrícula automáticamente si no existe
        if not self.matricula:
            # Lógica para generar matrícula (puedes personalizar esto)
            from django.utils import timezone
            year = timezone.now().year % 100
            base_matricula = f"{year}{self.licenciatura[:2].upper()}{self.semestre_actual:02d}"
            
            # Buscar el siguiente número disponible
            last_alumno = Alumno.objects.filter(
                matricula__startswith=base_matricula
            ).order_by('-matricula').first()
            
            if last_alumno and last_alumno.matricula:
                try:
                    last_number = int(last_alumno.matricula[-4:])
                    next_number = last_number + 1
                except ValueError:
                    next_number = 1
            else:
                next_number = 1
                
            self.matricula = f"{base_matricula}{next_number:04d}"
        
        super().save(*args, **kwargs)
    
    def get_sexo_display(self):
        return dict(self.SEXO_CHOICES).get(self.sexo, self.sexo)
    
    def get_turno_display(self):
        return dict(self.TURNO_CHOICES).get(self.turno, self.turno)
    
    def get_licenciatura_display(self):
        return dict(self.LICENCIATURA_CHOICES).get(self.licenciatura, self.licenciatura)
    
    def get_semestre_actual_display(self):
        semestres = {
            1: 'Primero', 2: 'Segundo', 3: 'Tercero', 4: 'Cuarto',
            5: 'Quinto', 6: 'Sexto', 7: 'Séptimo', 8: 'Octavo'
        }
        return semestres.get(self.semestre_actual, f'Semestre {self.semestre_actual}')