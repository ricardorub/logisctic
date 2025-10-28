from flask import request, jsonify, send_file
from model.models import Inventario, Compra
from model.db import db
from datetime import datetime
from sqlalchemy import func
import random
import pandas as pd
import io

def get_all_inventario():
    # Group by product name and aggregate the results
    inventario_agregado = db.session.query(
        Inventario.nombre_producto,
        func.sum(Inventario.cantidad_total).label('cantidad_total'),
        func.avg(Inventario.precio_compra).label('precio_compra'),
        func.max(Inventario.precio_venta).label('precio_venta'),
        func.max(Inventario.sku).label('sku'),
        func.max(Inventario.fecha_recepcion).label('fecha_recepcion')
    ).group_by(Inventario.nombre_producto).all()

    result = []
    for item in inventario_agregado:
        result.append({
            'nombre_producto': item.nombre_producto,
            'sku': item.sku,
            'precio_compra': item.precio_compra,
            'precio_venta': item.precio_venta,
            'cantidad_total': int(item.cantidad_total),
            'fecha_recepcion': item.fecha_recepcion.strftime('%Y-%m-%d') if item.fecha_recepcion else None
        })

    return jsonify(result), 200

def create_inventario():
    data = request.get_json()
    compra_id = data.get('compra_id')
    precio_venta = data.get('precio_venta')

    if not all([compra_id, precio_venta]):
        return jsonify({'error': 'Compra ID y Precio Venta son requeridos'}), 400

    if Inventario.query.filter_by(compra_id=compra_id).first():
        return jsonify({'error': 'Este Compra ID ya ha sido registrado en el inventario.'}), 400

    compra = Compra.query.filter_by(compra_id=compra_id).first()
    if not compra:
        return jsonify({'error': 'Compra ID no encontrado'}), 404

    new_item = Inventario(
        compra_id=compra_id,
        proveedor=compra.proveedor,
        nombre_producto=compra.nombre_producto,
        sku=compra.sku,
        precio_compra=compra.precio_unitario,
        precio_venta=float(precio_venta),
        cantidad_total=compra.cantidad_proveedor, # Storing the individual quantity
        fecha_recepcion=datetime.now().date()
    )

    try:
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': 'Item de inventario creado exitosamente', 'id': new_item.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_productos_inventario():
    productos = Inventario.query.distinct(Inventario.nombre_producto).all()
    return jsonify([{
        'nombre_producto': p.nombre_producto,
        'sku': p.sku,
        'precio_compra': p.precio_compra
    } for p in productos]), 200

def update_inventario(nombre_producto):
    data = request.get_json()
    precio_venta = data.get('precio_venta')

    if precio_venta is None:
        return jsonify({'error': 'Precio Venta es requerido'}), 400

    try:
        items_to_update = Inventario.query.filter_by(nombre_producto=nombre_producto).all()
        if not items_to_update:
            return jsonify({'error': 'No se encontraron items para el producto especificado'}), 404

        for item in items_to_update:
            item.precio_venta = float(precio_venta)

        db.session.commit()
        return jsonify({'message': f'Precio de venta actualizado para {nombre_producto}'}), 200
    except (ValueError, TypeError):
        return jsonify({'error': 'Precio de venta debe ser un número válido'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def delete_inventario(nombre_producto):
    # Deleting is based on product name in the aggregated view
    try:
        items_to_delete = Inventario.query.filter_by(nombre_producto=nombre_producto).all()
        if not items_to_delete:
            return jsonify({'error': 'No se encontraron items para el producto especificado'}), 404

        for item in items_to_delete:
            db.session.delete(item)

        db.session.commit()
        return jsonify({'message': f'Items de inventario para {nombre_producto} eliminados exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def export_inventario():
    inventario_agregado = db.session.query(
        Inventario.nombre_producto,
        func.sum(Inventario.cantidad_total).label('cantidad_total'),
        func.avg(Inventario.precio_compra).label('precio_compra'),
        func.max(Inventario.precio_venta).label('precio_venta'),
        func.max(Inventario.sku).label('sku'),
        func.max(Inventario.fecha_recepcion).label('fecha_recepcion')
    ).group_by(Inventario.nombre_producto).all()

    result = []
    for item in inventario_agregado:
        result.append({
            'Nombre Producto': item.nombre_producto,
            'SKU': item.sku,
            'Precio Compra': item.precio_compra,
            'Precio Venta': item.precio_venta,
            'Cantidad Total': int(item.cantidad_total),
            'Fecha Recepcion': item.fecha_recepcion.strftime('%Y-%m-%d') if item.fecha_recepcion else None
        })

    df = pd.DataFrame(result)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Inventario')
    writer.close()
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        download_name='inventario.xlsx',
        as_attachment=True
    )
