# debug_encryption.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumnos.models import Alumno
from core.encryption import encryption_manager

alumno = Alumno.objects.first()
print("=== DEBUG ENCRYPTION ===")
print(f"Curp cifrado: {alumno.curp}")
print(f"Nombre cifrado: {alumno.nombre}")

# Intentar descifrar manualmente
try:
    curp_descifrado = encryption_manager.decrypt(alumno.curp)
    print(f"Curp descifrado: {curp_descifrado}")
except Exception as e:
    print(f"Error descifrando CURP: {e}")

try:
    nombre_descifrado = encryption_manager.decrypt(alumno.nombre)
    print(f"Nombre descifrado: {nombre_descifrado}")
except Exception as e:
    print(f"Error descifrando nombre: {e}")