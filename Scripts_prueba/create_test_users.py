import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from usuarios.models import Usuario

# Crear usuarios de prueba
users_data = [
    {
        'username': 'control_escolar',
        'email': 'control@benune.edu.mx',
        'password': 'control123',
        'tipo_usuario': 'control_escolar',
        'first_name': 'Maria',
        'last_name': 'Garcia'
    },
    {
        'username': 'docente',
        'email': 'docente@benune.edu.mx',
        'password': 'docente123',
        'tipo_usuario': 'docente',
        'first_name': 'Juan',
        'last_name': 'Perez'
    },
    {
        'username': 'directivo',
        'email': 'directivo@benune.edu.mx',
        'password': 'directivo123',
        'tipo_usuario': 'directivo',
        'first_name': 'Carlos',
        'last_name': 'Lopez'
    }
]

for user_data in users_data:
    if not Usuario.objects.filter(username=user_data['username']).exists():
        user = Usuario.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            tipo_usuario=user_data['tipo_usuario']
        )
        print(f"Usuario creado: {user.username}")

print("Usuarios de prueba creados exitosamente!")