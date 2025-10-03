# create_test_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from evaluaciones.models import Licenciatura, Unidad, Materia

def create_test_data():
    print("Creando datos de prueba...")
    
    # Crear licenciaturas
    licenciaturas_data = [
        {
            'nombre': 'LICENCIATURA EN INCLUSIÓN EDUCATIVA',
            'codigo': 'LIE',
            'numero_semestres': 8,
            'plan': 2023
        },
        {
            'nombre': 'LICENCIATURA EN EDUCACIÓN ESPECIAL',
            'codigo': 'LEE', 
            'numero_semestres': 8,
            'plan': 2023
        },
        {
            'nombre': 'LICENCIATURA EN EDUCACIÓN PRIMARIA',
            'codigo': 'LEP',
            'numero_semestres': 8,
            'plan': 2023
        }
    ]
    
    for data in licenciaturas_data:
        lic, created = Licenciatura.objects.get_or_create(
            nombre=data['nombre'],
            defaults=data
        )
        if created:
            print(f"✓ Creada licenciatura: {lic.nombre}")
            
            # Crear unidades automáticamente
            unidades_base = [
                (1, 'Unidad Principal'),
                (2, 'Unidad Avanzada'),
            ]
            
            for num, nombre in unidades_base:
                unidad = Unidad.objects.create(
                    licenciatura=lic,
                    numero=num,
                    nombre=nombre
                )
                print(f"  - Creada unidad: {unidad.codigo}")
                
                # Crear algunas materias de ejemplo
                materias_ejemplo = [
                    (1, 'Fundamentos de la Educación'),
                    (1, 'Psicología del Desarrollo'),
                    (2, 'Didáctica General'),
                    (2, 'Tecnologías Educativas'),
                ]
                
                for semestre, nombre_materia in materias_ejemplo[:2]:  # Solo 2 materias por unidad
                    materia = Materia.objects.create(
                        licenciatura=lic,
                        unidad=unidad,
                        semestre=semestre,
                        nombre=nombre_materia,
                        creditos=5
                    )
                    print(f"    * Creada materia: {materia.codigo} - {materia.nombre}")

if __name__ == "__main__":
    create_test_data()