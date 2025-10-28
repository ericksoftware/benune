# correccion_sexo.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import Usuario

def corregir_sexo_usuarios():
    # Cambiar todos los 'N/A' a 'otro'
    usuarios = Usuario.objects.filter(sexo='N/A')
    for usuario in usuarios:
        usuario.sexo = 'otro'
        usuario.save(update_fields=['sexo'])
        print(f"✅ Corregido: {usuario.get_full_name()} - sexo: {usuario.sexo}")

if __name__ == '__main__':
    corregir_sexo_usuarios()