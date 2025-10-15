import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def check_postgres_encryption():
    print("=== VERIFICANDO CIFRADO REAL EN POSTGRESQL ===")
    
    with connection.cursor() as cursor:
        # Verificar usuarios
        print("\n--- USUARIOS (tabla: usuarios_usuario) ---")
        cursor.execute("SELECT email FROM usuarios_usuario")
        for row in cursor.fetchall():
            email = row[0]
            is_encrypted = email.startswith('gAAAA') if email else False
            print(f"Email: {email} | Cifrado: {is_encrypted}")
        
        # Verificar alumnos - email_institucional
        print("\n--- ALUMNOS - EMAIL INSTITUCIONAL (tabla: alumnos_alumno) ---")
        cursor.execute("SELECT email_institucional FROM alumnos_alumno")
        for row in cursor.fetchall():
            email = row[0]
            is_encrypted = email.startswith('gAAAA') if email else False
            print(f"Email: {email} | Cifrado: {is_encrypted}")
        
        # Verificar alumnos - password_email_institucional
        print("\n--- ALUMNOS - PASSWORD (tabla: alumnos_alumno) ---")
        cursor.execute("SELECT password_email_institucional FROM alumnos_alumno WHERE password_email_institucional != 'N/A'")
        for row in cursor.fetchall():
            password = row[0]
            is_encrypted = password.startswith('gAAAA') if password else False
            print(f"Password: {password} | Cifrado: {is_encrypted}")

if __name__ == '__main__':
    check_postgres_encryption()