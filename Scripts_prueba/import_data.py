# import_data_corregido.py
import os
import sys
import pandas as pd
from docx import Document
import django
from django.conf import settings
from django.db import transaction
import re
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from alumnos.models import Alumno
from evaluaciones.models import Materia, Calificacion
from core.encryption import encryption_manager

def get_file_path(filename):
    """Obtener la ruta completa del archivo"""
    if os.path.exists(filename):
        return filename
    
    possible_paths = [
        filename,
        os.path.join('data', filename),
        os.path.join('archivos', filename),
        os.path.join('documentos', filename),
        os.path.join('import', filename),
        os.path.join('uploads', filename),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    print(f"⚠️  Archivo no encontrado: {filename}")
    return None

def import_from_constancias_word(file_path):
    """Importar datos del archio Word de constancias"""
    alumnos_data = {}
    
    try:
        doc = Document(file_path)
        
        for table in doc.tables:
            for i, row in enumerate(table.rows):
                if i == 0:
                    continue
                    
                try:
                    cells = [cell.text.strip() for cell in row.cells]
                    
                    if len(cells) >= 12:
                        matricula = cells[2] if cells[2] != 'pendiente' else None
                        nombre_completo = cells[3]
                        curp = cells[6]
                        semestre_texto = cells[7].lower()
                        licenciatura_texto = cells[8]
                        turno_texto = cells[10].lower()
                        
                        sexo_texto = cells[4].lower() if cells[4] else cells[5].lower()
                        sexo = 'MUJER' if any(x in sexo_texto for x in ['alumna', 'mujer', 'femenino', 'f', 'a']) else 'HOMBRE'
                        
                        semestre_map = {
                            'primer': 1, 'primero': 1, '1ro': 1, '1er': 1, '1°': 1,
                            'segundo': 2, 'segunda': 2, '2do': 2, '2°': 2,
                            'tercer': 3, 'tercero': 3, '3ro': 3, '3er': 3, '3°': 3,
                            'cuarto': 4, 'cuarta': 4, '4to': 4, '4°': 4,
                            'quinto': 5, 'quinta': 5, '5to': 5, '5°': 5,
                            'sexto': 6, 'sexta': 6, '6to': 6, '6°': 6,
                            'séptimo': 7, 'septimo': 7, 'séptima': 7, 'septima': 7, '7mo': 7, '7°': 7,
                            'octavo': 8, 'octava': 8, '8vo': 8, '8°': 8
                        }
                        
                        semestre_actual = None
                        for key, value in semestre_map.items():
                            if key in semestre_texto:
                                semestre_actual = value
                                break
                        
                        if 'inclusión' in licenciatura_texto.lower() or 'inclusion' in licenciatura_texto.lower():
                            licenciatura = 'INCLUSION_EDUCATIVA'
                        else:
                            licenciatura = 'EDUCACION_ESPECIAL'
                        
                        turno = 'MATUTINO' if 'matutino' in turno_texto else 'VESPERTINO'
                        
                        if curp and (len(curp) != 18 or not curp.isalnum()):
                            print(f"⚠️  CURP inválido: {curp} para {nombre_completo}")
                            curp = None
                        
                        nombre, apellido_paterno, apellido_materno = separar_nombre_completo(nombre_completo)
                        
                        if not curp:
                            print(f"⚠️  Alumno sin CURP: {nombre_completo}")
                            continue
                            
                        identificador = curp
                        
                        if identificador not in alumnos_data:
                            alumnos_data[identificador] = {
                                'matricula': matricula,
                                'curp': curp,
                                'nombre': nombre,
                                'apellido_paterno': apellido_paterno,
                                'apellido_materno': apellido_materno,
                                'sexo': sexo,
                                'semestre_actual': semestre_actual,
                                'licenciatura': licenciatura,
                                'turno': turno,
                                'municipio_estado_nacimiento': 'N/A',
                                'fecha_nacimiento': '2000-01-01',
                                'institucion_procedencia': 'N/A',
                                'calificaciones': [],
                                'fuente': 'constancias_word'
                            }
                            
                except Exception as e:
                    print(f"Error procesando fila {i}: {e}")
                    continue
                    
    except Exception as e:
        print(f"Error procesando archivo Word: {e}")
    
    return alumnos_data

def import_from_excel(file_path):
    """Importar datos de archivos Excel"""
    alumnos_data = {}
    
    try:
        xl = pd.ExcelFile(file_path)
        
        for sheet_name in xl.sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                if 'MATRICULA' in df.columns and 'CURP' in df.columns and 'NOMBRE' in df.columns:
                    process_alumnos_sheet(df, alumnos_data, sheet_name)
                elif 'MATRICULA' in df.columns and 'NOMBRE DEL ALUMNO' in df.columns:
                    process_grades_sheet(df, alumnos_data, sheet_name)
                elif 'MATRICULA' in df.columns and 'CURP' in df.columns and 'NOMBRE' in df.columns:
                    process_alumnos_detailed_sheet(df, alumnos_data, sheet_name)
                    
            except Exception as e:
                print(f"Error procesando hoja {sheet_name}: {e}")
                continue
    
    except Exception as e:
        print(f"Error abriendo archivo Excel: {e}")
    
    return alumnos_data

def separar_nombre_completo(nombre_completo):
    """Separar nombre completo en componentes"""
    if not nombre_completo:
        return "N/A", "N/A", "N/A"
    
    if ',' in nombre_completo:
        partes = nombre_completo.split(',', 1)
        apellidos = partes[0].strip()
        nombre = partes[1].strip() if len(partes) > 1 else "N/A"
        
        apellidos_partes = apellidos.split()
        apellido_paterno = apellidos_partes[0] if apellidos_partes else "N/A"
        apellido_materno = ' '.join(apellidos_partes[1:]) if len(apellidos_partes) > 1 else "N/A"
    else:
        partes = nombre_completo.split()
        if len(partes) >= 3:
            nombre = partes[0]
            apellido_paterno = partes[1]
            apellido_materno = ' '.join(partes[2:])
        elif len(partes) == 2:
            nombre = partes[0]
            apellido_paterno = partes[1]
            apellido_materno = "N/A"
        else:
            nombre = nombre_completo
            apellido_paterno = "N/A"
            apellido_materno = "N/A"
    
    return nombre, apellido_paterno, apellido_materno

def process_alumnos_detailed_sheet(df, alumnos_data, sheet_name):
    """Procesar hoja detallada de alumnos"""
    for _, row in df.iterrows():
        try:
            matricula = None
            curp = None
            nombre_completo = None
            sexo = None
            semestre_actual = None
            licenciatura = None
            turno = None
            municipio_estado_nacimiento = "N/A"
            fecha_nacimiento = '2000-01-01'
            institucion_procedencia = "N/A"
            promedio_prepa = None
            correo_particular = None
            numero_celular = None
            
            for col in df.columns:
                col_upper = col.upper()
                if 'MATRICULA' in col_upper and pd.notna(row.get(col)):
                    matricula = str(row[col]).strip()
                elif 'CURP' in col_upper and pd.notna(row.get(col)):
                    curp = str(row[col]).strip()
                elif 'NOMBRE' in col_upper and pd.notna(row.get(col)):
                    nombre_completo = str(row[col]).strip()
                elif 'SEXO' in col_upper and pd.notna(row.get(col)):
                    sexo_val = str(row[col]).strip().upper()
                    sexo = 'MUJER' if sexo_val in ['MUJER', 'FEMENINO', 'F', 'A'] else 'HOMBRE'
                elif 'SEMESTRE' in col_upper and 'CURSA' in col_upper and pd.notna(row.get(col)):
                    semestre_texto = str(row[col]).strip().lower()
                    semestre_map = {
                        'primer': 1, 'primero': 1, '1ro': 1, '1er': 1, '1°': 1,
                        'segundo': 2, 'segunda': 2, '2do': 2, '2°': 2,
                        'tercer': 3, 'tercero': 3, '3ro': 3, '3er': 3, '3°': 3,
                        'cuarto': 4, 'cuarta': 4, '4to': 4, '4°': 4,
                        'quinto': 5, 'quinta': 5, '5to': 5, '5°': 5,
                        'sexto': 6, 'sexta': 6, '6to': 6, '6°': 6,
                        'séptimo': 7, 'septimo': 7, 'séptima': 7, 'septima': 7, '7mo': 7, '7°': 7,
                        'octavo': 8, 'octava': 8, '8vo': 8, '8°': 8
                    }
                    for key, value in semestre_map.items():
                        if key in semestre_texto:
                            semestre_actual = value
                            break
                elif 'LICENCIATURA' in col_upper and pd.notna(row.get(col)):
                    licenciatura_texto = str(row[col]).strip()
                    if 'INCLUSIÓN' in licenciatura_texto.upper() or 'INCLUSION' in licenciatura_texto.upper():
                        licenciatura = 'INCLUSION_EDUCATIVA'
                    else:
                        licenciatura = 'EDUCACION_ESPECIAL'
                elif 'TURNO' in col_upper and pd.notna(row.get(col)):
                    turno_texto = str(row[col]).strip().lower()
                    turno = 'MATUTINO' if 'matutino' in turno_texto else 'VESPERTINO'
                elif 'MUNICIPIO' in col_upper and 'NACIMIENTO' in col_upper and pd.notna(row.get(col)):
                    municipio_estado_nacimiento = str(row[col]).strip() or "N/A"
                elif 'FECHA' in col_upper and 'NACIMIENTO' in col_upper and pd.notna(row.get(col)):
                    fecha_val = parse_fecha(str(row[col]).strip())
                    if fecha_val:
                        fecha_nacimiento = fecha_val
                elif 'INSTITUCIÓN' in col_upper and 'PROCEDENCIA' in col_upper and pd.notna(row.get(col)):
                    institucion_procedencia = str(row[col]).strip() or "N/A"
                elif 'PROM' in col_upper and 'PREPA' in col_upper and pd.notna(row.get(col)):
                    try:
                        promedio_prepa = float(row[col])
                    except (ValueError, TypeError):
                        promedio_prepa = None
                elif 'CORREO' in col_upper and 'PARTICULAR' in col_upper and pd.notna(row.get(col)):
                    correo_particular = str(row[col]).strip()
                elif 'NÚMERO' in col_upper and 'CELULAR' in col_upper and pd.notna(row.get(col)):
                    numero_celular = str(row[col]).strip()
            
            nombre, apellido_paterno, apellido_materno = separar_nombre_completo(nombre_completo)
            
            if not curp:
                print(f"⚠️  Alumno sin CURP: {nombre_completo}")
                continue
                
            identificador = curp
            
            if identificador not in alumnos_data:
                alumnos_data[identificador] = {
                    'matricula': matricula,
                    'curp': curp,
                    'nombre': nombre,
                    'apellido_paterno': apellido_paterno,
                    'apellido_materno': apellido_materno,
                    'sexo': sexo,
                    'semestre_actual': semestre_actual,
                    'licenciatura': licenciatura,
                    'turno': turno,
                    'municipio_estado_nacimiento': municipio_estado_nacimiento,
                    'fecha_nacimiento': fecha_nacimiento,
                    'institucion_procedencia': institucion_procedencia,
                    'promedio_prepa': promedio_prepa,
                    'correo_particular': correo_particular,
                    'numero_celular': numero_celular,
                    'calificaciones': [],
                    'fuente': 'excel_detallado'
                }
            else:
                alumno_existente = alumnos_data[identificador]
                
                campos_actualizar = [
                    'nombre', 'apellido_paterno', 'apellido_materno', 'sexo', 
                    'semestre_actual', 'licenciatura', 'turno', 'municipio_estado_nacimiento',
                    'fecha_nacimiento', 'institucion_procedencia', 'promedio_prepa',
                    'correo_particular', 'numero_celular', 'matricula'
                ]
                
                for campo in campos_actualizar:
                    if campo in locals() and locals()[campo] not in ["N/A", None, ""]:
                        valor_existente = alumno_existente.get(campo)
                        if valor_existente in ["N/A", None, ""]:
                            alumno_existente[campo] = locals()[campo]
                
                alumno_existente['fuentes'] = alumno_existente.get('fuentes', []) + ['excel_detallado']
                        
        except Exception as e:
            print(f"Error procesando fila: {e}")
            continue

def parse_fecha(fecha_str):
    """Parsear diferentes formatos de fecha"""
    if not fecha_str or fecha_str.lower() in ['', 'nan', 'n/a', '*']:
        return None
    
    try:
        if fecha_str.isdigit():
            fecha_num = int(fecha_str)
            if fecha_num > 59:
                fecha_num -= 1
            base_date = datetime(1899, 12, 30)
            return base_date + timedelta(days=fecha_num)
        
        formatos = [
            '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S'
        ]
        
        for formato in formatos:
            try:
                return datetime.strptime(fecha_str, formato).date()
            except ValueError:
                continue
                
        return None
    except:
        return None

def process_alumnos_sheet(df, alumnos_data, sheet_name):
    """Procesar hoja de alumnos"""
    for _, row in df.iterrows():
        try:
            matricula = None
            curp = None
            nombre_completo = None
            
            for col in df.columns:
                if 'MATRICULA' in col.upper() and pd.notna(row.get(col)):
                    matricula = str(row[col]).strip()
                elif 'CURP' in col.upper() and pd.notna(row.get(col)):
                    curp = str(row[col]).strip()
                elif 'NOMBRE' in col.upper() and pd.notna(row.get(col)):
                    nombre_completo = str(row[col]).strip()
            
            nombre, apellido_paterno, apellido_materno = separar_nombre_completo(nombre_completo)
            
            if not curp:
                print(f"⚠️  Alumno sin CURP: {nombre_completo}")
                continue
                
            identificador = curp
            
            if identificador not in alumnos_data:
                alumnos_data[identificador] = {
                    'matricula': matricula,
                    'curp': curp,
                    'nombre': nombre,
                    'apellido_paterno': apellido_paterno,
                    'apellido_materno': apellido_materno,
                    'calificaciones': [],
                    'turno': 'MATUTINO' if 'MATUT' in sheet_name.upper() else 'VESPERTINO',
                    'semestre_actual': None,
                    'sexo': None,
                    'licenciatura': 'INCLUSION_EDUCATIVA' if 'INCLUSION' in sheet_name.upper() else 'EDUCACION_ESPECIAL',
                    'municipio_estado_nacimiento': 'N/A',
                    'fecha_nacimiento': '2000-01-01',
                    'institucion_procedencia': 'N/A',
                    'fuente': 'excel_general'
                }
            
            for col_name, value in row.items():
                if isinstance(col_name, str) and (col_name.startswith('LIE') or col_name.startswith('LEE')):
                    try:
                        if pd.notna(value):
                            calificacion = float(value)
                            # Extraer semestre de la clave de materia (ej: LIE2201 -> semestre 1)
                            semestre_materia = 1
                            if len(col_name) >= 6 and col_name[5].isdigit():
                                semestre_materia = int(col_name[5])
                            
                            alumnos_data[identificador]['calificaciones'].append({
                                'materia_clave': col_name,
                                'calificacion': calificacion,
                                'periodo': determinar_periodo(sheet_name),
                                'semestre_materia': semestre_materia
                            })
                    except (ValueError, TypeError):
                        continue
                        
        except Exception as e:
            print(f"Error procesando fila: {e}")
            continue

def process_grades_sheet(df, alumnos_data, sheet_name):
    """Procesar hoja de calificaciones"""
    for _, row in df.iterrows():
        try:
            matricula = None
            nombre_completo = None
            
            for col in df.columns:
                if 'MATRICULA' in col.upper() and pd.notna(row.get(col)):
                    matricula = str(row[col]).strip()
                elif 'NOMBRE' in col.upper() and pd.notna(row.get(col)):
                    nombre_completo = str(row[col]).strip()
            
            nombre, apellido_paterno, apellido_materno = separar_nombre_completo(nombre_completo)
            
            if not matricula or matricula == 'nan':
                print(f"⚠️  Alumno sin matrícula: {nombre_completo}")
                continue
                
            identificador = matricula
            
            if identificador not in alumnos_data:
                alumnos_data[identificador] = {
                    'matricula': matricula,
                    'curp': None,
                    'nombre': nombre,
                    'apellido_paterno': apellido_paterno,
                    'apellido_materno': apellido_materno,
                    'calificaciones': [],
                    'municipio_estado_nacimiento': 'N/A',
                    'fecha_nacimiento': '2000-01-01',
                    'institucion_procedencia': 'N/A',
                    'fuente': 'excel_calificaciones'
                }
            
            for col_name, value in row.items():
                if isinstance(col_name, str) and (col_name.startswith('LIE') or col_name.startswith('LEE')):
                    try:
                        if pd.notna(value):
                            calificacion = float(value)
                            # Extraer semestre de la clave de materia
                            semestre_materia = 1
                            if len(col_name) >= 6 and col_name[5].isdigit():
                                semestre_materia = int(col_name[5])
                            
                            alumnos_data[identificador]['calificaciones'].append({
                                'materia_clave': col_name,
                                'calificacion': calificacion,
                                'periodo': determinar_periodo(sheet_name),
                                'semestre_materia': semestre_materia
                            })
                    except (ValueError, TypeError):
                        continue
                        
        except Exception as e:
            print(f"Error procesando fila: {e}")
            continue

def determinar_periodo(sheet_name):
    """Determinar el período basado en el nombre de la hoja"""
    sheet_lower = sheet_name.lower()
    
    if '2023' in sheet_lower or '2023-2024' in sheet_lower:
        return '2023-2024'
    elif '2024' in sheet_lower or '2024-2025' in sheet_lower:
        return '2024-2025'
    elif '2025' in sheet_lower or '2025-2026' in sheet_lower:
        return '2025-2026'
    else:
        return '2024-2025'

def cifrar_datos_alumno(alumno_data):
    """Cifrar los datos sensibles del alumno"""
    campos_cifrar = [
        'nombre', 'apellido_paterno', 'apellido_materno', 'curp', 
        'municipio_estado_nacimiento', 'correo_particular', 'numero_celular',
        'institucion_procedencia'
    ]
    
    for campo in campos_cifrar:
        if campo in alumno_data and alumno_data[campo] not in ["N/A", None]:
            try:
                valor = str(alumno_data[campo])
                if campo == 'matricula' and len(valor) > 15:
                    valor = valor[:15]
                
                alumno_data[campo] = encryption_manager.encrypt(valor)
            except Exception as e:
                print(f"Error cifrando {campo}: {e}")
                alumno_data[campo] = encryption_manager.encrypt("N/A")
        else:
            alumno_data[campo] = encryption_manager.encrypt("N/A")
    
    return alumno_data

def importar_datos():
    """Función principal para importar todos los datos"""
    print("🚀 Iniciando importación de datos...")
    
    archivos = [
        'BASE DE CONSTANCIA ciclo escolar 2025-2026.docx',
        'CAPTURA DE CALIFICACION POR SEMESTRE Y GENERACIONES DE INCLUSION EDUCATIVA PLAN 2022.xlsx',
        'ALUMNOS 2025-2026.xlsx'
    ]
    
    todos_alumnos = {}
    
    for archivo in archivos:
        print(f"\n📂 Procesando archivo: {archivo}")
        
        file_path = get_file_path(archivo)
        if not file_path:
            continue
            
        if archivo.endswith('.docx'):
            alumnos_archivo = import_from_constancias_word(file_path)
        elif archivo.endswith('.xlsx'):
            alumnos_archivo = import_from_excel(file_path)
        else:
            print(f"⚠️  Formato no soportado: {archivo}")
            continue
        
        for identificador, datos in alumnos_archivo.items():
            if identificador in todos_alumnos:
                alumno_existente = todos_alumnos[identificador]
                
                campos_actualizar = [
                    'nombre', 'apellido_paterno', 'apellido_materno', 'sexo', 
                    'semestre_actual', 'licenciatura', 'turno', 'municipio_estado_nacimiento',
                    'fecha_nacimiento', 'institucion_procedencia', 'promedio_prepa',
                    'correo_particular', 'numero_celular', 'matricula'
                ]
                
                for campo in campos_actualizar:
                    if campo in datos and datos[campo] not in ["N/A", None, ""]:
                        valor_existente = alumno_existente.get(campo)
                        if valor_existente in ["N/A", None, ""]:
                            alumno_existente[campo] = datos[campo]
                
                alumno_existente['calificaciones'].extend(datos.get('calificaciones', []))
                alumno_existente['fuentes'] = alumno_existente.get('fuentes', []) + [datos.get('fuente', '')]
            else:
                datos['fuentes'] = [datos.get('fuente', '')]
                todos_alumnos[identificador] = datos
    
    print(f"\n📊 Total de alumnos encontrados: {len(todos_alumnos)}")
    
    with transaction.atomic():
        alumnos_importados = 0
        calificaciones_importadas = 0
        
        for identificador, datos in todos_alumnos.items():
            try:
                if not datos.get('municipio_estado_nacimiento'):
                    datos['municipio_estado_nacimiento'] = "N/A"
                if not datos.get('fecha_nacimiento'):
                    datos['fecha_nacimiento'] = '2000-01-01'
                if not datos.get('institucion_procedencia'):
                    datos['institucion_procedencia'] = "N/A"
                
                datos_cifrados = cifrar_datos_alumno(datos.copy())
                
                matricula = datos_cifrados.get('matricula')
                if matricula and len(matricula) > 20:
                    datos_cifrados['matricula'] = matricula[:20]
                
                if datos_cifrados['curp']:
                    # Usar update_or_create con CURP como identificador principal
                    alumno, created = Alumno.objects.update_or_create(
                        curp=datos_cifrados['curp'],
                        defaults={
                            'matricula': datos_cifrados.get('matricula'),
                            'nombre': datos_cifrados['nombre'],
                            'apellido_paterno': datos_cifrados['apellido_paterno'],
                            'apellido_materno': datos_cifrados['apellido_materno'],
                            'sexo': datos.get('sexo'),
                            'semestre_actual': datos.get('semestre_actual'),
                            'licenciatura': datos.get('licenciatura'),
                            'turno': datos.get('turno'),
                            'municipio_estado_nacimiento': datos_cifrados['municipio_estado_nacimiento'],
                            'fecha_nacimiento': datos.get('fecha_nacimiento'),
                            'institucion_procedencia': datos_cifrados['institucion_procedencia'],
                            'promedio_prepa': datos.get('promedio_prepa'),
                            'correo_particular': datos_cifrados.get('correo_particular'),
                            'numero_celular': datos_cifrados.get('numero_celular'),
                        }
                    )
                    
                    alumnos_importados += 1
                    
                    for calif_data in datos.get('calificaciones', []):
                        try:
                            # Obtener o crear materia con semestre
                            semestre_materia = calif_data.get('semestre_materia', 1)
                            materia, _ = Materia.objects.get_or_create(
                                clave=calif_data['materia_clave'],
                                defaults={
                                    'nombre': calif_data['materia_clave'],
                                    'semestre': semestre_materia,
                                    'licenciatura': datos.get('licenciatura', 'EDUCACION_ESPECIAL'),
                                    'creditos': 0
                                }
                            )
                            
                            # Si la materia ya existe pero no tiene semestre, actualizarlo
                            if not materia.semestre:
                                materia.semestre = semestre_materia
                                materia.save()
                            
                            Calificacion.objects.create(
                                alumno=alumno,
                                materia=materia,
                                calificacion=calif_data['calificacion'],
                                periodo=calif_data['periodo']
                            )
                            
                            calificaciones_importadas += 1
                        except Exception as e:
                            print(f"Error creando calificación: {e}")
                            continue
                else:
                    print(f"⚠️  Alumno sin CURP: {datos.get('nombre', 'Desconocido')}")
                        
            except Exception as e:
                print(f"Error importando alumno {identificador}: {e}")
                continue
    
    print(f"\n✅ Importación completada:")
    print(f"   - Alumnos importados/actualizados: {alumnos_importados}")
    print(f"   - Calificaciones importadas: {calificaciones_importadas}")

if __name__ == "__main__":
    importar_datos()