# core/encryption.py
from cryptography.fernet import Fernet
from django.conf import settings
import os

class EncryptionManager:
    def __init__(self):
        # Clave de cifrado (debería estar en variables de entorno)
        self.key = self._get_encryption_key()
        self.fernet = Fernet(self.key)
    
    def _get_encryption_key(self):
        # Usar una clave desde settings o generar una
        key = getattr(settings, 'ENCRYPTION_KEY', None)
        
        if not key:
            # Generar una clave (solo para desarrollo)
            key = Fernet.generate_key()
            # print("⚠️  ADVERTENCIA: Usando clave de cifrado generada automáticamente.")
            # print("⚠️  Para producción, define ENCRYPTION_KEY en tus variables de entorno")
        
        return key
    
    def encrypt(self, data):
        """Cifrar datos sensibles"""
        if data is None:
            return None
        data_str = str(data)
        return self.fernet.encrypt(data_str.encode()).decode()
    
    def decrypt(self, encrypted_data):
        """Descifrar datos"""
        if encrypted_data is None:
            return None
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except:
            return None

# Instancia global del manager de cifrado
encryption_manager = EncryptionManager()