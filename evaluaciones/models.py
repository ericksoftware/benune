from django.db import models
from alumnos.models import Alumno

class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    clave = models.CharField(max_length=20, unique=True)
    licenciatura = models.CharField(max_length=50, choices=Alumno.LICENCIATURA_CHOICES)
    semestre = models.PositiveIntegerField()
    creditos = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        ordering = ['semestre', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.get_licenciatura_display()}"

class Calificacion(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    calificacion = models.DecimalField(max_digits=4, decimal_places=2)
    periodo = models.CharField(max_length=20)  # Ej: "2025-1"
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        unique_together = ['alumno', 'materia', 'periodo']
        ordering = ['alumno', 'materia__semestre']
    
    def __str__(self):
        return f"{self.alumno} - {self.materia}: {self.calificacion}"

class ActaEvaluacion(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('generada', 'Generada'),
        ('aprobada', 'Aprobada'),
    ]
    
    licenciatura = models.CharField(max_length=50, choices=Alumno.LICENCIATURA_CHOICES)
    semestre = models.PositiveIntegerField()
    grupo = models.CharField(max_length=10)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    periodo = models.CharField(max_length=20)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_emision = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    archivo_pdf = models.FileField(upload_to='actas/%Y/%m/%d/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Acta de Evaluación'
        verbose_name_plural = 'Actas de Evaluación'
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"Acta {self.materia} - {self.grupo} - {self.periodo}"