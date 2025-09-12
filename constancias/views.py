from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from core.decorators import control_escolar_required
from .models import Constancia
from alumnos.models import Alumno
import os
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile

@login_required
def certificate_list(request):
    """Lista de todas las constancias"""
    constancias = Constancia.objects.all().order_by('-fecha_generacion')
    
    context = {
        'constancias': constancias,
        'page_title': 'Lista de Constancias'
    }
    return render(request, 'constancias/certificate_list.html', context)

@control_escolar_required
def generate_certificate(request):
    """Generar una nueva constancia"""
    if request.method == 'POST':
        try:
            alumno_id = request.POST.get('alumno')
            tipo_constancia = request.POST.get('tipo_constancia')
            fecha_emision = request.POST.get('fecha_emision')
            observaciones = request.POST.get('observaciones', '')
            
            alumno = Alumno.objects.get(id=alumno_id)
            
            # Crear la constancia
            constancia = Constancia.objects.create(
                alumno=alumno,
                tipo_constancia=tipo_constancia,
                fecha_emision=fecha_emision,
                observaciones=observaciones
            )
            
            # Generar PDF (esto es un ejemplo básico)
            html_string = render_to_string('constancias/certificate_template.html', {
                'constancia': constancia
            })
            
            # Generar PDF con WeasyPrint
            html = HTML(string=html_string)
            result = html.write_pdf()
            
            # Guardar el PDF
            pdf_path = f'constancias/{constancia.id}_{constancia.alumno.curp}.pdf'
            full_path = os.path.join(settings.MEDIA_ROOT, pdf_path)
            
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'wb') as f:
                f.write(result)
            
            constancia.archivo_pdf = pdf_path
            constancia.save()
            
            messages.success(request, f'Constancia generada exitosamente para {alumno.nombre_completo}')
            return redirect('view_certificate', certificate_id=constancia.id)
            
        except Exception as e:
            messages.error(request, f'Error al generar la constancia: {str(e)}')
    
    # Si es GET, mostrar el formulario
    alumnos = Alumno.objects.all().order_by('apellido_paterno', 'apellido_materno', 'nombre')
    
    context = {
        'alumnos': alumnos,
        'page_title': 'Generar Constancia'
    }
    return render(request, 'constancias/generate_certificate.html', context)

@login_required
def view_certificate(request, certificate_id):
    """Ver una constancia específica"""
    constancia = get_object_or_404(Constancia, id=certificate_id)
    
    context = {
        'constancia': constancia,
        'page_title': f'Constancia de {constancia.alumno.nombre_completo}'
    }
    return render(request, 'constancias/view_certificate.html', context)

@control_escolar_required
def download_certificate(request, certificate_id):
    """Descargar una constancia en PDF"""
    constancia = get_object_or_404(Constancia, id=certificate_id)
    
    if constancia.archivo_pdf:
        file_path = constancia.archivo_pdf.path
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="constancia_{constancia.alumno.curp}.pdf"'
            return response
    
    messages.error(request, 'El archivo PDF no está disponible')
    return redirect('view_certificate', certificate_id=certificate_id)