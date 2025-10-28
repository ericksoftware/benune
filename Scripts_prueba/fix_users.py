# fix_users.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import Usuario
from core.encryption import encryption_manager

def main():
    print("🔧 Corrigiendo usuarios para login...")
    
    # Verificar y corregir el usuario de control escolar
    try:
        # Buscar por email descifrado en todos los usuarios
        target_email = "control@benune.edu.mx"
        usuario_encontrado = None
        
        for usuario in Usuario.objects.all():
            try:
                email_descifrado = encryption_manager.decrypt(usuario.email)
                if email_descifrado == target_email:
                    usuario_encontrado = usuario
                    break
            except:
                continue
        
        if usuario_encontrado:
            print(f"✅ Usuario encontrado: {usuario_encontrado}")
            
            # Establecer contraseña
            usuario_encontrado.set_password("password123")
            usuario_encontrado.save()
            print("✅ Contraseña establecida correctamente")
            
            # Verificar autenticación
            from django.contrib.auth import authenticate
            user = authenticate(username=target_email, password="password123")
            if user:
                print("✅ Autenticación exitosa")
            else:
                print("❌ Error en autenticación")
        else:
            print("❌ Usuario no encontrado")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()