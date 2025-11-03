import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import joblib
from datetime import datetime
import os

# === 1. CARGAR DATASET ===
DATA_PATH = "dataset_training_sku_registros.xlsx"  # Dataset en la raíz
data = pd.read_excel(DATA_PATH, engine='openpyxl')

# === 2. LIMPIEZA Y PREPARACIÓN ===
# Convertir fechas si existen
if 'Fecha de pedido' in data.columns and 'Fecha de recepción' in data.columns:
    data['Fecha de pedido'] = pd.to_datetime(data['Fecha de pedido'], dayfirst=True, errors='coerce')
    data['Fecha de recepción'] = pd.to_datetime(data['Fecha de recepción'], dayfirst=True, errors='coerce')
    data['tiempo_entrega_real'] = (data['Fecha de recepción'] - data['Fecha de pedido']).dt.days
else:
    data['tiempo_entrega_real'] = np.nan

# Asegurar que las columnas numéricas sean válidas
cols_num = ['stock', 'ventas', 'duracion', 'numero_pedidos', 'tiempo_entrega', 'cobertura', 'frecuencia']
for col in cols_num:
    data[col] = pd.to_numeric(data[col], errors='coerce')

# Eliminar filas con datos faltantes
data = data.dropna(subset=cols_num)

# === 3. DIVISIÓN EN VARIABLES ===
X = data[['tiempo_entrega', 'stock', 'ventas', 'duracion', 'numero_pedidos']]
y = data[['tiempo_entrega', 'cobertura', 'frecuencia']]  # Tres salidas que tu modelo predice

# === 4. SEPARAR TRAIN/TEST ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === 5. ESCALADO ===
scaler_X = StandardScaler()
scaler_y = StandardScaler()

X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)

y_train_scaled = scaler_y.fit_transform(y_train)
y_test_scaled = scaler_y.transform(y_test)

# === 6. MODELO MLP ===
model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dense(3, activation='linear')  # tres salidas: tiempo_entrega, cobertura, frecuencia
])

model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])

# === 7. ENTRENAMIENTO ===
early_stop = EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True)

history = model.fit(
    X_train_scaled, y_train_scaled,
    validation_data=(X_test_scaled, y_test_scaled),
    epochs=200,
    batch_size=16,
    verbose=1,
    callbacks=[early_stop]
)

# === 8. GUARDADO DE MODELO Y ESCALADORES ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs("model", exist_ok=True)

model_name = f"model_mlp_{timestamp}.h5"
scaler_X_name = f"scaler_X_{timestamp}.pkl"
scaler_y_name = f"scaler_y_{timestamp}.pkl"

model.save(f"model/{model_name}")
joblib.dump(scaler_X, f"model/{scaler_X_name}")
joblib.dump(scaler_y, f"model/{scaler_y_name}")

print("\n✅ Entrenamiento completado correctamente.")
print(f"Modelo guardado: {model_name}")
print(f"Scaler_X guardado: {scaler_X_name}")
print(f"Scaler_Y guardado: {scaler_y_name}")

# === 9. EVALUACIÓN BÁSICA ===
loss, mae = model.evaluate(X_test_scaled, y_test_scaled, verbose=0)
print(f"\n📊 Resultados de validación:")
print(f"Loss (MSE): {loss:.4f}")
print(f"MAE: {mae:.4f}")

# === 10. MÉTRICAS ADICIONALES DE EVALUACIÓN ===
# Predicciones en el conjunto de prueba (ya escalado)
y_pred_scaled = model.predict(X_test_scaled)

# Invertir la escala para comparar en valores reales
y_test_inv = scaler_y.inverse_transform(y_test_scaled)
y_pred_inv = scaler_y.inverse_transform(y_pred_scaled)

# Calcular métricas de error y correlación
mse_total = mean_squared_error(y_test_inv, y_pred_inv)
rmse_total = np.sqrt(mse_total)
mae_total = mean_absolute_error(y_test_inv, y_pred_inv)
mape_total = mean_absolute_percentage_error(y_test_inv, y_pred_inv)
r2_total = r2_score(y_test_inv, y_pred_inv)

print("\n📈 Evaluación adicional del modelo (valores reales):")
print(f"RMSE (Raíz del Error Cuadrático Medio): {rmse_total:.4f}")
print(f"MAPE (Error Porcentual Medio):           {mape_total * 100:.2f}%")
print(f"R²   (Coeficiente de Determinación):     {r2_total:.4f}")

# Evaluación por cada variable de salida
labels = ['Tiempo de entrega', 'Cobertura', 'Frecuencia']
for i in range(3):
    mse_i = mean_squared_error(y_test_inv[:, i], y_pred_inv[:, i])
    rmse_i = np.sqrt(mse_i)
    mae_i = mean_absolute_error(y_test_inv[:, i], y_pred_inv[:, i])
    mape_i = mean_absolute_percentage_error(y_test_inv[:, i], y_pred_inv[:, i])
    r2_i = r2_score(y_test_inv[:, i], y_pred_inv[:, i])

    print(f"\n🔹 {labels[i]}")
    print(f"   RMSE: {rmse_i:.4f}")
    print(f"   MAE:  {mae_i:.4f}")
    print(f"   MAPE: {mape_i * 100:.2f}%")
    print(f"   R²:   {r2_i:.4f}")