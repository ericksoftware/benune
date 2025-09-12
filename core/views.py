# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home_redirect(request):
    """Redirige a los usuarios autenticados al dashboard, sino al login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')

@login_required
def dashboard(request):
    """Dashboard principal del sistema"""
    # Determinar el tipo de usuario para mostrar información relevante
    user_type = request.user.tipo_usuario if hasattr(request.user, 'tipo_usuario') else 'desconocido'
    
    context = {
        'page_title': 'Panel de Control',
        'user_type': user_type,
        'is_control_escolar': user_type == 'control_escolar',
    }
    return render(request, 'core/dashboard.html', context)