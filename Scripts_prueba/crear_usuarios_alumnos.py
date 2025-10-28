import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from alumnos.models import Alumno
from django.contrib.auth import get_user_model

User = get_user_model()

def crear_usuarios_para_alumnos():
    alumnos_sin_usuario = Alumno.objects.all()
    usuarios_creados = 0
    
    for alumno in alumnos_sin_usuario:
        username = f"alumno_{alumno.matricula if alumno.matricula != 'PENDIENTE' else alumno.id}"
        
        if not User.objects.filter(username=username).exists():
            try:
                user = User.objects.create_user(
                    username=username,
                    email=alumno.email_institucional if alumno.email_institucional not in ['N/A', 'Pendiente'] else f"{username}@edubc.mx",
                    password=alumno.password_email_institucional,
                    tipo_usuario='alumno',
                    first_name=alumno.nombre,
                    last_name=f"{alumno.apellido_paterno} {alumno.apellido_materno}"
                )
                print(f"✅ Creado usuario para: {alumno.nombre_completo()} -> {username}")
                usuarios_creados += 1
            except Exception as e:
                print(f"❌ Error con {alumno.nombre_completo()}: {e}")
        else:
            print(f"⚠️ Usuario ya existe: {username}")
    
    print(f"\n🎉 Se crearon {usuarios_creados} usuarios para alumnos")

if __name__ == "__main__":
    crear_usuarios_para_alumnos()