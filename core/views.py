# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth import logout

def home_redirect(request):
    """Redirige a los usuarios autenticados al dashboard, sino al login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')

@login_required
def dashboard(request):
    """Dashboard principal del sistema"""
    user_type = request.user.tipo_usuario if hasattr(request.user, 'tipo_usuario') else 'desconocido'
    
    # Contexto adicional para alumnos
    context = {
        'page_title': 'Panel de Control',
        'user_type': user_type,
        'is_control_escolar': user_type == 'control_escolar',
        'is_docente': user_type == 'docente',
        'is_directivo': user_type == 'directivo',
        'is_alumno': user_type == 'alumno',  # ← Esto ahora funcionará
    }
    
    # Si es alumno, puedes agregar información específica
    if user_type == 'alumno':
        try:
            # Buscar el alumno correspondiente al usuario
            from alumnos.models import Alumno
            # El username del usuario es "alumno_{matricula}" o "alumno_{id}"
            username_parts = request.user.username.split('_')
            if len(username_parts) > 1:
                alumno_id_or_matricula = username_parts[1]
                
                # Buscar por matrícula o ID
                alumno = Alumno.objects.filter(
                    matricula=alumno_id_or_matricula
                ).first() or Alumno.objects.filter(
                    id=alumno_id_or_matricula
                ).first()
                
                if alumno:
                    context['alumno'] = alumno
        except Exception as e:
            print(f"Error obteniendo datos del alumno: {e}")
    
    return render(request, 'core/dashboard.html', context)

def forbidden_view(request, exception=None):
    """Vista para mostrar página de acceso prohibido"""
    return render(request, 'core/403.html', status=403)

def custom_logout(request):
    """Vista personalizada para cerrar sesión que acepta GET"""
    logout(request)
    return redirect('login')