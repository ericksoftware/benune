from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from core.decorators import control_escolar_required
from .models import Calificacion, Materia, ActaEvaluacion
from alumnos.models import Alumno
import pandas as pd
import os
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db import models

@login_required
def grade_list(request):
    """Lista de calificaciones"""
    calificaciones = Calificacion.objects.all().select_related('alumno', 'materia')
    
    # Filtrar por parámetros GET
    licenciatura = request.GET.get('licenciatura')
    semestre = request.GET.get('semestre')
    materia_id = request.GET.get('materia')
    
    if licenciatura:
        calificaciones = calificaciones.filter(alumno__licenciatura=licenciatura)
    if semestre:
        calificaciones = calificaciones.filter(alumno__semestre_actual=semestre)
    if materia_id:
        calificaciones = calificaciones.filter(materia_id=materia_id)
    
    materias = Materia.objects.all()
    
    context = {
        'calificaciones': calificaciones,
        'materias': materias,
        'licenciatura_filter': licenciatura,
        'semestre_filter': semestre,
        'materia_filter': materia_id,
        'page_title': 'Lista de Calificaciones'
    }
    return render(request, 'evaluaciones/grade_list.html', context)

@control_escolar_required
def import_grades(request):
    """Importar calificaciones desde Excel"""
    if request.method == 'POST':
        try:
            excel_file = request.FILES['excel_file']
            licenciatura = request.POST['licenciatura']
            semestre = request.POST['semestre']
            
            # Leer el archivo Excel
            df = pd.read_excel(excel_file)
            
            # Validar columnas requeridas
            required_columns = ['MATRICULA', 'MATERIA', 'CALIFICACION']
            for col in required_columns:
                if col not in df.columns:
                    messages.error(request, f'Falta la columna requerida: {col}')
                    return redirect('import_grades')
            
            # Procesar cada fila
            success_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    matricula = str(row['MATRICULA']).strip()
                    nombre_materia = str(row['MATERIA']).strip()
                    calificacion_val = float(row['CALIFICACION'])
                    
                    # Buscar alumno y materia
                    alumno = Alumno.objects.get(matricula=matricula)
                    materia = Materia.objects.get(nombre=nombre_materia)
                    
                    # Crear o actualizar calificación
                    calificacion, created = Calificacion.objects.update_or_create(
                        alumno=alumno,
                        materia=materia,
                        periodo=f"2025-{semestre}",
                        defaults={'calificacion': calificacion_val}
                    )
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Error en fila {index + 2}: {e}")
            
            messages.success(request, f'Importación completada: {success_count} registros exitosos, {error_count} errores')
            return redirect('grade_list')
            
        except Exception as e:
            messages.error(request, f'Error al importar el archivo: {str(e)}')
    
    # Si es GET, mostrar el formulario
    context = {
        'page_title': 'Importar Calificaciones'
    }
    return render(request, 'evaluaciones/import_grades.html', context)

@control_escolar_required
def generate_transcript(request):
    """Generar acta de evaluación"""
    if request.method == 'POST':
        try:
            licenciatura = request.POST['licenciatura']
            semestre = request.POST['semestre']
            grupo = request.POST['grupo']
            materia_id = request.POST['materia']
            periodo = request.POST['periodo']
            fecha_emision = request.POST['fecha_emision']
            
            materia = Materia.objects.get(id=materia_id)
            
            # Crear el acta
            acta = ActaEvaluacion.objects.create(
                licenciatura=licenciatura,
                semestre=semestre,
                grupo=grupo,
                materia=materia,
                periodo=periodo,
                fecha_emision=fecha_emision,
                estado='generada'
            )
            
            # Obtener calificaciones para este acta
            calificaciones = Calificacion.objects.filter(
                alumno__licenciatura=licenciatura,
                alumno__semestre_actual=semestre,
                materia=materia,
                periodo=periodo
            ).select_related('alumno')
            
            # Generar PDF
            html_string = render_to_string('evaluaciones/transcript_template.html', {
                'acta': acta,
                'calificaciones': calificaciones,
                'total_alumnos': calificaciones.count(),
                'promedio_grupo': calificaciones.aggregate(avg=models.Avg('calificacion'))['calificacion__avg'] or 0
            })
            
            html = HTML(string=html_string)
            result = html.write_pdf()
            
            # Guardar el PDF
            pdf_path = f'actas/{acta.id}_{acta.materia.clave}_{acta.grupo}.pdf'
            full_path = os.path.join(settings.MEDIA_ROOT, pdf_path)
            
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'wb') as f:
                f.write(result)
            
            acta.archivo_pdf = pdf_path
            acta.save()
            
            messages.success(request, f'Acta generada exitosamente para {materia.nombre}')
            return redirect('view_transcript', transcript_id=acta.id)
            
        except Exception as e:
            messages.error(request, f'Error al generar el acta: {str(e)}')
    
    # Si es GET, mostrar el formulario
    materias = Materia.objects.all()
    
    context = {
        'materias': materias,
        'page_title': 'Generar Acta de Evaluación'
    }
    return render(request, 'evaluaciones/generate_transcript.html', context)

@login_required
def view_transcript(request, transcript_id):
    """Ver un acta de evaluación específica"""
    acta = get_object_or_404(ActaEvaluacion, id=transcript_id)
    calificaciones = Calificacion.objects.filter(
        alumno__licenciatura=acta.licenciatura,
        alumno__semestre_actual=acta.semestre,
        materia=acta.materia,
        periodo=acta.periodo
    ).select_related('alumno')
    
    context = {
        'acta': acta,
        'calificaciones': calificaciones,
        'total_alumnos': calificaciones.count(),
        'promedio_grupo': calificaciones.aggregate(avg=models.Avg('calificacion'))['calificacion__avg'] or 0,
        'page_title': f'Acta de {acta.materia.nombre}'
    }
    return render(request, 'evaluaciones/view_transcript.html', context)

@control_escolar_required
def download_transcript(request, transcript_id):
    """Descargar un acta en PDF"""
    acta = get_object_or_404(ActaEvaluacion, id=transcript_id)
    
    if acta.archivo_pdf:
        file_path = acta.archivo_pdf.path
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="acta_{acta.materia.clave}_{acta.grupo}.pdf"'
            return response
    
    messages.error(request, 'El archivo PDF no está disponible')
    return redirect('view_transcript', transcript_id=transcript_id)