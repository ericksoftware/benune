from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from core.decorators import control_escolar_required
from .models import Alumno
from evaluaciones.models import Carrera, Calificacion, Materia, Unidad
from django.db import IntegrityError
from django.core.exceptions import ValidationError

@control_escolar_required
def student_list(request):
    """Lista de todos los alumnos - Solo control escolar"""
    alumnos = Alumno.objects.all().order_by('apellido_paterno', 'apellido_materno', 'nombre')
    
    # Filtros
    estado_filter = request.GET.get('estado', '')
    carrera_filter = request.GET.get('carrera', '')
    
    if estado_filter:
        alumnos = alumnos.filter(estado=estado_filter)
    if carrera_filter:
        alumnos = alumnos.filter(carrera_id=carrera_filter)
    
    carreras = Carrera.objects.all()
    
    context = {
        'alumnos': alumnos,
        'carreras': carreras,
        'estado_filter': estado_filter,
        'carrera_filter': carrera_filter,
        'page_title': 'Lista de Alumnos'
    }
    return render(request, 'alumnos/student_list.html', context)

# alumnos/views.py - Agregar debug
@control_escolar_required
def student_detail(request, student_id):
    """Detalle de un alumno específico - Solo control escolar"""
    alumno = get_object_or_404(Alumno, id=student_id)
    calificaciones = Calificacion.objects.filter(alumno=alumno).select_related('materia')
    
    # DEBUG: Verificar calificaciones cargadas
    print(f"🔍 DEBUG STUDENT_DETAIL - Alumno: {alumno.nombre_completo()}")
    print(f"🔍 DEBUG STUDENT_DETAIL - Calificaciones cargadas: {calificaciones.count()}")
    for calif in calificaciones:
        print(f"🔍 DEBUG STUDENT_DETAIL - {calif.materia.nombre}: {calif.calificacion}")
    
    # Obtener materias de la carrera del alumno
    materias_carrera = []
    unidades_carrera = []
    materias_con_unidad_count = 0
    unidades_sin_materia_count = 0
    materias_calificadas = 0
    materias_por_calificar = 0
    promedio_general = None
    
    if alumno.carrera:
        # Obtener TODAS las materias de la carrera
        materias_carrera = Materia.objects.filter(
            carrera=alumno.carrera
        ).prefetch_related('unidades').order_by('semestre', 'nombre')
        
        # Obtener TODAS las unidades de la carrera
        unidades_carrera = Unidad.objects.filter(
            carrera=alumno.carrera
        ).order_by('numero')
        
        # Calcular estadísticas
        materias_con_unidad_count = sum(1 for materia in materias_carrera if materia.unidades.exists())
        unidades_sin_materia_count = sum(1 for unidad in unidades_carrera if not unidad.materias.exists())
        
        materias_calificadas = calificaciones.count()
        materias_por_calificar = materias_carrera.count() - materias_calificadas
        
        # Promedio general
        if calificaciones.exists():
            suma_calificaciones = sum(calif.calificacion for calif in calificaciones if calif.calificacion)
            promedio_general = round(suma_calificaciones / calificaciones.count(), 2)
    
    context = {
        'alumno': alumno,
        'calificaciones': calificaciones,
        'materias_carrera': materias_carrera,
        'unidades_carrera': unidades_carrera,
        'materias_con_unidad_count': materias_con_unidad_count,
        'unidades_sin_materia_count': unidades_sin_materia_count,
        'materias_calificadas': materias_calificadas,
        'materias_por_calificar': materias_por_calificar,
        'promedio_general': promedio_general,
        'page_title': f'Detalle de {alumno.nombre_completo()}'
    }
    return render(request, 'alumnos/student_detail.html', context)

