# benune_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    # Administración de Django
    path('admin/', admin.site.urls),
    
    # Página principal (redirige al dashboard si está autenticado, sino al login)
    path('', core_views.home_redirect, name='home'),
    
    # Autenticación simple
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Incluir URLs de las apps
    path('', include('core.urls')),        # Dashboard
    path('alumnos/', include('alumnos.urls')),      # Visualización de alumnos
    path('constancias/', include('constancias.urls')),  # Constancias (solo control escolar)
    path('evaluaciones/', include('evaluaciones.urls')), # Evaluaciones (solo control escolar)
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Personalizar títulos del admin
admin.site.site_header = 'BENUNE - Administración'
admin.site.site_title = 'Sistema de Gestión BENUNE'
admin.site.index_title = 'Panel de Administración'