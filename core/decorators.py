# core/decorators.py - ACTUALIZADO
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

def control_escolar_required(view_func):
    """Decorator que permite el acceso solo a control escolar"""
    def check_user(user):
        return user.is_authenticated and hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'control_escolar'
    
    def wrapper(request, *args, **kwargs):
        if not check_user(request.user):
            # Redirigir a la página de prohibido
            return render(request, 'core/403.html', {
                'exception': 'No tienes permisos para acceder a esta página'
            }, status=403)
        return view_func(request, *args, **kwargs)
    
    return wrapper

def docente_required(view_func):
    """Decorator que permite el acceso solo a docentes"""
    def check_user(user):
        return user.is_authenticated and hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'docente'
    
    def wrapper(request, *args, **kwargs):
        if not check_user(request.user):
            return render(request, 'core/403.html', {
                'exception': 'No tienes permisos para acceder a esta página'
            }, status=403)
        return view_func(request, *args, **kwargs)
    
    return wrapper

def directivo_required(view_func):
    """Decorator que permite el acceso solo a directivos"""
    def check_user(user):
        return user.is_authenticated and hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'directivo'
    
    def wrapper(request, *args, **kwargs):
        if not check_user(request.user):
            return render(request, 'core/403.html', {
                'exception': 'No tienes permisos para acceder a esta página'
            }, status=403)
        return view_func(request, *args, **kwargs)
    
    return wrapper

def alumno_required(view_func):
    """Decorator que permite el acceso solo a alumnos"""
    def check_user(user):
        return user.is_authenticated and hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'alumno'
    
    def wrapper(request, *args, **kwargs):
        if not check_user(request.user):
            return render(request, 'core/403.html', {
                'exception': 'No tienes permisos para acceder a esta página'
            }, status=403)
        return view_func(request, *args, **kwargs)
    
    return wrapper