# fix_double_encryption.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumnos.models import Alumno
from core.encryption import encryption_manager

def fix_double_encryption():
    print("🔧 Arreglando cifrado duplicado...")
    
    for alumno in Alumno.objects.all():
        updated = False
        
        # Verificar y arreglar cada campo cifrado
        campos_cifrados = [
            'curp', 'nombre', 'apellido_paterno', 'apellido_materno',
            'municipio_estado_nacimiento', 'institucion_procedencia',
            'correo_particular', 'numero_celular'
        ]
        
        for campo in campos_cifrados:
            valor = getattr(alumno, campo)
            if valor and valor.startswith('gAAAAAB'):
                try:
                    # Descifrar una vez
                    first_decrypt = encryption_manager.decrypt(valor)
                    # Si todavía está cifrado, descifrar de nuevo y guardar
                    if first_decrypt and first_decrypt.startswith('gAAAAAB'):
                        final_decrypt = encryption_manager.decrypt(first_decrypt)
                        setattr(alumno, campo, final_decrypt)
                        updated = True
                        print(f"✅ {campo} arreglado: {valor[:30]}... -> {final_decrypt}")
                except Exception as e:
                    print(f"❌ Error en {campo}: {e}")
        
        if updated:
            alumno.save()
            print(f"💾 Alumno {alumno.matricula} actualizado")

if __name__ == "__main__":
    fix_double_encryption()