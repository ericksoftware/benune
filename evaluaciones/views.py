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
from .models import Licenciatura, Unidad

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
                    codigo_materia = str(row['MATERIA']).strip()  # Cambiar nombre por código
                    calificacion_val = float(row['CALIFICACION'])
                    
                    alumno = Alumno.objects.get(matricula=matricula)
                    materia = Materia.objects.get(codigo=codigo_materia)
                    
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
            pdf_path = f'actas/{acta.id}_{acta.materia.codigo}_{acta.grupo}.pdf'
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
            response['Content-Disposition'] = f'attachment; filename="acta_{acta.materia.codigo}_{acta.grupo}.pdf"'
            return response
    
    messages.error(request, 'El archivo PDF no está disponible')
    return redirect('view_transcript', transcript_id=transcript_id)

# evaluaciones/views.py - Agrega estas vistas

@control_escolar_required
def lista_licenciaturas(request):
    """Lista todas las licenciaturas"""
    licenciaturas = Licenciatura.objects.all().order_by('id')  # Ordenar por ID de menor a mayor
    
    context = {
        'licenciaturas': licenciaturas,
        'page_title': 'Gestión de Licenciaturas'
    }
    return render(request, 'evaluaciones/licenciaturas/lista_licenciaturas.html', context)

@control_escolar_required
def agregar_licenciatura(request):
    """Agregar una nueva licenciatura"""
    if request.method == 'POST':
        try:
            nombre = request.POST['nombre']
            numero_semestres = request.POST['numero_semestres']
            plan = request.POST['plan']
            codigo = request.POST.get('codigo', '')
            numero_unidades = int(request.POST.get('numero_unidades', 2))  # Nuevo campo
            
            # Crear la licenciatura
            licenciatura = Licenciatura.objects.create(
                nombre=nombre,
                numero_semestres=numero_semestres,
                plan=plan,
                codigo=codigo
            )
            
            # Crear unidades automáticamente basadas en el número especificado
            año_plan = str(licenciatura.plan)[-2:]
            
            for i in range(1, numero_unidades + 1):
                Unidad.objects.create(
                    licenciatura=licenciatura,
                    numero=i,
                    nombre=f'Unidad {i}',  # Nombre simple basado en el número
                    # El código se generará automáticamente en el save() del modelo
                )
            
            messages.success(request, f'Licenciatura "{nombre}" agregada exitosamente con {numero_unidades} unidades')
            return redirect('lista_licenciaturas')
            
        except Exception as e:
            messages.error(request, f'Error al agregar la licenciatura: {str(e)}')
    
    context = {
        'page_title': 'Agregar Licenciatura',
        'modo': 'agregar'
    }
    return render(request, 'evaluaciones/licenciaturas/form_licenciatura.html', context)
    
    context = {
        'page_title': 'Agregar Licenciatura',
        'modo': 'agregar'
    }
    return render(request, 'evaluaciones/licenciaturas/form_licenciatura.html', context)

@control_escolar_required
def editar_licenciatura(request, licenciatura_id):
    """Editar una licenciatura existente"""
    licenciatura = get_object_or_404(Licenciatura, id=licenciatura_id)
    
    if request.method == 'POST':
        try:
            numero_unidades_nuevo = int(request.POST.get('numero_unidades', licenciatura.unidades.count()))
            numero_unidades_actual = licenciatura.unidades.count()
            
            # Actualizar información básica
            licenciatura.nombre = request.POST['nombre']
            licenciatura.numero_semestres = request.POST['numero_semestres']
            licenciatura.plan = request.POST['plan']
            licenciatura.codigo = request.POST.get('codigo', '')
            licenciatura.activa = 'activa' in request.POST
            
            licenciatura.save()
            
            # Manejar cambio en el número de unidades
            if numero_unidades_nuevo != numero_unidades_actual:
                año_plan = str(licenciatura.plan)[-2:]
                
                if numero_unidades_nuevo > numero_unidades_actual:
                    # Agregar unidades nuevas
                    for i in range(numero_unidades_actual + 1, numero_unidades_nuevo + 1):
                        Unidad.objects.create(
                            licenciatura=licenciatura,
                            numero=i,
                            nombre=f'Unidad {i}'
                        )
                    messages.info(request, f'Se agregaron {numero_unidades_nuevo - numero_unidades_actual} unidades nuevas')
                    
                elif numero_unidades_nuevo < numero_unidades_actual:
                    # Eliminar unidades sobrantes (solo si no tienen materias)
                    unidades_a_eliminar = licenciatura.unidades.filter(numero__gt=numero_unidades_nuevo)
                    unidades_con_materias = []
                    unidades_eliminadas = 0
                    
                    for unidad in unidades_a_eliminar:
                        if unidad.materias.exists():
                            unidades_con_materias.append(unidad.codigo)
                        else:
                            unidad.delete()
                            unidades_eliminadas += 1
                    
                    if unidades_con_materias:
                        messages.warning(request, f'No se pudieron eliminar {len(unidades_con_materias)} unidades porque tienen materias: {", ".join(unidades_con_materias)}')
            
            messages.success(request, f'Licenciatura "{licenciatura.nombre}" actualizada exitosamente')
            return redirect('detalle_licenciatura', licenciatura_id=licenciatura.id)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar la licenciatura: {str(e)}')
    
    context = {
        'licenciatura': licenciatura,
        'page_title': f'Editar {licenciatura.nombre}',
        'modo': 'editar'
    }
    return render(request, 'evaluaciones/licenciaturas/form_licenciatura.html', context)

