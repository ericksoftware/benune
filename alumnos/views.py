# alumnos/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Alumno

@login_required
def student_list(request):
    """Lista de todos los alumnos (todos los usuarios autenticados pueden ver)"""
    alumnos = Alumno.objects.all().order_by('apellido_paterno', 'apellido_materno', 'nombre')
    
    context = {
        'alumnos': alumnos,
        'page_title': 'Lista de Alumnos'
    }
    return render(request, 'alumnos/student_list.html', context)

@login_required
def student_detail(request, student_id):
    """Detalle de un alumno específico (todos los usuarios autenticados pueden ver)"""
    alumno = get_object_or_404(Alumno, id=student_id)
    
    context = {
        'alumno': alumno,
        'page_title': f'Detalle de {alumno.nombre_completo}'
    }
    return render(request, 'alumnos/student_detail.html', context)