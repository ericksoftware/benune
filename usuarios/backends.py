from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from alumnos.models import Alumno

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        if not username or not password:
            return None
            
        # Normalizar el username
        username = username.lower().strip()
        
        print(f"🔐 Intentando autenticar: {username}")
            
        try:
            # PRIMERO: Buscar por username normal
            user = UserModel.objects.get(username=username)
            print(f"✅ Encontrado por username: {user.username}")
            if user and user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            print("❌ No encontrado por username")
            pass
            
        # SEGUNDO: Buscar por email (Django YA nos da el email descifrado)
        try:
            # Buscar directamente por email descifrado
            user = UserModel.objects.get(email=username)
            print(f"✅ Encontrado por email: {user.email}")
            if user and user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            print(f"❌ No encontrado por email: {username}")
            pass
        except UserModel.MultipleObjectsReturned:
            user = UserModel.objects.filter(email=username).first()
            print(f"✅ Múltiples usuarios, tomando primero: {user.email}")
            if user and user.check_password(password):
                return user
        
        # TERCERO: Buscar alumnos
        try:
            print("🎓 Buscando alumno...")
            
            # Buscar TODOS los alumnos activos
            alumnos = Alumno.objects.filter(estado='activo')
            
            for alumno in alumnos:
                # Django automáticamente descifra el email
                if alumno.email_institucional and alumno.email_institucional.lower() == username:
                    print(f"✅ Alumno encontrado: {alumno.nombre_completo()}")
                    
                    # Comparar contraseña (automáticamente descifrada)
                    if alumno.password_email_institucional == password:
                        print("✅ Contraseña de alumno válida")
                        
                        # BUSCAR el usuario que YA EXISTE por username esperado
                        expected_username = f"alumno_{alumno.matricula or alumno.id}"
                        try:
                            user = UserModel.objects.get(username=expected_username)
                            print(f"✅ Usuario Django encontrado por username: {user.username}")
                            
                            # Si el usuario no tiene email, asignárselo (SOLO EN MEMORIA)
                            if not user.email or user.email in ['', 'N/A']:
                                user.email = username  # Solo para esta sesión
                                print(f"🔄 Email asignado en memoria: {username}")
                            
                            return user
                        except UserModel.DoesNotExist:
                            print("❌ No se encontró usuario Django para este alumno")
                            return None
                    else:
                        print("❌ Contraseña de alumno incorrecta")
                        return None
            
            print(f"❌ No se encontró alumno con email: {username}")
                        
        except Exception as e:
            print(f"❌ Error buscando alumno: {e}")
            
        # CUARTO: Búsqueda manual como fallback
        try:
            print("🔄 Búsqueda manual en todos los usuarios...")
            for user in UserModel.objects.all():
                if user.email and user.email.lower() == username:
                    print(f"✅ Encontrado manualmente: {user.email}")
                    if user.check_password(password):
                        return user
        except Exception as e:
            print(f"❌ Error en búsqueda manual: {e}")
            
        print("❌ Autenticación fallida completamente")
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None