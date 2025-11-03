import os
import pandas as pd
from werkzeug.utils import secure_filename
import json
from datetime import datetime
from flask import request, jsonify, render_template, redirect, url_for, current_app, session
from tensorflow.keras.models import load_model
import joblib
import numpy as np
import math

# --- Helper Functions ---

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def classify_tiempo_entrega(dias):
    """Clasificar tiempo de entrega con manejo robusto de tipos y valores."""
    try:
        # Normalizar/validar entrada
        if dias is None:
            return 'No calculado', 'No disponible', 'No disponible'

        if isinstance(dias, str):
            s = dias.strip().replace(',', '.')  # soporta "4,5"
            if s == '':
                return 'No calculado', 'No disponible', 'No disponible'
            dias = float(s)

        dias = float(dias)
        if not np.isfinite(dias):  # NaN, inf
            return 'No calculado', 'No disponible', 'No disponible'
        if dias < 0:
            return 'No calculado', 'No disponible', 'No disponible'

        # Umbrales con pequeña tolerancia numérica
        eps = 1e-9
        if dias < 5 - eps:
            return 'Bajo (0-4)', 'Mantener stock de seguridad bajo', 'Riesgo de Sobre inventario'
        elif dias <= 10 + eps:
            return 'Óptimo (5-10)', 'Equilibrio', 'Sin riesgo significativo'
        else:
            return 'Largo (>10)', 'Mantener stock de seguridad alto', 'Riesgo de Quiebre de stock'

    except Exception:
        return 'No calculado', 'No disponible', 'No disponible'

def classify_cobertura(dias):
    """Clasificar cobertura según el algoritmo proporcionado"""
    if dias < 20:
        return 'Bajo (<30 días)', 'Riesgo de Quiebre de stock', 'Reposición Urgente'
    elif 20 <= dias <= 45:
        return 'Óptimo (30-50 días)', 'Equilibrio', 'Costo de almacenamiento y Producto disponible'
    else:  # >45
        return 'Largo (>50 días)', 'Riesgo de sobre stock (sobre inventario)', 'Riesgo de Obsolescencia; Aumento de costos de almacenamiento'

def classify_frecuencia(frecuencia):
    """Clasificar frecuencia de pedidos según el algoritmo proporcionado"""
    if frecuencia <= 1.00:
        return 'Baja Frecuencia (≤1.00 pedidos/día)', 'Reabastezca menos; Descontinuar el producto; Cuidado con el sobre stock; Mínimo de stock de seguridad'
    elif 1.01 < frecuencia <= 2.30:
        return 'Frecuencia Media (1.01-2.30 pedidos/día)', 'Equilibrio; Costo de almacenamiento y Producto disponible'
    else:  # >2.30
        return 'Alta Frecuencia (>2.30 pedidos/día)', 'Reposición rápida; Riesgo Quiebre stock; Mayor stock de seguridad'

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
                except Exception as e:
                    print(f"[DEBUG] Error al leer {filename}: {e}")
                    continue
    
    return sorted(files_info, key=lambda x: x['upload_date'], reverse=True)

def save_processed_data(original_filename, processed_data, columns):
    """Guardar datos procesados en archivo JSON"""
    from datetime import datetime, date
    import math
    import numpy as np
    from werkzeug.utils import secure_filename

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{secure_filename(original_filename)}.json"
    file_path = os.path.join(current_app.config['DATA_FOLDER'], safe_filename)

    # 🔹 Limpieza de valores no serializables (NaN, Inf, Timestamp, etc.)
    for row in processed_data:
        for k, v in row.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                row[k] = 0
            elif isinstance(v, (np.integer, np.floating)):
                row[k] = float(v)
            elif isinstance(v, (datetime, date, np.datetime64)):
                row[k] = str(v)
            elif v is None:
                row[k] = ""

    data_to_save = {
        'original_name': original_filename,
        'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'processed_data': processed_data,
        'columns': columns
    }

    # 🔹 Serializador compatible con Numpy, Timestamp, etc.
    def default_serializer(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, (datetime, date, np.datetime64)):
            return str(obj)
        return str(obj)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2, default=default_serializer)
        print(f"[DEBUG] JSON guardado correctamente en: {file_path}")
    except Exception as e:
        print(f"[ERROR] No se pudo guardar JSON: {e}")

    return safe_filename.replace('.json', '')

