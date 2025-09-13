# create_encrypt_existing_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumnos.models import Alumno
from core.encryption import encryption_manager

def encrypt_existing_data():
    for alumno in Alumno.objects.all():
        # Guardar automáticamente cifrará los datos
        alumno.save()
    print("Datos existentes cifrados")

if __name__ == "__main__":
    encrypt_existing_data()