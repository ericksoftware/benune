# evaluaciones/models.py
from django.db import models
from alumnos.models import Alumno

class Licenciatura(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=10, unique=True)
    numero_semestres = models.PositiveIntegerField(default=8)
    plan = models.PositiveIntegerField(default=2023)
    activa = models.BooleanField(default=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Licenciatura'
        verbose_name_plural = 'Licenciaturas'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - Plan {self.plan}"
    
    def get_semestres_range(self):
        """Retorna un rango de semestres para esta licenciatura"""
        return range(1, self.numero_semestres + 1)
    
    def save(self, *args, **kwargs):
        if not self.codigo and self.nombre:
            palabras = self.nombre.split()
            siglas = ''.join([palabra[0].upper() for palabra in palabras if palabra[0].isalpha()])
            self.codigo = siglas[:10]
        
        if self.codigo:
            counter = 1
            original_codigo = self.codigo
            while Licenciatura.objects.filter(codigo=self.codigo).exclude(pk=self.pk).exists():
                self.codigo = f"{original_codigo}{counter}"
                counter += 1
        
        super().save(*args, **kwargs)

class Unidad(models.Model):
    licenciatura = models.ForeignKey(Licenciatura, on_delete=models.CASCADE, related_name='unidades')
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=100, default='')  # Hacer el nombre opcional
    numero = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'
        unique_together = ['licenciatura', 'codigo']
        ordering = ['licenciatura', 'numero']
    
    def __str__(self):
        return self.codigo  # Solo mostrar el código
    
    def save(self, *args, **kwargs):
        if not self.codigo and self.licenciatura:
            año_plan = str(self.licenciatura.plan)[-2:]
            numero_str = str(self.numero).zfill(2)
            self.codigo = f"{self.licenciatura.codigo}{año_plan}{numero_str}"
        
        # Si no se proporciona nombre, usar el código
        if not self.nombre:
            self.nombre = f"Unidad {self.numero}"
        
        if self.codigo:
            counter = 1
            original_codigo = self.codigo
            while Unidad.objects.filter(codigo=self.codigo).exclude(pk=self.pk).exists():
                self.codigo = f"{original_codigo}_{counter}"
                counter += 1
        
        super().save(*args, **kwargs)

class Materia(models.Model):
    licenciatura = models.ForeignKey(Licenciatura, on_delete=models.CASCADE)
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE, related_name='materias')
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    semestre = models.PositiveIntegerField()
    creditos = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        ordering = ['licenciatura', 'semestre', 'codigo']
        unique_together = ['licenciatura', 'codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        if not self.unidad and self.licenciatura:
            unidad_default = Unidad.objects.filter(licenciatura=self.licenciatura).first()
            if not unidad_default:
                año_plan = str(self.licenciatura.plan)[-2:]
                unidad_default = Unidad.objects.create(
                    licenciatura=self.licenciatura,
                    numero=1,
                    nombre='Unidad Principal',
                    codigo=f"{self.licenciatura.codigo}{año_plan}01"
                )
            self.unidad = unidad_default
        
        if not self.codigo and self.licenciatura and self.unidad:
            materias_semestre = Materia.objects.filter(
                licenciatura=self.licenciatura, 
                semestre=self.semestre,
                unidad=self.unidad
            ).count()
            numero = str(materias_semestre + 1).zfill(2)
            self.codigo = f"{self.unidad.codigo}{numero}"
        
        super().save(*args, **kwargs)

class Calificacion(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    calificacion = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    periodo = models.CharField(max_length=20)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        unique_together = ['alumno', 'materia', 'periodo']
        ordering = ['alumno', 'materia__semestre', 'materia__codigo']
    
    def __str__(self):
        calif = self.calificacion if self.calificacion else "N/A"
        return f"{self.alumno.matricula} - {self.materia.codigo}: {calif}"

class PromedioPeriodo(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    periodo = models.CharField(max_length=20)
    promedio_general = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total_materias = models.IntegerField(default=0)
    materias_cursadas = models.IntegerField(default=0)
    materias_aprobadas = models.IntegerField(default=0)
    
    fecha_calculo = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Promedio de Periodo'
        verbose_name_plural = 'Promedios de Periodo'
        unique_together = ['alumno', 'periodo']
        ordering = ['alumno', 'periodo']
    
    def __str__(self):
        return f"{self.alumno.matricula} - {self.periodo} - {self.promedio_general}"
    
    def calcular_promedio(self):
        calificaciones = Calificacion.objects.filter(
            alumno=self.alumno,
            periodo=self.periodo
        ).exclude(calificacion__isnull=True)
        
        if calificaciones.exists():
            total_calificaciones = sum(calif.calificacion for calif in calificaciones)
            self.promedio_general = total_calificaciones / calificaciones.count()
            self.total_materias = calificaciones.count()
            self.materias_cursadas = calificaciones.count()
            self.materias_aprobadas = calificaciones.filter(calificacion__gte=6).count()
            self.save()

class ActaEvaluacion(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('generada', 'Generada'),
        ('aprobada', 'Aprobada'),
        ('cerrada', 'Cerrada'),
    ]
    
    licenciatura = models.ForeignKey(Licenciatura, on_delete=models.CASCADE)
    semestre = models.PositiveIntegerField()
    grupo = models.CharField(max_length=10)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    periodo = models.CharField(max_length=20)
    
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_emision = models.DateField()
    generada_por = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    archivo_pdf = models.FileField(upload_to='actas/%Y/%m/%d/', blank=True, null=True)
    
    total_alumnos = models.IntegerField(default=0)
    alumnos_evaluados = models.IntegerField(default=0)
    promedio_grupo = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    
    class Meta:
        verbose_name = 'Acta de Evaluación'
        verbose_name_plural = 'Actas de Evaluación'
        ordering = ['-fecha_generacion']
        unique_together = ['materia', 'grupo', 'periodo']
    
    def __str__(self):
        return f"Acta {self.materia.codigo} - {self.grupo} - {self.periodo}"
    
    def calcular_estadisticas(self):
        calificaciones = Calificacion.objects.filter(
            materia=self.materia,
            periodo=self.periodo
        ).exclude(calificacion__isnull=True)
        
        self.total_alumnos = calificaciones.count()
        self.alumnos_evaluados = calificaciones.exclude(calificacion__isnull=True).count()
        
        if calificaciones.exists():
            total_calificaciones = sum(calif.calificacion for calif in calificaciones)
            self.promedio_grupo = total_calificaciones / calificaciones.count()
        
        self.save()