@control_escolar_required
def detalle_licenciatura(request, licenciatura_id):
    """Ver detalle de una licenciatura"""
    licenciatura = get_object_or_404(Licenciatura, id=licenciatura_id)
    unidades = licenciatura.unidades.all().prefetch_related('materias')
    
    # Obtener materias por semestre
    materias_por_semestre = {}
    for semestre in range(1, licenciatura.numero_semestres + 1):
        materias_por_semestre[semestre] = Materia.objects.filter(
            licenciatura=licenciatura,
            semestre=semestre
        ).select_related('unidad')
    
    context = {
        'licenciatura': licenciatura,
        'unidades': unidades,
        'materias_por_semestre': materias_por_semestre,
        'page_title': f'Detalle de {licenciatura.nombre}'
    }
    return render(request, 'evaluaciones/licenciaturas/detalle_licenciatura.html', context)

@control_escolar_required
def eliminar_licenciatura(request, licenciatura_id):
    """Eliminar una licenciatura"""
    licenciatura = get_object_or_404(Licenciatura, id=licenciatura_id)
    
    if request.method == 'POST':
        try:
            nombre = licenciatura.nombre
            licenciatura.delete()
            messages.success(request, f'Licenciatura "{nombre}" eliminada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar la licenciatura: {str(e)}')
    
    return redirect('lista_licenciaturas')

@control_escolar_required
def agregar_materia(request, licenciatura_id):
    """Agregar una materia a una licenciatura"""
    licenciatura = get_object_or_404(Licenciatura, id=licenciatura_id)
    
    if request.method == 'POST':
        try:
            nombre = request.POST['nombre']
            semestre = int(request.POST['semestre'])
            unidad_id = request.POST['unidad_id']
            creditos = int(request.POST.get('creditos', 8))
            
            unidad = get_object_or_404(Unidad, id=unidad_id, licenciatura=licenciatura)
            
            # Crear la materia
            materia = Materia.objects.create(
                licenciatura=licenciatura,
                unidad=unidad,
                nombre=nombre,
                semestre=semestre,
                creditos=creditos
            )
            
            messages.success(request, f'Materia "{nombre}" agregada exitosamente')
            
        except Exception as e:
            messages.error(request, f'Error al agregar la materia: {str(e)}')
    
    return redirect('detalle_licenciatura', licenciatura_id=licenciatura_id)

@control_escolar_required
def eliminar_materia(request, materia_id):
    """Eliminar una materia"""
    materia = get_object_or_404(Materia, id=materia_id)
    licenciatura_id = materia.licenciatura.id
    
    if request.method == 'POST':
        try:
            nombre = materia.nombre
            materia.delete()
            messages.success(request, f'Materia "{nombre}" eliminada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar la materia: {str(e)}')
    
    return redirect('detalle_licenciatura', licenciatura_id=licenciatura_id)

@control_escolar_required
def editar_materia(request, materia_id):
    """Editar una materia existente"""
    materia = get_object_or_404(Materia, id=materia_id)
    
    if request.method == 'POST':
        try:
            materia.nombre = request.POST['nombre']
            materia.semestre = int(request.POST['semestre'])
            materia.unidad_id = request.POST['unidad_id']
            materia.creditos = int(request.POST.get('creditos', 8))
            materia.activa = 'activa' in request.POST
            
            materia.save()
            
            messages.success(request, f'Materia "{materia.nombre}" actualizada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar la materia: {str(e)}')
    
    return redirect('detalle_licenciatura', licenciatura_id=materia.licenciatura.id)

@control_escolar_required
def cambiar_estado_materia(request, materia_id):
    """Cambiar el estado activo/inactivo de una materia"""
    materia = get_object_or_404(Materia, id=materia_id)
    
    if request.method == 'POST':
        try:
            materia.activa = not materia.activa
            materia.save()
            
            estado = "activada" if materia.activa else "desactivada"
            messages.success(request, f'Materia "{materia.nombre}" {estado} exitosamente')
        except Exception as e:
            messages.error(request, f'Error al cambiar el estado de la materia: {str(e)}')
    
    return redirect('detalle_licenciatura', licenciatura_id=materia.licenciatura.id)

@control_escolar_required
def obtener_datos_materia(request, materia_id):
    """Obtener datos de una materia para edición (AJAX)"""
    materia = get_object_or_404(Materia, id=materia_id)
    
    return JsonResponse({
        'nombre': materia.nombre,
        'semestre': materia.semestre,
        'unidad_id': materia.unidad.id,
        'creditos': materia.creditos,
        'activa': materia.activa
    })