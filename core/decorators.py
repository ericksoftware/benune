# core/decorators.py
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test

def control_escolar_required(view_func):
    """Decorator que permite el acceso solo a control escolar"""
    def check_user(user):
        return user.is_authenticated and hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'control_escolar'
    
    return user_passes_test(check_user)(view_func)

def docente_required(view_func):
    """Decorator que permite el acceso solo a docentes"""
    def check_user(user):
        return user.is_authenticated and hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'docente'
    
    return user_passes_test(check_user)(view_func)

def directivo_required(view_func):
    """Decorator que permite el acceso solo a directivos"""
    def check_user(user):
        return user.is_authenticated and hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'directivo'
    
    return user_passes_test(check_user)(view_func)

def alumno_required(view_func):
    """Decorator que permite el acceso solo a alumnos"""
    def check_user(user):
        return user.is_authenticated and hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'alumno'
    
    return user_passes_test(check_user)(view_func)