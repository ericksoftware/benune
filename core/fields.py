# core/fields.py
from django.db import models
from .encryption import encryption_manager

class EncryptedCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return encryption_manager.decrypt(value)
    
    def to_python(self, value):
        if value is None:
            return value
        return encryption_manager.decrypt(value)
    
    def get_prep_value(self, value):
        if value is None:
            return value
        return encryption_manager.encrypt(value)

class EncryptedEmailField(EncryptedCharField):
    """Campo de email cifrado"""
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 254  # Longitud estándar para emails
        super().__init__(*args, **kwargs)

class EncryptedTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return encryption_manager.decrypt(value)
    
    def to_python(self, value):
        if value is None:
            return value
        return encryption_manager.decrypt(value)
    
    def get_prep_value(self, value):
        if value is None:
            return value
        return encryption_manager.encrypt(value)