# === Cargar modelo y escaladores ===
MODEL_PATH = "model/model_mlp_20251031_114854.h5"
SCALER_X_PATH = "model/scaler_X_20251031_114854.pkl"
SCALER_Y_PATH = "model/scaler_y_20251031_114854.pkl"

model = load_model(MODEL_PATH)
scaler_X = joblib.load(SCALER_X_PATH)
scaler_y = joblib.load(SCALER_Y_PATH)

# --- Procesamiento Principal ---
def preprocess_file_logic(file_path, filename):
    """Preprocesar el archivo cargado y estimar métricas con el modelo MLP + clasificación contextual"""
    try:
        print(f"\n[MLP] Procesando archivo: {filename}")
        file_ext = filename.rsplit('.', 1)[1].lower()

        # === Leer archivo ===
        df = pd.read_csv(file_path, encoding='utf-8') if file_ext == 'csv' else pd.read_excel(file_path, engine='openpyxl')
        df.columns = df.columns.str.strip().str.lower()

        # === Normalizar formato de fechas (sin horas) ===
        if 'fecha de pedido' in df.columns:
            df['fecha de pedido'] = pd.to_datetime(df['fecha de pedido'], errors='coerce').dt.date
        if 'fecha de recepción' in df.columns:
            df['fecha de recepción'] = pd.to_datetime(df['fecha de recepción'], errors='coerce').dt.date

        # === Validación de columnas requeridas ===
        model_input_cols = ['tiempo_entrega', 'stock', 'ventas', 'duracion', 'numero_pedidos']
        for col in model_input_cols:
            if col not in df.columns:
                raise Exception(f"Falta la columna requerida: {col}")

        # === Limpieza básica ===
        df = df.dropna(subset=model_input_cols)
        df = df[(df['ventas'] > 0) & (df['duracion'] > 0)]

        # === Escalar y predecir ===
        X = df[model_input_cols].astype(float).values
        X_scaled = scaler_X.transform(X)
        y_pred_scaled = model.predict(X_scaled)
        y_pred = scaler_y.inverse_transform(y_pred_scaled)

        # === Saneamos NaN/Inf y redondeamos ===
        def sane_round(arr):
            arr = np.asarray(arr, dtype='float64')
            arr[~np.isfinite(arr)] = 0.0
            arr = np.maximum(arr, 0.0)
            return np.round(arr, 2)

        tiempo_pred = sane_round(y_pred[:, 0])
        cobert_pred = sane_round(y_pred[:, 1])
        frec_pred   = sane_round(y_pred[:, 2])

        # === Asignar resultados ===
        df['Tiempo de entrega (Días)'] = tiempo_pred
        df['Cobertura (Días)'] = cobert_pred
        df['Frecuencia de pedidos por SKU (Días)'] = frec_pred

        # === Clasificaciones ===
        clasif_tiempo = df['Tiempo de entrega (Días)'].apply(classify_tiempo_entrega)
        df['Clasificación Tiempo Entrega'] = clasif_tiempo.apply(lambda x: x[0])
        df['Recomendación Tiempo Entrega'] = clasif_tiempo.apply(lambda x: x[1])
        df['Riesgo Tiempo Entrega'] = clasif_tiempo.apply(lambda x: x[2])

        clasif_cobertura = df['Cobertura (Días)'].apply(classify_cobertura)
        df['Clasificación Cobertura'] = clasif_cobertura.apply(lambda x: x[0])
        df['Recomendación Cobertura'] = clasif_cobertura.apply(lambda x: x[1])
        df['Riesgo Cobertura'] = clasif_cobertura.apply(lambda x: x[2])

        clasif_frec = df['Frecuencia de pedidos por SKU (Días)'].apply(classify_frecuencia)
        df['Clasificación Frecuencia'] = clasif_frec.apply(lambda x: x[0])
        df['Recomendación Frecuencia'] = clasif_frec.apply(lambda x: x[1])

        # === Estado general ===
        df['ESTADO'] = df.apply(calcular_estado_final, axis=1)

        # === Convertir tipos ===
        df = df.applymap(lambda x: float(x) if isinstance(x, (np.floating, np.float32, np.float64)) else x)

        # === Salida ===
        processed_data = df.to_dict(orient='records')
        columns = df.columns.tolist()

        print(f"[MLP] Procesadas {len(processed_data)} filas correctamente con el modelo.")
        return processed_data, columns

    except Exception as e:
        print(f"[MLP][ERROR] {e}")
        raise Exception(f"Error al procesar el archivo: {str(e)}")