@control_escolar_required
def student_create(request):
    """Crear nuevo alumno - Solo control escolar"""
    carreras = Carrera.objects.all()
    
    if request.method == 'POST':
        try:
            # Obtener matrícula
            matricula = request.POST.get('matricula', 'PENDIENTE').strip().upper()
            
            # Validar que matrículas diferentes de "PENDIENTE" sean únicas
            if matricula != 'PENDIENTE':
                if Alumno.objects.filter(matricula=matricula).exists():
                    alumno_existente = Alumno.objects.get(matricula=matricula)
                    messages.error(request, f'La matrícula "{matricula}" ya le pertenece al alumno: {alumno_existente.nombre_completo()}')
                    return redirect('student_create')
            
            # Crear nuevo alumno
            alumno = Alumno()
            
            # Información básica
            alumno.matricula = matricula
            alumno.curp = request.POST.get('curp', 'N/A').strip().upper()
            alumno.rfc = request.POST.get('rfc', 'N/A').strip().upper()
            alumno.nombre = request.POST.get('nombre', 'N/A').strip()
            alumno.apellido_paterno = request.POST.get('apellido_paterno', 'N/A').strip()
            alumno.apellido_materno = request.POST.get('apellido_materno', 'N/A').strip()
            
            # Información personal
            alumno.municipio_nacimiento = request.POST.get('municipio_nacimiento', 'N/A')
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            if fecha_nacimiento:
                alumno.fecha_nacimiento = fecha_nacimiento
            alumno.sexo = request.POST.get('sexo', 'N/A')
            
            # Información académica previa
            alumno.institucion_procedencia = request.POST.get('institucion_procedencia', 'N/A')
            alumno.municipio_institucion = request.POST.get('municipio_institucion', 'N/A')
            alumno.clave_escuela = request.POST.get('clave_escuela', 'N/A')
            fecha_terminacion = request.POST.get('fecha_terminacion_prepa')
            if fecha_terminacion:
                alumno.fecha_terminacion_prepa = fecha_terminacion
            promedio_prepa = request.POST.get('promedio_prepa')
            if promedio_prepa:
                alumno.promedio_prepa = float(promedio_prepa)
            alumno.constancia_terminacion = request.POST.get('constancia_terminacion', 'no')
            
            # Información académica actual
            carrera_id = request.POST.get('carrera')
            if carrera_id:
                alumno.carrera = Carrera.objects.get(id=carrera_id)
            promedio_anterior = request.POST.get('promedio_semestre_anterior')
            if promedio_anterior:
                alumno.promedio_semestre_anterior = float(promedio_anterior)
            alumno.semestre_actual = request.POST.get('semestre_actual', 1)
            alumno.turno = request.POST.get('turno', 'matutino')
            alumno.plan = request.POST.get('plan', 2023)
            
            # Información de contacto
            alumno.email_institucional = request.POST.get('email_institucional', 'Pendiente')
            alumno.password_email_institucional = request.POST.get('password_email_institucional', 'N/A')
            alumno.email_personal = request.POST.get('email_personal', 'N/A')
            alumno.telefono = request.POST.get('telefono', 'N/A')
            
            # Estado
            alumno.estado = request.POST.get('estado', 'activo')
            
            alumno.save()
            
            messages.success(request, f'Alumno {alumno.nombre_completo()} creado exitosamente')
            return redirect('student_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear el alumno: {str(e)}')
    
    context = {
        'carreras': carreras,
        'page_title': 'Registrar Nuevo Alumno',
        'modo': 'crear'
    }
    return render(request, 'alumnos/student_form.html', context)

@control_escolar_required
def student_edit(request, student_id):
    """Editar alumno existente - Solo control escolar"""
    alumno = get_object_or_404(Alumno, id=student_id)
    carreras = Carrera.objects.all()
    
    if request.method == 'POST':
        try:
            # Obtener nueva matrícula
            nueva_matricula = request.POST.get('matricula', 'PENDIENTE').strip().upper()
            
            # Validar que matrículas diferentes de "PENDIENTE" sean únicas
            if (nueva_matricula != 'PENDIENTE' and 
                nueva_matricula != alumno.matricula):
                if Alumno.objects.filter(matricula=nueva_matricula).exists():
                    alumno_existente = Alumno.objects.get(matricula=nueva_matricula)
                    messages.error(request, f'La matrícula "{nueva_matricula}" ya le pertenece al alumno: {alumno_existente.nombre_completo()}')
                    return redirect('student_edit', student_id=student_id)
            
            # Actualizar información básica
            alumno.matricula = nueva_matricula
            alumno.curp = request.POST.get('curp', 'N/A').strip().upper()
            alumno.rfc = request.POST.get('rfc', 'N/A').strip().upper()
            alumno.nombre = request.POST.get('nombre', 'N/A').strip()
            alumno.apellido_paterno = request.POST.get('apellido_paterno', 'N/A').strip()
            alumno.apellido_materno = request.POST.get('apellido_materno', 'N/A').strip()
            
            # Información personal
            alumno.municipio_nacimiento = request.POST.get('municipio_nacimiento', 'N/A')
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            if fecha_nacimiento:
                alumno.fecha_nacimiento = fecha_nacimiento
            else:
                alumno.fecha_nacimiento = None
            alumno.sexo = request.POST.get('sexo', 'N/A')
            
            # Información académica previa
            alumno.institucion_procedencia = request.POST.get('institucion_procedencia', 'N/A')
            alumno.municipio_institucion = request.POST.get('municipio_institucion', 'N/A')
            alumno.clave_escuela = request.POST.get('clave_escuela', 'N/A')
            fecha_terminacion = request.POST.get('fecha_terminacion_prepa')
            if fecha_terminacion:
                alumno.fecha_terminacion_prepa = fecha_terminacion
            else:
                alumno.fecha_terminacion_prepa = None
            promedio_prepa = request.POST.get('promedio_prepa')
            if promedio_prepa:
                alumno.promedio_prepa = float(promedio_prepa)
            else:
                alumno.promedio_prepa = None
            alumno.constancia_terminacion = request.POST.get('constancia_terminacion', 'no')
            
            # Información académica actual
            carrera_id = request.POST.get('carrera')
            if carrera_id:
                alumno.carrera = Carrera.objects.get(id=carrera_id)
            else:
                alumno.carrera = None
            promedio_anterior = request.POST.get('promedio_semestre_anterior')
            if promedio_anterior:
                alumno.promedio_semestre_anterior = float(promedio_anterior)
            else:
                alumno.promedio_semestre_anterior = None
            alumno.semestre_actual = request.POST.get('semestre_actual', 1)
            alumno.turno = request.POST.get('turno', 'matutino')
            alumno.plan = request.POST.get('plan', 2023)
            
            # Información de contacto
            alumno.email_institucional = request.POST.get('email_institucional', 'Pendiente').strip()
            alumno.password_email_institucional = request.POST.get('password_email_institucional', 'N/A')
            alumno.email_personal = request.POST.get('email_personal', 'N/A').strip()
            alumno.telefono = request.POST.get('telefono', 'N/A')
            
            # Estado
            alumno.estado = request.POST.get('estado', 'activo')
            
            alumno.save()
            
            messages.success(request, f'Alumno {alumno.nombre_completo()} actualizado exitosamente')
            return redirect('student_detail', student_id=alumno.id)
            
        except ValidationError as e:
            # Capturar errores de validación del modelo
            for field, errors in e.error_dict.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
        except Exception as e:
            messages.error(request, f'Error al actualizar el alumno: {str(e)}')
    
    context = {
        'alumno': alumno,
        'carreras': carreras,
        'page_title': f'Editar {alumno.nombre_completo()}',
        'modo': 'editar'
    }
    return render(request, 'alumnos/student_form.html', context)

