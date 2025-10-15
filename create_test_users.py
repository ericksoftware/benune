# create_test_users.py
import os
import django
import sys

# Agregar el directorio del proyecto al path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import Usuario
from django.contrib.auth import get_user_model

def crear_usuarios_prueba():
    """Crear usuarios de prueba para el sistema"""
    
    print("🔧 Creando usuarios de prueba...")
    
    # Datos de usuarios a crear
    usuarios_data = [
        {
            'email': 'control@benune.edu.mx',
            'password': 'Control123',
            'first_name': 'María',
            'last_name': 'García López',
            'tipo_usuario': 'control_escolar',
            'turno': 'matutino',
            'telefono': '5551234567',
            'is_staff': True,
            'is_superuser': False
        },
        {
            'email': 'directivo@benune.edu.mx',
            'password': 'Directivo123',
            'first_name': 'Carlos',
            'last_name': 'Rodríguez Martínez',
            'tipo_usuario': 'directivo',
            'turno': 'matutino',
            'telefono': '5557654321',
            'is_staff': True,
            'is_superuser': False
        },
        {
            'email': 'docente@benune.edu.mx',
            'password': 'Docente123',
            'first_name': 'Ana',
            'last_name': 'Hernández Silva',
            'tipo_usuario': 'docente',
            'turno': 'vespertino',
            'telefono': '5559876543',
            'is_staff': False,
            'is_superuser': False
        },
        {
            'email': 'admin@benune.edu.mx',
            'password': 'Admin123',
            'first_name': 'Super',
            'last_name': 'Administrador',
            'tipo_usuario': 'directivo',
            'turno': 'matutino',
            'telefono': '5550000000',
            'is_staff': True,
            'is_superuser': True
        }
    ]
    
    usuarios_creados = 0
    usuarios_actualizados = 0
    
    for user_data in usuarios_data:
        email = user_data['email']
        password = user_data.pop('password')
        
        try:
            # Verificar si el usuario ya existe
            usuario, created = Usuario.objects.get_or_create(
                email=email,
                defaults=user_data
            )
            
            if created:
                # Si se creó nuevo, establecer la contraseña
                usuario.set_password(password)
                usuario.save()
                usuarios_creados += 1
                print(f"✅ CREADO: {email} - {usuario.get_tipo_usuario_display()}")
            else:
                # Si ya existía, actualizar datos y contraseña
                for key, value in user_data.items():
                    setattr(usuario, key, value)
                usuario.set_password(password)
                usuario.save()
                usuarios_actualizados += 1
                print(f"🔄 ACTUALIZADO: {email} - {usuario.get_tipo_usuario_display()}")
                
        except Exception as e:
            print(f"❌ ERROR al crear {email}: {str(e)}")
    
    print(f"\n📊 Resumen:")
    print(f"   Usuarios creados: {usuarios_creados}")
    print(f"   Usuarios actualizados: {usuarios_actualizados}")
    print(f"   Total en sistema: {Usuario.objects.count()}")
    
    # Mostrar lista de usuarios creados
    print(f"\n👥 Lista de usuarios disponibles:")
    for usuario in Usuario.objects.all():
        print(f"   • {usuario.email} - {usuario.get_tipo_usuario_display()} - {usuario.get_full_name()}")

def crear_usuario_control_escolar():
    """Función específica para crear solo un usuario de control escolar"""
    
    print("🔧 Creando usuario de Control Escolar...")
    
    user_data = {
        'email': 'control@benune.edu.mx',
        'password': 'Control123',
        'first_name': 'María',
        'last_name': 'García López',
        'tipo_usuario': 'control_escolar',
        'turno': 'matutino',
        'telefono': '5551234567',
        'is_staff': True,
        'is_superuser': False
    }
    
    email = user_data['email']
    password = user_data.pop('password')
    
    try:
        usuario, created = Usuario.objects.get_or_create(
            email=email,
            defaults=user_data
        )
        
        if created:
            usuario.set_password(password)
            usuario.save()
            print(f"✅ USUARIO CONTROL ESCOLAR CREADO:")
        else:
            for key, value in user_data.items():
                setattr(usuario, key, value)
            usuario.set_password(password)
            usuario.save()
            print(f"🔄 USUARIO CONTROL ESCOLAR ACTUALIZADO:")
        
        print(f"   📧 Email: {usuario.email}")
        print(f"   🔑 Contraseña: {password}")
        print(f"   👤 Nombre: {usuario.get_full_name()}")
        print(f"   🏢 Tipo: {usuario.get_tipo_usuario_display()}")
        print(f"   ⏰ Turno: {usuario.get_turno_display()}")
        print(f"   📞 Teléfono: {usuario.telefono}")
        
    except Exception as e:
        print(f"❌ ERROR al crear usuario control escolar: {str(e)}")

if __name__ == '__main__':
    print("🚀 INICIANDO CREACIÓN DE USUARIOS DE PRUEBA")
    print("=" * 50)
    
    # Crear solo el usuario de control escolar
    crear_usuario_control_escolar()
    
    print("\n" + "=" * 50)
    print("¿Deseas crear todos los usuarios de prueba?")
    respuesta = input("(s/n): ").lower().strip()
    
    if respuesta == 's':
        print("\n")
        crear_usuarios_prueba()
    
    print("\n🎉 Proceso completado!")
    print("\n💡 Credenciales de acceso:")
    print("   Control Escolar: control@benune.edu.mx / Control123")
    print("   Directivo: directivo@benune.edu.mx / Directivo123") 
    print("   Docente: docente@benune.edu.mx / Docente123")
    print("   Admin: admin@benune.edu.mx / Admin123")

    # http://127.0.0.1:8000/constancias/