import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumnos.models import Alumno

def check_specific_alumno():
    print("=== VERIFICANDO ALUMNO ESPECÍFICO ===")
    
    try:
        alumno = Alumno.objects.get(email_institucional='erodriguez@edubc.mx')
        print(f"Alumno: {alumno.nombre_completo()}")
        print(f"Email: {alumno.email_institucional}")
        print(f"Password: {alumno.password_email_institucional}")
        print(f"Estado: {alumno.estado}")
        
        # Verificar si los campos están realmente cifrados en la BD
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT email_institucional, password_email_institucional FROM alumnos_alumno WHERE id = %s", [alumno.id])
            row = cursor.fetchone()
            if row:
                email_db = row[0]
                password_db = row[1]
                print(f"\n--- VALORES DIRECTOS DE LA BD ---")
                print(f"Email en BD: {email_db}")
                print(f"Password en BD: {password_db}")
                print(f"Email cifrado: {email_db.startswith('gAAAA')}")
                print(f"Password cifrado: {password_db.startswith('gAAAA')}")
                
    except Alumno.DoesNotExist:
        print("No se encontró el alumno con email: erodriguez@edubc.mx")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_specific_alumno()