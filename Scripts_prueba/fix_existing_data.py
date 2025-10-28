# fix_existing_data.py - CORREGIDO
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumnos.models import Alumno

def fix_existing_data():
    """Corregir datos existentes después del cambio de modelo"""
    print("🔍 Buscando matrículas duplicadas...")
    
    # Encontrar matrículas duplicadas (excluyendo "PENDIENTE")
    from django.db.models import Count
    duplicates = Alumno.objects.exclude(matricula='PENDIENTE').values('matricula').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    if not duplicates:
        print("✅ No se encontraron matrículas duplicadas")
        return
    
    print(f"📝 Se encontraron {len(duplicates)} matrículas duplicadas")
    
    for dup in duplicates:
        matricula = dup['matricula']
        print(f"\n🔧 Corrigiendo duplicados para: {matricula}")
        
        # Obtener todos los alumnos con esta matrícula
        alumnos = Alumno.objects.filter(matricula=matricula).order_by('id')
        
        # Mantener el primero, cambiar los demás a "PENDIENTE"
        for i, alumno in enumerate(alumnos):
            if i == 0:
                print(f"   ✅ Manteniendo: {alumno.nombre_completo()}") 
            else:
                print(f"   🔄 Cambiando a PENDIENTE: {alumno.nombre_completo()}")
                alumno.matricula = 'PENDIENTE'
                alumno.save()
    
    print(f"\n🎉 Proceso completado. {len(duplicates)} matrículas corregidas")

if __name__ == '__main__':
    fix_existing_data()