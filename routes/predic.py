from flask import Blueprint
from controller import contact_controller
import os
import pandas as pd
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import shutil

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Asegurar que existan las carpetas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def classify_tiempo_entrega(dias):
    """Clasificar tiempo de entrega según el algoritmo proporcionado"""
    if 0 <= dias <= 3:
        return 'Bajo (0-3)', 'Se debe mantener stock de seguridad bajo', 'Riesgo de Sobre inventario'
    elif 4 <= dias <= 7:
        return 'Óptimo (4-7)', 'Equilibrio', 'Sin riesgo significativo'
    else:  # >8
        return 'Largo (>8)', 'Se debe mantener stock de seguridad alto', 'Riesgo de Quiebre de stock'

def classify_cobertura(dias):
    """Clasificar cobertura según el algoritmo proporcionado"""
    if dias < 15:
        return 'Bajo (<15 días)', 'Riesgo de Quiebre de stock', 'Reposición Urgente'
    elif 15 <= dias <= 45:
        return 'Óptimo (15-45 días)', 'Equilibrio', 'Costo de almacenamiento y Producto disponible'
    else:  # >45
        return 'Largo (>45 días)', 'Riesgo de sobre stock (sobre inventario)', 'Riesgo de Obsolescencia; Aumento de costos de almacenamiento'

def classify_frecuencia(frecuencia):
    """Clasificar frecuencia de pedidos según el algoritmo proporcionado"""
    if frecuencia <= 0.25:
        return 'Baja Frecuencia (≤0.25 pedidos/día)', 'Reabastezca menos; Descontinuar el producto; Cuidado con el sobre stock; Mínimo de stock de seguridad'
    elif 0.25 < frecuencia <= 0.50:
        return 'Frecuencia Media (0.25-0.50 pedidos/día)', 'Equilibrio; Costo de almacenamiento y Producto disponible'
    else:  # >0.50
        return 'Alta Frecuencia (>0.50 pedidos/día)', 'Reposición rápida; Riesgo Quiebre stock; Mayor stock de seguridad'

def calcular_estado_final(row):
    """Calcular estado final basado en las tres métricas principales"""
    # Ponderar las clasificaciones para determinar el estado general
    tiempo_entrega = row.get('Clasificación Tiempo Entrega', '')
    cobertura = row.get('Clasificación Cobertura', '')
    frecuencia = row.get('Clasificación Frecuencia', '')
    
    # Sistema de puntuación
    score = 0
    
    # Tiempo de entrega
    if 'Óptimo' in tiempo_entrega:
        score += 2
    elif 'Bajo' in tiempo_entrega:
        score += 1
    
    # Cobertura
    if 'Óptimo' in cobertura:
        score += 2
    elif 'Largo' in cobertura:
        score += 1
    
    # Frecuencia
    if 'Media' in frecuencia:
        score += 2
    elif 'Alta' in frecuencia:
        score += 1
    
    # Determinar estado final
    if score >= 5:
        return 'optimo'
    elif score >= 3:
        return 'atencion'
    else:
        return 'critico'

