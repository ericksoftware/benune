# clean_my_migrations.py
import os
import shutil

def clean_my_migrations():
    print("Limpiando migraciones de nuestras apps...")
    
    # Solo nuestras apps, no las de Django
    our_apps = ['alumnos', 'constancias', 'core', 'evaluaciones', 'usuarios']
    
    for app in our_apps:
        migrations_path = os.path.join('.', app, 'migrations')
        if os.path.exists(migrations_path):
            print(f"Procesando: {migrations_path}")
            
            # Borrar todos los archivos .py excepto __init__.py
            for file in os.listdir(migrations_path):
                file_path = os.path.join(migrations_path, file)
                if file.endswith('.py') and file != '__init__.py':
                    os.remove(file_path)
                    print(f"  - Eliminado: {file}")
                elif file.endswith('.pyc'):
                    os.remove(file_path)
                    print(f"  - Eliminado: {file}")
    
    # Borrar base de datos SQLite si existe
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("Base de datos eliminada")
    
    print("¡Limpieza completada!")

if __name__ == "__main__":
    clean_my_migrations()