# --- Controller Functions ---
def file_page_controller():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    saved_files = get_saved_files_logic()
    user = {
        'email': session.get('user_email'),
        'first_name': session.get('user_first_name', ''),
        'last_name': session.get('user_last_name', '')
    }

    print(f"[DEBUG] Archivos detectados en /data: {len(saved_files)}")
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
                'redirect_url': url_for('predic.file_page_controller')
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al procesar el archivo: {str(e)}'})
    else:
        return jsonify({'success': False, 'message': 'Tipo de archivo no permitido'})

def delete_processed_data(filename):
    """Eliminar un archivo procesado del directorio /data"""
    try:
        file_path = os.path.join(current_app.config['DATA_FOLDER'], f"{filename}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[DEBUG] Archivo eliminado: {file_path}")
            return True
        else:
            print(f"[DEBUG] No se encontró el archivo: {file_path}")
            return False
    except Exception as e:
        print(f"[ERROR] No se pudo eliminar {filename}: {e}")
        return False

def delete_file_controller(filename):
    try:
        if delete_processed_data(filename):
            return jsonify({'success': True, 'message': 'Archivo eliminado correctamente'})
        else:
            return jsonify({'success': False, 'message': 'Error al eliminar el archivo'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def load_processed_data(filename):
    """Cargar datos procesados desde archivo JSON"""
    file_path = os.path.join(current_app.config['DATA_FOLDER'], f"{filename}.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] No se pudo cargar {file_path}: {e}")
        return None

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

        import pandas as pd
        df = pd.DataFrame(data['processed_data'])

        # 🔹 Obtiene los promedios reales del pretest
        pretest = {
            "tiempoEntrega": round(df["Tiempo de entrega (Días)"].mean(), 2) if "Tiempo de entrega (Días)" in df.columns else 0,
            "cobertura": round(df["Cobertura (Días)"].mean(), 2) if "Cobertura (Días)" in df.columns else 0,
            "frecuencia": round(df["Frecuencia de pedidos por SKU (Días)"].mean(), 2) if "Frecuencia de pedidos por SKU (Días)" in df.columns else 0
        }

        # 🔹 Renderiza el HTML con valores dinámicos
        return render_template(
            'retail7.html',
            user=user,
            data=data['processed_data'],
            columns=data['columns'],
            filename=data['original_name'],
            saved_filename=filename
        )

    else:
        # 👈 AHORA EL ELSE ESTÁ CORRECTAMENTE ALINEADO CON EL IF
        return redirect(url_for('predic.file_page'))

def get_files_controller():
    files_info = get_saved_files_logic()
    return jsonify(files_info)

# ==========================================
# 🔹 NUEVA FUNCIÓN: Conteo de estados por SKU
# ==========================================
def get_estado_counts_controller(filename):
    """Devuelve la distribución real de estados según el archivo JSON cargado"""
    try:
        file_path = os.path.join(current_app.config['DATA_FOLDER'], f"{filename}.json")
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': f'Archivo {filename} no encontrado'})

        # Cargar el archivo procesado
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        df = pd.DataFrame(data.get('processed_data', []))

        if 'ESTADO' not in df.columns:
            return jsonify({'success': False, 'message': 'La columna ESTADO no existe en el archivo.'})

        # Contar cada categoría
        counts = df['ESTADO'].value_counts().to_dict()

        optimo = int(counts.get('optimo', 0))
        atencion = int(counts.get('atencion', 0))
        critico = int(counts.get('critico', 0))
        total = int(optimo + atencion + critico)

        print(f"[DEBUG] Conteo real de estados para {filename}: "
              f"Óptimo={optimo}, Atención={atencion}, Crítico={critico}, Total={total}")

        return jsonify({
            'success': True,
            'optimo': optimo,
            'atencion': atencion,
            'critico': critico,
            'total': total
        })

    except Exception as e:
        print(f"[ERROR] get_estado_counts_controller: {e}")
        return jsonify({'success': False, 'message': str(e)})
