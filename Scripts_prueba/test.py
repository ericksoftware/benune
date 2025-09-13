# test_encryption.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.encryption import encryption_manager

# Probar el cifrado con tu clave
test_data = "CURP_TEST123456HMCDGR07"
encrypted = encryption_manager.encrypt(test_data)
decrypted = encryption_manager.decrypt(encrypted)

print("🔐 Prueba de cifrado:")
print(f"Texto original: {test_data}")
print(f"Texto cifrado: {encrypted}")
print(f"Texto descifrado: {decrypted}")
print(f"¿Coinciden? {test_data == decrypted}")

# Probar con datos sensibles típicos
datos_sensibles = [
    "GAMA860115HBCRRR06",
    "liviere.aguilar@gmail.com",
    "6861956063",
    "MEXICALI, B.C."
]

print("\n🧪 Prueba con datos sensibles:")
for dato in datos_sensibles:
    encrypted = encryption_manager.encrypt(dato)
    decrypted = encryption_manager.decrypt(encrypted)
    print(f"Original: {dato}")
    print(f"Cifrado: {encrypted[:30]}...")
    print(f"Descifrado: {decrypted}")
    print("---")