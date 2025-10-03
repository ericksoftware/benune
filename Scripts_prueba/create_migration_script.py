# create_migration_script.py
import os
import django

# Configurar el entorno de Django ANTES de cualquier importación
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumnos.models import Alumno

def migrar_datos_existentes():
    print("🔍 Iniciando migración de datos existentes...")
    
    total_alumnos = Alumno.objects.count()
    print(f"📊 Total de alumnos a migrar: {total_alumnos}")
    
    for i, alumno in enumerate(Alumno.objects.all(), 1):
        try:
            # Solo guardar para que los nuevos campos encriptados se manejen correctamente
            alumno.save()
            
            print(f"✅ Alumno {i}/{total_alumnos} migrado: {alumno.nombre_completo}")
            
        except Exception as e:
            print(f"❌ Error migrando alumno {i}: {e}")
    
    print("🎉 Migración completada exitosamente!")

if __name__ == "__main__":
    migrar_datos_existentes()