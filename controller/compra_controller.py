from flask import request, jsonify
from model.models import Compra
from model.db import db
from datetime import datetime

def get_all_compras():
    compras = Compra.query.all()
    return jsonify([{
        'id': compra.id,
        'proveedor': compra.proveedor,
        'nombre_producto': compra.nombre_producto,
        'cantidad_proveedor': compra.cantidad_proveedor,
        'fecha_compra': compra.fecha_compra.strftime('%Y-%m-%d'),
        'fecha_entrega': compra.fecha_entrega.strftime('%Y-%m-%d')
    } for compra in compras]), 200

def create_compra():
    data = request.get_json()
    proveedor = data.get('proveedor')
    nombre_producto = data.get('nombre_producto')
    cantidad_proveedor = data.get('cantidad_proveedor')
    fecha_compra_str = data.get('fecha_compra')
    fecha_entrega_str = data.get('fecha_entrega')

    if not all([proveedor, nombre_producto, cantidad_proveedor, fecha_compra_str, fecha_entrega_str]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    try:
        fecha_compra = datetime.strptime(fecha_compra_str, '%Y-%m-%d').date()
        fecha_entrega = datetime.strptime(fecha_entrega_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400

    new_compra = Compra(
        proveedor=proveedor,
        nombre_producto=nombre_producto,
        cantidad_proveedor=int(cantidad_proveedor),
        fecha_compra=fecha_compra,
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
    fecha_compra_str = data.get('fecha_compra')
    fecha_entrega_str = data.get('fecha_entrega')

    if not all([proveedor, nombre_producto, cantidad_proveedor, fecha_compra_str, fecha_entrega_str]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    try:
        fecha_compra = datetime.strptime(fecha_compra_str, '%Y-%m-%d').date()
        fecha_entrega = datetime.strptime(fecha_entrega_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400

    compra.proveedor = proveedor
    compra.nombre_producto = nombre_producto
    compra.cantidad_proveedor = int(cantidad_proveedor)
    compra.fecha_compra = fecha_compra
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
