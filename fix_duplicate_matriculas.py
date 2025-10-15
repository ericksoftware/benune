# fix_duplicate_matriculas.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumnos.models import Alumno

def fix_duplicate_matriculas():
    """Corregir matrículas duplicadas existentes"""
    # Encontrar matrículas duplicadas (excluyendo "PENDIENTE")
    from django.db.models import Count
    duplicates = Alumno.objects.exclude(matricula='PENDIENTE').values('matricula').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    for dup in duplicates:
        matricula = dup['matricula']
        print(f"Corrigiendo duplicados para matrícula: {matricula}")
        
        # Obtener todos los alumnos con esta matrícula
        alumnos = Alumno.objects.filter(matricula=matricula).order_by('fecha_registro')
        
        # Mantener el primero, cambiar los demás a "PENDIENTE"
        for i, alumno in enumerate(alumnos):
            if i == 0:
                print(f"  - Manteniendo: {alumno.nombre_completo()}") 
            else:
                print(f"  - Cambiando a PENDIENTE: {alumno.nombre_completo()}")
                alumno.matricula = 'PENDIENTE'
                alumno.save()

if __name__ == '__main__':
    fix_duplicate_matriculas()
    print("✅ Matrículas duplicadas corregidas")