from flask import request, jsonify
from model.models import Inventario, Compra
from model.db import db

def get_all_inventario():
    inventario_items = Inventario.query.all()
    return jsonify([{
        'id': item.id,
        'nombre_producto': item.nombre_producto,
        'sku': item.sku,
        'precio_compra': item.precio_compra,
        'precio_venta': item.precio_venta,
        'cantidad_total': item.cantidad_total
    } for item in inventario_items]), 200

def create_inventario():
    data = request.get_json()
    nombre_producto = data.get('nombre_producto')
    sku = data.get('sku')
    precio_compra = data.get('precio_compra')
    precio_venta = data.get('precio_venta')

    if not all([nombre_producto, sku, precio_compra, precio_venta]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    total = db.session.query(db.func.sum(Compra.cantidad_proveedor)).filter_by(nombre_producto=nombre_producto).scalar()
    cantidad_total = total or 0

    new_item = Inventario(
        nombre_producto=nombre_producto,
        sku=sku,
        precio_compra=float(precio_compra),
        precio_venta=float(precio_venta),
        cantidad_total=cantidad_total
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

    nombre_producto = data.get('nombre_producto')
    sku = data.get('sku')
    precio_compra = data.get('precio_compra')
    precio_venta = data.get('precio_venta')

    if not all([nombre_producto, sku, precio_compra, precio_venta]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    total = db.session.query(db.func.sum(Compra.cantidad_proveedor)).filter_by(nombre_producto=nombre_producto).scalar()
    cantidad_total = total or 0

    item.nombre_producto = nombre_producto
    item.sku = sku
    item.precio_compra = float(precio_compra)
    item.precio_venta = float(precio_venta)
    item.cantidad_total = cantidad_total

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
