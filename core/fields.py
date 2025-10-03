# core/fields.py
from django.db import models
from .encryption import encryption_manager

class EncryptedCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        # Para campos cifrados, usar mínimo 500 caracteres
        if 'max_length' in kwargs and kwargs['max_length'] < 500:
            kwargs['max_length'] = 500
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None or value == '':
            return value
        try:
            decrypted = encryption_manager.decrypt(value)
            return decrypted if decrypted is not None else value
        except Exception as e:
            print(f"❌ Error descifrando '{value}': {e}")
            return value
    
    def to_python(self, value):
        if value is None or value == '':
            return value
        return value
    
    def get_prep_value(self, value):
        if value is None or value == '' or value == 'N/A':
            return value
        
        # SIEMPRE cifrar el valor antes de guardar
        try:
            encrypted = encryption_manager.encrypt(value)
            if encrypted is None:
                print(f"⚠️ Cifrado retornó None para: {value}")
                return value
            print(f"🔐 Cifrando '{value}' -> '{encrypted}'")
            return encrypted
        except Exception as e:
            print(f"❌ Error cifrando '{value}': {e}")
            return value

class EncryptedEmailField(EncryptedCharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 500
        super().__init__(*args, **kwargs)
    
    # Asegurar que los emails SIEMPRE se cifren
    def get_prep_value(self, value):
        return super().get_prep_value(value)