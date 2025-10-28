from flask import request, jsonify
from model.models import Compra, Inventario
from model.db import db
from datetime import datetime
import random

def get_all_compras():
    compras = Compra.query.all()
    return jsonify([{
        'id': compra.id,
        'compra_id': compra.compra_id,
        'proveedor': compra.proveedor,
        'nombre_producto': compra.nombre_producto,
        'cantidad_proveedor': compra.cantidad_proveedor,
        'precio_unitario': compra.precio_unitario,
        'fecha_compra': compra.fecha_compra.strftime('%Y-%m-%d'),
        'fecha_entrega': compra.fecha_entrega.strftime('%Y-%m-%d')
    } for compra in compras]), 200

def create_compra():
    data = request.get_json()
    proveedor = data.get('proveedor')
    nombre_producto = data.get('nombre_producto')
    cantidad_proveedor = data.get('cantidad_proveedor')
    precio_unitario = data.get('precio_unitario')
    fecha_entrega_str = data.get('fecha_entrega')

    if not all([proveedor, nombre_producto, cantidad_proveedor, precio_unitario, fecha_entrega_str]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    try:
        fecha_entrega = datetime.strptime(fecha_entrega_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400

    # Generate a unique 6-digit compra_id
    while True:
        compra_id = random.randint(100000, 999999)
        if not Compra.query.filter_by(compra_id=compra_id).first():
            break

    new_compra = Compra(
        compra_id=compra_id,
        proveedor=proveedor,
        nombre_producto=nombre_producto,
        cantidad_proveedor=int(cantidad_proveedor),
        precio_unitario=float(precio_unitario),
        fecha_compra=datetime.now().date(),
        fecha_entrega=fecha_entrega
    )

    try:
        db.session.add(new_compra)
        db.session.commit()
        return jsonify({'message': 'Compra creada exitosamente', 'id': new_compra.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def update_compra(compra_id):
    data = request.get_json()
    compra = Compra.query.get(compra_id)
    if not compra:
        return jsonify({'error': 'Compra no encontrada'}), 404

    proveedor = data.get('proveedor')
    nombre_producto = data.get('nombre_producto')
    cantidad_proveedor = data.get('cantidad_proveedor')
    precio_unitario = data.get('precio_unitario')
    fecha_entrega_str = data.get('fecha_entrega')

    if not all([proveedor, nombre_producto, cantidad_proveedor, precio_unitario, fecha_entrega_str]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    try:
        fecha_entrega = datetime.strptime(fecha_entrega_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400

    compra.proveedor = proveedor
    compra.nombre_producto = nombre_producto
    compra.cantidad_proveedor = int(cantidad_proveedor)
    compra.precio_unitario = float(precio_unitario)
    compra.fecha_entrega = fecha_entrega

    try:
        db.session.commit()
        return jsonify({'message': 'Compra actualizada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def delete_compra(compra_id):
    compra = Compra.query.get(compra_id)
    if not compra:
        return jsonify({'error': 'Compra no encontrada'}), 404

    try:
        db.session.delete(compra)
        db.session.commit()
        return jsonify({'message': 'Compra eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_productos():
    productos = Compra.query.with_entities(Compra.nombre_producto).distinct().all()
    return jsonify([producto[0] for producto in productos]), 200

def get_cantidad_total(nombre_producto):
    total = db.session.query(db.func.sum(Compra.cantidad_proveedor)).filter_by(nombre_producto=nombre_producto).scalar()
    return jsonify({'total': total or 0}), 200

def get_all_compra_ids():
    compras = Compra.query.with_entities(Compra.compra_id).all()
    return jsonify([compra[0] for compra in compras]), 200

def get_compra_details(compra_id):
    compra = Compra.query.filter_by(compra_id=compra_id).first()
    if not compra:
        return jsonify({'error': 'Compra no encontrada'}), 404
    return jsonify({
        'proveedor': compra.proveedor,
        'nombre_producto': compra.nombre_producto,
        'precio_unitario': compra.precio_unitario
    }), 200

def get_available_compra_ids():
    # Subquery to get all compra_id from Inventario
    inventario_compra_ids = db.session.query(Inventario.compra_id).subquery()
    # Query to get all compra_id from Compra that are not in the subquery
    available_compras = db.session.query(Compra.compra_id)\
        .outerjoin(inventario_compra_ids, Compra.compra_id == inventario_compra_ids.c.compra_id)\
        .filter(inventario_compra_ids.c.compra_id == None).all()
    return jsonify([compra[0] for compra in available_compras]), 200
