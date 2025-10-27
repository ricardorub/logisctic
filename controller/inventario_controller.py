from flask import request, jsonify
from model.models import Inventario, Compra
from model.db import db
from datetime import datetime
from sqlalchemy import func

def get_all_inventario():
    inventario_items = Inventario.query.all()
    result = []
    for item in inventario_items:
        result.append({
            'id': item.id,
            'compra_id': item.compra_id,
            'nombre_producto': item.nombre_producto,
            'sku': item.sku,
            'precio_compra': item.precio_compra,
            'precio_venta': item.precio_venta,
            'cantidad_total': item.cantidad_total,
            'fecha_recepcion': item.fecha_recepcion.strftime('%Y-%m-%d') if item.fecha_recepcion else None
        })
    return jsonify(result), 200

def create_inventario():
    data = request.get_json()
    compra_id = data.get('compra_id')
    nombre_producto = data.get('nombre_producto')
    sku = data.get('sku')
    precio_venta = data.get('precio_venta')

    if not all([compra_id, nombre_producto, sku, precio_venta]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    if Inventario.query.filter_by(compra_id=compra_id).first():
        return jsonify({'error': 'Este Compra ID ya ha sido registrado en el inventario.'}), 400

    compra = Compra.query.filter_by(compra_id=compra_id).first()
    if not compra:
        return jsonify({'error': 'Compra ID no encontrado'}), 404

    new_item = Inventario(
        compra_id=compra_id,
        nombre_producto=nombre_producto,
        sku=sku,
        precio_compra=compra.precio_unitario,
        precio_venta=float(precio_venta),
        cantidad_total=compra.cantidad_proveedor,
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
    productos = Inventario.query.all()
    return jsonify([{
        'nombre_producto': p.nombre_producto,
        'sku': p.sku
    } for p in productos]), 200

def update_inventario(item_id):
    data = request.get_json()
    item = Inventario.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item de inventario no encontrado'}), 404

    compra_id = data.get('compra_id')
    nombre_producto = data.get('nombre_producto')
    sku = data.get('sku')
    precio_venta = data.get('precio_venta')

    if not all([compra_id, nombre_producto, sku, precio_venta]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    if item.compra_id != int(compra_id) and Inventario.query.filter_by(compra_id=compra_id).first():
        return jsonify({'error': 'Este Compra ID ya ha sido registrado en el inventario.'}), 400

    compra = Compra.query.filter_by(compra_id=compra_id).first()
    if not compra:
        return jsonify({'error': 'Compra ID no encontrado'}), 404

    item.compra_id = compra_id
    item.nombre_producto = nombre_producto
    item.sku = sku
    item.precio_compra = compra.precio_unitario
    item.precio_venta = float(precio_venta)
    item.cantidad_total = compra.cantidad_proveedor

    try:
        db.session.commit()
        return jsonify({'message': 'Item de inventario actualizado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def delete_inventario(item_id):
    item = Inventario.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item de inventario no encontrado'}), 404

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item de inventario eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
