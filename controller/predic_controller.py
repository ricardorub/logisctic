import os
import pandas as pd
from werkzeug.utils import secure_filename
import json
from datetime import datetime
from flask import request, jsonify, render_template, redirect, url_for, current_app, session

# --- Helper Functions ---

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

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
    tiempo_entrega = row.get('Clasificación Tiempo Entrega', '')
    cobertura = row.get('Clasificación Cobertura', '')
    frecuencia = row.get('Clasificación Frecuencia', '')
    
    score = 0
    if 'Óptimo' in tiempo_entrega: score += 2
    elif 'Bajo' in tiempo_entrega: score += 1
    
    if 'Óptimo' in cobertura: score += 2
    elif 'Largo' in cobertura: score += 1
    
    if 'Media' in frecuencia: score += 2
    elif 'Alta' in frecuencia: score += 1
    
    if score >= 5: return 'optimo'
    elif score >= 3: return 'atencion'
    else: return 'critico'

def get_saved_files_logic():
    """Obtener lista de archivos guardados"""
    files_info = []
    data_folder = current_app.config['DATA_FOLDER']
    
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
    file_path = os.path.join(current_app.config['DATA_FOLDER'], safe_filename)
    
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
    file_path = os.path.join(current_app.config['DATA_FOLDER'], f"{filename}.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def delete_processed_data(filename):
    """Eliminar archivo procesado"""
    file_path = os.path.join(current_app.config['DATA_FOLDER'], f"{filename}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def preprocess_file_logic(file_path, filename):
    """Preprocesar el archivo cargado y calcular métricas"""
    try:
        file_ext = filename.rsplit('.', 1)[1].lower()
        df = pd.read_csv(file_path, encoding='utf-8') if file_ext == 'csv' else pd.read_excel(file_path)
        
        df.columns = df.columns.str.strip().str.upper()
        
        column_mapping = {}
        expected_columns = {
            'fecha_pedido': ['FECHA DE PEDIDO', 'FECHA_PEDIDO', 'FECHA PEDIDO'],
            'fecha_recepcion': ['FECHA DE RECEPCIÓN', 'FECHA_RECEPCION', 'FECHA RECEPCION'],
            'stock': ['STOCK', 'STOCK (UND)', 'INVENTARIO'],
            'duracion': ['DURACIÓN', 'DURACION', 'DURACIÓN (DÍAS)', 'DURACION (DIAS)'],
            'ventas': ['VENTAS', 'VENTAS (UND)', 'DEMANDA'],
            'numero_pedidos': ['NÚMERO DE PEDIDOS', 'NUMERO DE PEDIDOS', 'PEDIDOS']
        }
        
        for standard_name, possible_names in expected_columns.items():
            for col in df.columns:
                if col in possible_names:
                    column_mapping[standard_name] = col
                    break
        
        processed_data = []
        for index, row in df.iterrows():
            row_dict = {col_name: str(value).strip() if not pd.isna(value) else '' for col_name, value in row.items()}
            
            try:
                if 'fecha_pedido' in column_mapping and 'fecha_recepcion' in column_mapping:
                    fecha_pedido = pd.to_datetime(row[column_mapping['fecha_pedido']], dayfirst=True, errors='coerce')
                    fecha_recepcion = pd.to_datetime(row[column_mapping['fecha_recepcion']], dayfirst=True, errors='coerce')
                    if pd.notna(fecha_pedido) and pd.notna(fecha_recepcion):
                        tiempo_entrega_dias = (fecha_recepcion - fecha_pedido).days
                        row_dict['Tiempo de entrega (Días)'] = str(tiempo_entrega_dias)
                        clasif_te, recom_te, riesgo_te = classify_tiempo_entrega(tiempo_entrega_dias)
                        row_dict.update({'Clasificación Tiempo Entrega': clasif_te, 'Recomendación Tiempo Entrega': recom_te, 'Riesgo Tiempo Entrega': riesgo_te})

                if 'stock' in column_mapping and 'duracion' in column_mapping and 'ventas' in column_mapping:
                    stock = float(row[column_mapping['stock']]) if row[column_mapping['stock']] not in ('', None, 'nan') else 0
                    duracion = float(row[column_mapping['duracion']]) if row[column_mapping['duracion']] not in ('', None, 'nan') else 0
                    ventas = float(row[column_mapping['ventas']]) if row[column_mapping['ventas']] not in ('', None, 'nan') else 1
                    if ventas > 0:
                        cobertura_dias = (stock * duracion) / ventas
                        row_dict['Cobertura (Días)'] = f"{cobertura_dias:.2f}"
                        clasif_cobertura, recom_cobertura, riesgo_cobertura = classify_cobertura(cobertura_dias)
                        row_dict.update({'Clasificación Cobertura': clasif_cobertura, 'Recomendación Cobertura': recom_cobertura, 'Riesgo Cobertura': riesgo_cobertura})

                if 'numero_pedidos' in column_mapping and 'duracion' in column_mapping:
                    num_pedidos = float(row[column_mapping['numero_pedidos']]) if row[column_mapping['numero_pedidos']] not in ('', None, 'nan') else 0
                    duracion = float(row[column_mapping['duracion']]) if row[column_mapping['duracion']] not in ('', None, 'nan') else 1
                    if duracion > 0:
                        frecuencia = num_pedidos / duracion
                        row_dict['Frecuencia de pedidos por SKU (Días)'] = f"{frecuencia:.2f}"
                        clasif_frecuencia, recom_frecuencia = classify_frecuencia(frecuencia)
                        row_dict.update({'Clasificación Frecuencia': clasif_frecuencia, 'Recomendación Frecuencia': recom_frecuencia})

                row_dict['ESTADO'] = calcular_estado_final(row_dict)
            except (ValueError, TypeError, KeyError):
                row_dict['ESTADO'] = 'atencion'
            
            processed_data.append(row_dict)
        
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

# --- Controller Functions ---

def file_page_controller():
    if 'user_id' not in session:
        return redirect(url_for('auth.login')) # Or wherever your login page is
    
    saved_files = get_saved_files_logic()
    user = {
        'email': session.get('user_email'),
        'first_name': session.get('user_first_name', ''),
        'last_name': session.get('user_last_name', '')
    }
    return render_template('file.html', user=user, saved_files=saved_files)


def upload_file_controller():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No se seleccionó ningún archivo'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No se seleccionó ningún archivo'})
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            processed_data, columns = preprocess_file_logic(file_path, filename)
            data_folder = current_app.config['DATA_FOLDER']
            if not os.path.exists(data_folder):
                os.makedirs(data_folder)
            saved_filename = save_processed_data(filename, processed_data, columns)
            os.remove(file_path)
            
            return jsonify({
                'success': True, 
                'message': 'Archivo procesado correctamente',
                'filename': saved_filename,
                'redirect_url': url_for('predic.view_file', filename=saved_filename)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al procesar el archivo: {str(e)}'})
    else:
        return jsonify({'success': False, 'message': 'Tipo de archivo no permitido'})

def delete_file_controller(filename):
    try:
        if delete_processed_data(filename):
            return jsonify({'success': True, 'message': 'Archivo eliminado correctamente'})
        else:
            return jsonify({'success': False, 'message': 'Error al eliminar el archivo'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def view_file_controller(filename):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    data = load_processed_data(filename)
    if data:
        user = {
            'email': session.get('user_email'),
            'first_name': session.get('user_first_name', ''),
            'last_name': session.get('user_last_name', '')
        }
        return render_template('retail7.html', 
                             user=user,
                             data=data['processed_data'],
                             columns=data['columns'],
                             filename=data['original_name'],
                             saved_filename=filename)
    else:
        return redirect(url_for('predic.file_page'))

def get_files_controller():
    files_info = get_saved_files_logic()
    return jsonify(files_info)