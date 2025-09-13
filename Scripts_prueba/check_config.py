# check_config.py
import os
import django
from dotenv import load_dotenv

load_dotenv()

print("🔍 Verificando configuración...")
print("=" * 50)

# Check encryption key
enc_key = os.getenv('ENCRYPTION_KEY')
print(f"ENCRYPTION_KEY: {'✅ Configurada' if enc_key else '❌ Faltante'}")

# Check database config
db_config = [
    ('DB_NAME', os.getenv('DB_NAME')),
    ('DB_USER', os.getenv('DB_USER')),
    ('DB_PASSWORD', os.getenv('DB_PASSWORD')),
    ('DB_HOST', os.getenv('DB_HOST')),
    ('DB_PORT', os.getenv('DB_PORT'))
]

for key, value in db_config:
    status = '✅ Configurada' if value else '❌ Faltante'
    print(f"{key}: {status}")

# Check secret key
secret_key = os.getenv('SECRET_KEY')
print(f"SECRET_KEY: {'✅ Configurada' if secret_key else '❌ Faltante'}")

print("=" * 50)
print("💡 Si hay ❌ Faltante, completa tu archivo .env")