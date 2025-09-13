from cryptography.fernet import Fernet
key = Fernet.generate_key()
print("Clave de cifrado:", key.decode())