@control_escolar_required
def student_delete(request, student_id):
    """Eliminar alumno - Solo control escolar"""
    alumno = get_object_or_404(Alumno, id=student_id)
    
    if request.method == 'POST':
        try:
            nombre_completo = alumno.nombre_completo()
            alumno.delete()
            messages.success(request, f'Alumno {nombre_completo} eliminado exitosamente')
            return redirect('student_list')
        except Exception as e:
            messages.error(request, f'Error al eliminar el alumno: {str(e)}')
    
    context = {
        'alumno': alumno,
        'page_title': f'Eliminar {alumno.nombre_completo()}'
    }
    return render(request, 'alumnos/student_confirm_delete.html', context)

@control_escolar_required
def student_update_grades(request, student_id):
    """Actualizar calificaciones del alumno - Solo control escolar"""
    alumno = get_object_or_404(Alumno, id=student_id)
    
    if request.method == 'POST':
        try:
            print(f"🔍 DEBUG - Procesando calificaciones para alumno: {alumno.nombre_completo()}")
            
            # Obtener TODOS los campos del POST que empiecen con "calificacion_"
            campos_calificacion = [key for key in request.POST.keys() if key.startswith('calificacion_')]
            print(f"🔍 DEBUG - Campos encontrados en POST: {len(campos_calificacion)}")
            
            for campo in campos_calificacion:
                # Extraer el ID de la materia del nombre del campo
                materia_id = campo.replace('calificacion_', '')
                calificacion_valor = request.POST.get(campo, '').strip()
                
                print(f"🔍 DEBUG - Procesando: {campo} = '{calificacion_valor}'")
                
                try:
                    materia = Materia.objects.get(id=materia_id)
                    
                    # Si el campo está vacío o es "N/A", eliminar la calificación existente
                    if not calificacion_valor or calificacion_valor.lower() == 'n/a':
                        deleted_count, _ = Calificacion.objects.filter(
                            alumno=alumno, 
                            materia=materia
                        ).delete()
                        print(f"🔍 DEBUG - Calificación eliminada para {materia.nombre}: {deleted_count}")
                    else:
                        # Convertir a decimal y guardar/actualizar
                        calificacion_decimal = float(calificacion_valor)
                        
                        # Crear o actualizar calificación
                        calificacion, created = Calificacion.objects.update_or_create(
                            alumno=alumno,
                            materia=materia,
                            defaults={
                                'calificacion': calificacion_decimal,
                                'periodo': f"2025-{alumno.semestre_actual}"
                            }
                        )
                        
                        print(f"🔍 DEBUG - Calificación {'CREADA' if created else 'ACTUALIZADA'} para {materia.nombre}: {calificacion.calificacion}")
                        
                except Materia.DoesNotExist:
                    print(f"❌ ERROR - Materia con ID {materia_id} no existe")
                    continue
                except ValueError as e:
                    print(f"❌ ERROR en valor: {e}")
                    continue
            
            # VERIFICAR DESPUÉS DE GUARDAR
            calificaciones_despues = Calificacion.objects.filter(alumno=alumno)
            print(f"🔍 DEBUG - Calificaciones después de guardar: {calificaciones_despues.count()}")
            for calif in calificaciones_despues:
                print(f"🔍 DEBUG - Calificación guardada: {calif.materia.nombre} = {calif.calificacion}")
            
            messages.success(request, f'Calificaciones de {alumno.nombre_completo()} actualizadas exitosamente')
            
        except Exception as e:
            print(f"❌ ERROR general: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error al actualizar las calificaciones: {str(e)}')
    
    return redirect('student_detail', student_id=student_id)