def get_saved_files():
    """Obtener lista de archivos guardados"""
    files_info = []
    data_folder = app.config['DATA_FOLDER']
    
    if os.path.exists(data_folder):
        for filename in os.listdir(data_folder):
            if filename.endswith('.json'):
                file_path = os.path.join(data_folder, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        files_info.append({
                            'filename': filename.replace('.json', ''),
                            'original_name': data.get('original_name', ''),
                            'upload_date': data.get('upload_date', ''),
                            'record_count': len(data.get('processed_data', [])),
                            'columns': data.get('columns', [])
                        })
                except:
                    continue
    
    return sorted(files_info, key=lambda x: x['upload_date'], reverse=True)

def save_processed_data(original_filename, processed_data, columns):
    """Guardar datos procesados en archivo JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{secure_filename(original_filename)}.json"
    file_path = os.path.join(app.config['DATA_FOLDER'], safe_filename)
    
    data_to_save = {
        'original_name': original_filename,
        'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'processed_data': processed_data,
        'columns': columns
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    
    return safe_filename.replace('.json', '')

def load_processed_data(filename):
    """Cargar datos procesados desde archivo JSON"""
    file_path = os.path.join(app.config['DATA_FOLDER'], f"{filename}.json")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def delete_processed_data(filename):
    """Eliminar archivo procesado"""
    file_path = os.path.join(app.config['DATA_FOLDER'], f"{filename}.json")
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def preprocess_file(file_path, filename):
    """Preprocesar el archivo cargado y calcular métricas según el algoritmo proporcionado"""
    try:
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        if file_ext == 'csv':
            df = pd.read_csv(file_path, encoding='utf-8')
        else:
            df = pd.read_excel(file_path)
        
        # Limpiar nombres de columnas → mayúsculas y sin espacios extra
        df.columns = df.columns.str.strip().str.upper()
        
        # Mapear nombres de columnas esperados
        column_mapping = {}
        expected_columns = {
            'fecha_pedido': ['FECHA DE PEDIDO', 'FECHA_PEDIDO', 'FECHA PEDIDO'],
            'fecha_recepcion': ['FECHA DE RECEPCIÓN', 'FECHA_RECEPCION', 'FECHA RECEPCION'],
            'stock': ['STOCK', 'STOCK (UND)', 'INVENTARIO'],
            'duracion': ['DURACIÓN', 'DURACION', 'DURACIÓN (DÍAS)', 'DURACION (DIAS)'],
            'ventas': ['VENTAS', 'VENTAS (UND)', 'DEMANDA'],
            'numero_pedidos': ['NÚMERO DE PEDIDOS', 'NUMERO DE PEDIDOS', 'PEDIDOS']
        }
        
        # Buscar columnas equivalentes
        for standard_name, possible_names in expected_columns.items():
            for col in df.columns:
                if col in possible_names:
                    column_mapping[standard_name] = col
                    break
        
        processed_data = []
        
        for index, row in df.iterrows():
            row_dict = {}
            
            # Copiar datos originales
            for col_name, value in row.items():
                if pd.isna(value) or value == '':
                    row_dict[col_name] = ''
                else:
                    row_dict[col_name] = str(value).strip()
            
            # Calcular métricas según el algoritmo
            try:
                # Tiempo de entrega
                if 'fecha_pedido' in column_mapping and 'fecha_recepcion' in column_mapping:
                    fecha_pedido = pd.to_datetime(row[column_mapping['fecha_pedido']], dayfirst=True, errors='coerce')
                    fecha_recepcion = pd.to_datetime(row[column_mapping['fecha_recepcion']], dayfirst=True, errors='coerce')
                    
                    if pd.notna(fecha_pedido) and pd.notna(fecha_recepcion):
                        tiempo_entrega_dias = (fecha_recepcion - fecha_pedido).days
                        row_dict['Tiempo de entrega (Días)'] = str(tiempo_entrega_dias)
                        
                        clasif_te, recom_te, riesgo_te = classify_tiempo_entrega(tiempo_entrega_dias)
                        row_dict['Clasificación Tiempo Entrega'] = clasif_te
                        row_dict['Recomendación Tiempo Entrega'] = recom_te
                        row_dict['Riesgo Tiempo Entrega'] = riesgo_te
                
                # Cobertura
                if 'stock' in column_mapping and 'duracion' in column_mapping and 'ventas' in column_mapping:
                    stock = float(row[column_mapping['stock']]) if row[column_mapping['stock']] not in ('', None, 'nan') else 0
                    duracion = float(row[column_mapping['duracion']]) if row[column_mapping['duracion']] not in ('', None, 'nan') else 0
                    ventas = float(row[column_mapping['ventas']]) if row[column_mapping['ventas']] not in ('', None, 'nan') else 1
                    
                    if ventas > 0:
                        cobertura_dias = (stock * duracion) / ventas
                        row_dict['Cobertura (Días)'] = f"{cobertura_dias:.2f}"
                        
                        clasif_cobertura, recom_cobertura, riesgo_cobertura = classify_cobertura(cobertura_dias)
                        row_dict['Clasificación Cobertura'] = clasif_cobertura
                        row_dict['Recomendación Cobertura'] = recom_cobertura
                        row_dict['Riesgo Cobertura'] = riesgo_cobertura
                
                # Frecuencia de pedidos
                if 'numero_pedidos' in column_mapping and 'duracion' in column_mapping:
                    num_pedidos = float(row[column_mapping['numero_pedidos']]) if row[column_mapping['numero_pedidos']] not in ('', None, 'nan') else 0
                    duracion = float(row[column_mapping['duracion']]) if row[column_mapping['duracion']] not in ('', None, 'nan') else 1
                    
                    if duracion > 0:
                        frecuencia = num_pedidos / duracion
                        row_dict['Frecuencia de pedidos por SKU (Días)'] = f"{frecuencia:.2f}"
                        
                        clasif_frecuencia, recom_frecuencia = classify_frecuencia(frecuencia)
                        row_dict['Clasificación Frecuencia'] = clasif_frecuencia
                        row_dict['Recomendación Frecuencia'] = recom_frecuencia
                
                # Calcular estado final
                estado_final = calcular_estado_final(row_dict)
                row_dict['ESTADO'] = estado_final
                
            except (ValueError, TypeError, KeyError) as e:
                # Si hay error en cálculos, asignar estado por defecto
                row_dict['ESTADO'] = 'atencion'
            
            processed_data.append(row_dict)
        
        # Columnas originales + nuevas métricas + ESTADO
        original_columns = list(df.columns)
        new_columns = [
            'Tiempo de entrega (Días)', 'Clasificación Tiempo Entrega', 'Recomendación Tiempo Entrega', 'Riesgo Tiempo Entrega',
            'Cobertura (Días)', 'Clasificación Cobertura', 'Recomendación Cobertura', 'Riesgo Cobertura',
            'Frecuencia de pedidos por SKU (Días)', 'Clasificación Frecuencia', 'Recomendación Frecuencia',
            'ESTADO'
        ]
        columns = original_columns + [col for col in new_columns if col not in original_columns]
        
        return processed_data, columns
        
    except Exception as e:
        raise Exception(f"Error al procesar el archivo: {str(e)}")

@app.route('/')
def index():
    return redirect(url_for('archivo'))

@app.route('/archivo.html')
def archivo():
    files_info = get_saved_files()
    return render_template('archivo.html', saved_files=files_info)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No se seleccionó ningún archivo'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No se seleccionó ningún archivo'})
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            processed_data, columns = preprocess_file(file_path, filename)
            saved_filename = save_processed_data(filename, processed_data, columns)
            os.remove(file_path)
            
            return jsonify({
                'success': True, 
                'message': 'Archivo procesado correctamente',
                'filename': saved_filename,
                'record_count': len(processed_data)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al procesar el archivo: {str(e)}'})
    else:
        return jsonify({'success': False, 'message': 'Tipo de archivo no permitido'})

@app.route('/delete_file/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        if delete_processed_data(filename):
            return jsonify({'success': True, 'message': 'Archivo eliminado correctamente'})
        else:
            return jsonify({'success': False, 'message': 'Error al eliminar el archivo'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/view_file/<filename>')
def view_file(filename):
    data = load_processed_data(filename)
    if data:
        return render_template('retail7.html', 
                             data=data['processed_data'],
                             columns=data['columns'],
                             filename=data['original_name'],
                             saved_filename=filename)
    else:
        flash('Error al cargar el archivo', 'error')
        return redirect(url_for('archivo'))

@app.route('/get_files')
def get_files():
    files_info = get_saved_files()
    return jsonify(files_info)

@app.route('/back_to_upload')
def back_to_upload():
    return redirect(url_for('archivo'))

@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools_config():
    return '', 204

