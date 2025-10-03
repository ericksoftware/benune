# create_migration_script.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from evaluaciones.models import Licenciatura, Unidad, Materia

def migrate_existing_data():
    """Migrar datos existentes para crear unidades y asignarlas a materias"""
    print("Iniciando migración de datos...")
    
    # Para cada licenciatura, crear unidades por defecto
    for licenciatura in Licenciatura.objects.all():
        print(f"Procesando licenciatura: {licenciatura.nombre}")
        
        # Crear unidades por defecto si no existen
        unidades_base = [
            (1, 'Unidad Principal'),
            (2, 'Unidad Avanzada'),
            (3, 'Unidad Especializada')
        ]
        
        for num, nombre in unidades_base:
            unidad, created = Unidad.objects.get_or_create(
                licenciatura=licenciatura,
                numero=num,
                defaults={'nombre': nombre}
            )
            if created:
                print(f"  - Creada unidad: {unidad.codigo}")
        
        # Asignar unidades a materias existentes
        materias_sin_unidad = Materia.objects.filter(licenciatura=licenciatura, unidad__isnull=True)
        if materias_sin_unidad.exists():
            unidad_principal = Unidad.objects.filter(licenciatura=licenciatura, numero=1).first()
            if unidad_principal:
                updated = materias_sin_unidad.update(unidad=unidad_principal)
                print(f"  - Asignadas {updated} materias a la unidad principal")
    
    print("Migración completada!")

if __name__ == "__main__":
    migrate_existing_data()